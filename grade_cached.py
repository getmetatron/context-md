#!/usr/bin/env python3
"""Bounded, offline grading against an already-cached SWE-bench image.

Uses official test generation and parsing. Empty patches run unchanged code
instead of failing `git apply`. All evaluation inputs/logs are grader-private.
This component does not grant solvers access to the dataset or Docker socket.
"""

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import time
import uuid

from process_guard import atomic_json


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def task_row(dataset, instance_id):
    import pandas as pd
    rows = pd.read_parquet(dataset, filters=[("instance_id", "==", instance_id)])
    if len(rows) != 1:
        raise ValueError("expected exactly one benchmark task")
    return rows.iloc[0].to_dict()


def grading_spec(row, arch, runtime=None):
    from swebench.harness.test_spec.test_spec import make_test_spec
    if runtime and runtime.get("kind") == "native_repo":
        from native_runtime import amended_row
        row = amended_row(row, runtime)
    if runtime and runtime.get("kind") in {"python_pytest", "python_repo"}:
        from python_runtime import amended_row
        row = amended_row(row, runtime)
    if runtime and runtime.get("kind") == "django_repo":
        from django_runtime import amended_row
        row = amended_row(row, runtime)
    from registration_metadata import normalized_lists
    return make_test_spec(normalized_lists(row), namespace="swebench", arch=arch)


def grading_script(spec, row, runtime=None):
    if not runtime:
        return spec.eval_script
    if runtime.get("kind") in {"python_pytest", "python_repo"}:
        from python_runtime import amend_script
    elif runtime.get("kind") == "native_repo":
        from native_runtime import amend_script
    elif row["repo"] == "django/django":
        from django_runtime import amend_script
    else:
        raise ValueError("unsupported explicit runtime amendment")
    return amend_script(spec.eval_script, runtime)


def coverage(report, spec, raw_statuses, executed_errors=()):
    """Require every registered test to be observed, including baseline failures."""
    result = {}
    statuses = report.get("tests_status", {})
    for name, expected in (("FAIL_TO_PASS", spec.FAIL_TO_PASS), ("PASS_TO_PASS", spec.PASS_TO_PASS)):
        # The official summary counts missing tests as failures. That alone
        # cannot establish that the grader actually executed those tests.
        if any(raw_statuses.get(test) not in {"PASSED", "FAILED"} and
               not (raw_statuses.get(test) == "ERROR" and test in executed_errors) for test in expected):
            raise RuntimeError("registered tests absent/skipped/errored in raw output: " + name)
        observed = statuses.get(name, {})
        passed, failed = set(observed.get("success", [])), set(observed.get("failure", []))
        if passed & failed or passed | failed != set(expected):
            raise RuntimeError("incomplete or inconsistent grading coverage: " + name)
        if any((test in passed) != (raw_statuses[test] == "PASSED") for test in expected):
            raise RuntimeError("raw output and grading summary disagree: " + name)
        result[name] = {"expected": len(expected), "passed": len(passed), "failed": len(failed)}
    if not spec.FAIL_TO_PASS:
        raise ValueError("smoke grading requires a nonempty FAIL_TO_PASS set")
    return result


def django_test_body_errors(log, expected):
    """Attest named test-body exceptions; collection/fixture errors stay invalid."""
    result = []
    aliases = django_test_aliases(expected)
    for test in expected:
        if not re.search(r"(?m)^"+re.escape(test)+r" \.\.\. ERROR$", log):
            continue
        original = next(key for key, value in aliases.items() if value == test)
        match = re.search(r"(?m)^ERROR: "+re.escape(original)+r"$", log)
        if not match:
            continue
        block = re.split(r"(?m)^={10,}$", log[match.end():], maxsplit=1)[0]
        method = original.split(" ", 1)[0]
        if re.search(r'File "/testbed/tests/[^"\n]+", line \d+, in '+re.escape(method)+r"\n", block):
            result.append(test)
    return result


def unregistered_failures(log, expected, repo, raw_statuses, pytest_summary=False):
    """Supplement registered coverage with unexpected failures in the same run."""
    if repo == "django/django":
        known = set(expected)|set(django_test_aliases(expected))
        return sorted({match[2] for match in re.finditer(r"(?m)^(FAIL|ERROR): (.+)$", log) if match[2] not in known})
    if pytest_summary:
        return sorted({line[len("FAILED "):] for line in log.splitlines() if line.startswith("FAILED ") and
            not any(line == "FAILED "+test or line.startswith("FAILED "+test+" - ") for test in expected)})
    return sorted(test for test,status in raw_statuses.items() if status in {"FAILED","ERROR"} and test not in expected)


def django_test_aliases(expected):
    """Map exact full unittest IDs to exact registered pytest-style node IDs."""
    result = {}
    for test in expected:
        canonical = test
        if "::" in test:
            parts = test.split("::")
            if (len(parts) != 3 or not re.fullmatch(r"tests/(?:[A-Za-z_]\w*/)*[A-Za-z_]\w*\.py", parts[0]) or
                    not all(re.fullmatch(r"[A-Za-z_]\w*", value) for value in parts[1:])):
                raise ValueError("unsupported Django benchmark node ID")
            module = parts[0][len("tests/"):-3].replace("/", ".")
            canonical = parts[2]+" ("+module+"."+parts[1]+")"
        if canonical in result and result[canonical] != test:
            raise ValueError("ambiguous Django test identity aliases")
        result[canonical] = test
    return result


def normalize_django_descriptions(log, expected):
    """Emit canonical IDs for unittest's two-line ID/docstring status layout.

    The official Django parser otherwise attributes the result to the docstring.
    Keep every raw line and insert an equivalent identity/status line only for
    an exact registered test ID. Skips/errors retain their original status.
    """
    aliases = django_test_aliases(expected)
    expected = set(aliases)
    pending = None
    lines = []
    for line in log.splitlines(keepends=True):
        stripped = line.strip()
        if re.fullmatch(r"test\S* \([^()]+\)", stripped):
            pending = stripped if stripped in expected else None
        elif re.match(r"^test\S* \([^()]+\) \.\.\. ", stripped):
            pending = None
        lines.append(line)
        status = re.search(r" \.\.\. (ok|OK|FAIL|ERROR|skipped(?: .*)?)$", stripped)
        direct = stripped.rsplit(" ... ", 1)[0] if status else None
        if direct in aliases and aliases[direct] != direct:
            lines.append(aliases[direct]+" ... "+status[1]+"\n")
        if pending and status:
            lines.append(("" if line.endswith("\n") else "\n")+pending+" ... "+status[1]+"\n")
            if aliases[pending] != pending:
                lines.append(aliases[pending]+" ... "+status[1]+"\n")
            pending = None
    return "".join(lines)


def grade(row, patch, output, image, image_id, arch, timeout=300,
          setup_commit=None, setup_overlay_sha256=None, allow_derived_image=False, runtime=None):
    import docker
    from swebench.harness.docker_utils import copy_to_container
    import swebench.harness.grading as grading
    import swebench.harness.test_spec.test_spec as specification

    if not isinstance(timeout, int) or not 1 <= timeout <= 3600:
        raise ValueError("timeout must be 1..3600 seconds")
    output = Path(output).resolve()
    # Never reuse a completed/partial run directory or accept cached results.
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    os.chmod(output, 0o700)
    if shutil.disk_usage(output).free < 512 * 1024**2:
        raise RuntimeError("grading requires at least 512 MiB of free host storage")
    spec = grading_spec(row, arch, runtime)
    eval_script = grading_script(spec, row, runtime)
    if runtime and runtime.get("status_parser") not in {None, "exact_pytest_summary", "jq_cases"}:
        raise ValueError("unsupported explicit grading status parser")
    author_image = runtime.get("author_image") if runtime and runtime.get("kind") in {"python_pytest", "python_repo", "native_repo", "django_repo"} else None
    if author_image and not re.fullmatch(r"jiayuanz3/swecontextbench@sha256:[0-9a-f]{64}", author_image):
        raise ValueError("benchmark author image must use an immutable manifest")
    if image != spec.instance_image_key and image != author_image and not (allow_derived_image and image.startswith("context-inheritance/bridge-")):
        raise ValueError("image name differs from the official task specification")
    client = docker.from_env(timeout=20)
    container, database = None, None
    started = time.monotonic()
    run_id = "ci-grade-" + uuid.uuid4().hex
    receipt = {"schema": 1, "run_id": run_id, "instance_id": row["instance_id"],
               "base_commit": row["base_commit"], "image": image, "image_id": image_id,
               "architecture": arch, "patch_sha256": sha256(patch.encode()),
               "image_provenance": "official_cached" if image == spec.instance_image_key else "benchmark_author_cached" if image == author_image else "local_derived",
               "dataset_version": row["version"], "recipe_version": spec.version,
               "effective_registration_sha256": sha256(json.dumps({"FAIL_TO_PASS": spec.FAIL_TO_PASS, "PASS_TO_PASS": spec.PASS_TO_PASS}, sort_keys=True).encode()),
               "eval_script_sha256": sha256(eval_script.encode()),
               "original_eval_script_sha256": sha256(spec.eval_script.encode()),
               "runtime_amendments": runtime,
               "grader_sha256": sha256(Path(__file__).read_bytes()),
               "swebench_version": importlib.metadata.version("swebench"),
               "official_module_sha256": {name: sha256(Path(inspect.getfile(module)).read_bytes())
                                           for name, module in (("grading", grading), ("test_spec", specification))},
               "timeout_seconds": timeout, "network": "none", "host_mounts": [],
               "container_lifetime_seconds": timeout + 90,
               "setup_commit": setup_commit or row["base_commit"],
               "setup_overlay_sha256": setup_overlay_sha256,
               "completed": False, "resolved": None}
    atomic_json(output / "receipt.json", receipt)
    try:
        cached = client.images.get(image)  # No pulling or building.
        if cached.id != image_id or cached.attrs["Architecture"] != {"arm64": "arm64", "x86_64": "amd64"}[arch]:
            raise ValueError("cached image identity or architecture differs from the pin")
        (output / "eval.sh").write_text(eval_script)
        (output / "patch.diff").write_text(patch)
        volumes = {}
        if runtime and runtime.get("backend") == "postgresql":
            from django_runtime import PostgresFixture
            database = PostgresFixture(client, runtime["postgres_image_id"], output, timeout+150)
            volumes = database.start()
            receipt["grader_database_transport"] = "offline Unix socket over read-only Docker-managed volume"
        # PID 1 independently expires the whole container, including test children.
        # No host filesystem, credentials, or Docker socket is mounted.
        container = client.containers.create(
            image=cached.id, name=run_id, user="root", detach=True,
            command=["timeout", "--signal=TERM", "--kill-after=5s", str(timeout + 90), "tail", "-f", "/dev/null"],
            network_mode="none", auto_remove=True, mem_limit="4g", nano_cpus=2_000_000_000,
            pids_limit=512, cap_drop=["ALL"], security_opt=["no-new-privileges:true"],
            labels={"context-inheritance.role": "grader", "context-inheritance.run": run_id,
                    "context-inheritance.expires_at": str(time.time() + timeout + 95)},
            platform=spec.platform,
            volumes=volumes,
        )
        container.start()
        check = container.exec_run(["git", "-c", "safe.directory=/testbed", "rev-parse", "HEAD"], workdir="/testbed")
        if check.exit_code or check.output.decode().strip() != receipt["setup_commit"]:
            raise RuntimeError("cached image is not at the pinned base/setup commit")
        overlay = container.exec_run(["git", "-c", "safe.directory=/testbed", "diff", "--binary", row["base_commit"], "HEAD"], workdir="/testbed")
        if overlay.exit_code or (overlay.output and sha256(overlay.output) != setup_overlay_sha256):
            raise RuntimeError("image setup changes require an explicitly reviewed overlay hash")
        if not overlay.output and setup_overlay_sha256 is not None:
            raise RuntimeError("declared setup overlay is absent")
        (output / "setup-overlay.diff").write_bytes(overlay.output)
        dirty = container.exec_run(["git", "-c", "safe.directory=/testbed", "status", "--porcelain"], workdir="/testbed")
        if dirty.exit_code:
            raise RuntimeError("cached grading image worktree inspection failed")
        if dirty.output.strip() and runtime and runtime.get("initial_untracked_cleanup"):
            from go_runtime import clean_untracked_binary
            cleanup = clean_untracked_binary(container, row, runtime["initial_untracked_cleanup"])
            atomic_json(output/"initial-untracked-cleanup.json", cleanup)
            receipt["initial_untracked_cleanup"] = cleanup
            dirty = container.exec_run(["git", "-c", "safe.directory=/testbed", "status", "--porcelain"], workdir="/testbed")
        if dirty.exit_code or dirty.output.strip():
            raise RuntimeError("cached grading image has a dirty initial worktree")
        if runtime and runtime.get("version_evidence"):
            evidence = runtime["version_evidence"]
            version_file = container.exec_run(["git", "show", row["base_commit"]+":"+evidence["file"]], workdir="/testbed")
            if version_file.exit_code or sha256(version_file.output) != evidence["sha256"]:
                raise RuntimeError("version evidence differs from the pinned benchmark source")
            if row["repo"] == "django/django":
                from django_runtime import version_from_source
                declared = list(version_from_source(version_file.output.decode()))
            else:
                match = re.search(r'(?m)^__version__ = [\"\x27]([^\"\x27]+)[\"\x27]$', version_file.output.decode())
                declared = match[1] if match else None
            if declared != evidence["value"]:
                raise RuntimeError("source version declaration differs from the amendment")
        copy_to_container(container, output / "eval.sh", PurePosixPath("/eval.sh"))
        if database:
            from django_runtime import SETTINGS
            (output/"ci_grade_postgres.py").write_text(SETTINGS)
            copy_to_container(container, output/"ci_grade_postgres.py", PurePosixPath("/testbed/tests/ci_grade_postgres.py"))
        if patch.strip():
            copy_to_container(container, output / "patch.diff", PurePosixPath("/candidate.diff"))
            applied = container.exec_run(["git", "-c", "safe.directory=/testbed", "apply", "--check", "/candidate.diff"], workdir="/testbed")
            (output / "apply-check.log").write_bytes(applied.output)
            if applied.exit_code:
                raise RuntimeError("candidate patch does not apply cleanly")
            applied = container.exec_run(["git", "-c", "safe.directory=/testbed", "apply", "/candidate.diff"], workdir="/testbed")
            if applied.exit_code:
                raise RuntimeError("candidate patch application failed")
        receipt["candidate_applied"] = bool(patch.strip())
        atomic_json(output / "receipt.json", receipt)
        with (output / "test-output.log").open("wb") as log:
            result = subprocess.run(
                ["docker", "exec", container.id, "timeout", "--signal=TERM", "--kill-after=5s", str(timeout), "/bin/bash", "/eval.sh"],
                stdout=log, stderr=subprocess.STDOUT, timeout=timeout + 30,
            )
            log.flush()
            os.fsync(log.fileno())
        receipt["eval_exit_code"] = result.returncode
        if result.returncode in {124, 137, 143}:
            raise RuntimeError("grading command timed out or was killed")
        prediction = {"instance_id": row["instance_id"], "model_name_or_path": "technical-grader-check", "model_patch": patch}
        grading_log = output / "test-output.log"
        if row["repo"] == "django/django":
            normalized = normalize_django_descriptions(grading_log.read_text(), spec.FAIL_TO_PASS+spec.PASS_TO_PASS)
            if runtime and runtime.get("traceback_status_completion"):
                from django_runtime import complete_traceback_statuses
                normalized = complete_traceback_statuses(normalized, spec.FAIL_TO_PASS+spec.PASS_TO_PASS)
            if runtime and runtime.get("interrupted_pass_completion"):
                from django_runtime import complete_interrupted_passes
                normalized = complete_interrupted_passes(normalized, spec.FAIL_TO_PASS+spec.PASS_TO_PASS)
            grading_log = output / "parser-input.log"
            grading_log.write_text(normalized)
            receipt["log_normalization"] = "canonical IDs for registered multiline unittest descriptions; original output retained"
            receipt["parser_input_sha256"] = sha256(grading_log.read_bytes())
        report = grading.get_eval_report(spec, prediction, str(grading_log), include_tests_status=True)
        atomic_json(output / "official-report.json", report)
        task_report = report[row["instance_id"]]
        raw_statuses, markers_found = grading.get_logs_eval(spec, str(grading_log))
        if not markers_found:
            raise RuntimeError("official test-output markers were not found")
        if runtime and runtime.get("status_parser") in {"exact_pytest_summary", "jq_cases"}:
            from swebench.harness.constants import EvalType, ResolvedStatus
            if runtime["status_parser"] == "jq_cases":
                if row["repo"] != "jqlang/jq" or runtime.get("kind") != "native_repo":
                    raise ValueError("unsupported jq parser amendment")
                from native_runtime import jq_case_statuses
                raw_statuses = jq_case_statuses(grading_log.read_text())
                parser_amendment = "Exact jq case identities; complete terminal counts, contiguous declarations and no malformed/skipped cases required."
            else:
                if row["repo"] not in {"pylint-dev/pylint", "sympy/sympy"} or runtime.get("kind") not in {"python_pytest", "python_repo"}:
                    raise ValueError("unsupported registered-test parser amendment")
                from python_runtime import registered_statuses, repository_path_aliases
                expected = spec.FAIL_TO_PASS+spec.PASS_TO_PASS
                rule = runtime.get("test_id_alias_rule")
                if rule is None:
                    aliases = {}
                elif rule == "pylint_stdin_repository_root" and row["repo"] == "pylint-dev/pylint":
                    aliases = repository_path_aliases(expected)
                else:
                    raise ValueError("unsupported pytest identity alias rule")
                raw_statuses = registered_statuses(grading_log.read_text(), expected, aliases)
                parser_amendment = "Exact complete pytest summary IDs; declared path-dependent alias."
            tests = grading.get_eval_tests_report(raw_statuses,
                {"instance_id": spec.instance_id, "FAIL_TO_PASS": spec.FAIL_TO_PASS, "PASS_TO_PASS": spec.PASS_TO_PASS},
                eval_type=EvalType.PASS_AND_FAIL)
            task_report = {**task_report, "tests_status": tests,
                "resolved": grading.get_resolution_status(tests) == ResolvedStatus.FULL.value}
            atomic_json(output/"runtime-report.json", {spec.instance_id: task_report})
            atomic_json(output/"registered-statuses.json", raw_statuses)
            receipt["status_parser_amendment"] = parser_amendment+" Official scoring functions; unamended official report retained."
        errors = django_test_body_errors(grading_log.read_text(), spec.FAIL_TO_PASS+spec.PASS_TO_PASS) if row["repo"] == "django/django" else []
        receipt["attested_test_body_errors_count"] = len(errors)
        receipt["test_counts"] = coverage(task_report, spec, raw_statuses, errors)
        if runtime and runtime.get("strict_unregistered_failures"):
            unexpected = unregistered_failures(grading_log.read_text(), spec.FAIL_TO_PASS+spec.PASS_TO_PASS,
                row["repo"], raw_statuses, runtime.get("status_parser") == "exact_pytest_summary")
            atomic_json(output/"unregistered-failures.json", unexpected)
            receipt["unknown_failure_count"] = len(unexpected)
        else:
            unexpected = []
        receipt["completed"] = True
        receipt["resolved"] = task_report["resolved"] and not unexpected
    except BaseException as error:
        receipt["failure_type"] = type(error).__name__
        receipt["failure_message"] = str(error)[:500]
        raise
    finally:
        receipt["elapsed_seconds"] = time.monotonic() - started
        try:
            if container is not None:
                container.remove(force=True)
        except docker.errors.NotFound:
            pass
        finally:
            try:
                if database:
                    receipt["database_cleanup_errors"] = database.close()
            finally:
                client.close()
                atomic_json(output / "receipt.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--arch", choices=["arm64", "x86_64"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--setup-commit")
    parser.add_argument("--setup-overlay-sha256")
    parser.add_argument("--allow-derived-image", action="store_true")
    args = parser.parse_args()
    if args.reference and args.patch:
        parser.error("choose either a candidate patch or the quarantined reference fix")
    row = task_row(args.dataset, args.instance)
    patch = row["patch"] if args.reference else args.patch.read_text() if args.patch else ""
    receipt = grade(row, patch, args.output, args.image, args.image_id, args.arch, args.timeout,
                    args.setup_commit, args.setup_overlay_sha256, args.allow_derived_image)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
