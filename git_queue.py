#!/usr/bin/env python3
"""Git coordination prototype. Does not invoke models or inspect grading outcomes."""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import os
import subprocess
import tempfile
import time
import uuid


class QueueError(RuntimeError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def positive(value, label):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise QueueError(f"{label} must be positive and finite")


def validate_manifest(manifest):
    jobs = manifest.get("jobs", [])
    if manifest.get("schema") != 1 or not isinstance(jobs, list) or not jobs:
        raise QueueError("manifest requires schema 1 and a nonempty jobs list")
    by_id = {}
    for job in jobs:
        name = job.get("job_id", "")
        if not isinstance(name, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", name) or name in by_id:
            raise QueueError("job IDs must be unique safe identifiers")
        if not isinstance(job.get("max_attempts"), int) or isinstance(job["max_attempts"], bool) or job["max_attempts"] < 1:
            raise QueueError(f"{name}: max_attempts must be a positive integer")
        for key in ("capabilities", "depends_on"):
            if not isinstance(job.get(key), list) or any(not isinstance(x, str) or not x for x in job[key]):
                raise QueueError(f"{name}: {key} must be a list of strings")
        if not isinstance(job.get("spec"), dict):
            raise QueueError(f"{name}: spec must be an object")
        availability_limit = job.get("max_availability_attempts", 8)
        if not isinstance(availability_limit, int) or isinstance(availability_limit, bool) or availability_limit < 1:
            raise QueueError(f"{name}: max_availability_attempts must be a positive integer")
        if job.get("assigned_worker") is not None and not re.fullmatch(r"worker-[0-9]{2,}", job["assigned_worker"]):
            raise QueueError(f"{name}: assigned_worker must be a generic worker ID")
        by_id[name] = job
    visiting, visited = set(), set()

    def visit(name):
        if name not in by_id or name in visiting:
            raise QueueError("missing or cyclic job dependency")
        if name in visited:
            return
        visiting.add(name)
        for dependency in by_id[name]["depends_on"]:
            visit(dependency)
        visiting.remove(name)
        visited.add(name)

    for name in by_id:
        visit(name)
    encoded(manifest)
    return jobs


class GitQueue:
    def __init__(self, remote, branch="queue-v1", retries=12):
        if not remote or str(remote).startswith("-"):
            raise QueueError("remote must be a path or a Git remote URL")
        # Every transaction uses a new temporary checkout, so resolve local
        # paths now rather than relative to that checkout. Named remotes such
        # as 'origin' are intentionally unsupported.
        local = Path(remote).expanduser()
        if local.exists():
            self.remote = str(local.resolve())
        elif ":" in str(remote):
            self.remote = str(remote)
        else:
            raise QueueError("remote must be an existing local path or an explicit Git URL")
        self.branch = branch
        self.ref = f"refs/heads/{branch}"
        self.retries = retries
        self._git(None, "check-ref-format", self.ref)

    @staticmethod
    def _git(cwd, *args, check=True):
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_SSH_COMMAND": "ssh -o BatchMode=yes -o ConnectTimeout=10"}
        result = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
             "-c", "user.name=Research Queue", "-c", "user.email=queue@example.invalid", *args],
            cwd=cwd, text=True, capture_output=True, timeout=20, env=env,
        )
        if check and result.returncode:
            raise QueueError(result.stderr.strip() or "Git command failed")
        return result

    def _remote_head(self):
        result = self._git(None, "ls-remote", "--exit-code", self.remote, self.ref, check=False)
        if result.returncode == 2:
            return None
        if result.returncode:
            raise QueueError(result.stderr.strip() or "cannot read remote")
        return result.stdout.split()[0]

    def _load(self, directory):
        self._git(directory, "init", "--quiet")
        self._git(directory, "fetch", "--quiet", "--no-tags", "--depth=1", self.remote, self.ref)
        self._git(directory, "checkout", "--quiet", "--detach", "FETCH_HEAD")
        head = self._git(directory, "rev-parse", "HEAD").stdout.strip()
        state = json.loads((Path(directory) / "state.json").read_text())
        if state.get("schema") != 1:
            raise QueueError("unsupported queue state schema")
        digest = hashlib.sha256(encoded(state["manifest"]).encode()).hexdigest()
        if digest != state["manifest_sha256"]:
            raise QueueError("manifest digest mismatch")
        return head, state

    def _push(self, directory, state):
        (Path(directory) / "state.json").write_text(encoded(state) + "\n")
        self._git(directory, "add", "state.json")
        self._git(directory, "commit", "--quiet", "-m", "Record queue transition")
        return self._git(directory, "push", "--quiet", self.remote, f"HEAD:{self.ref}", check=False)

    def initialize(self, manifest):
        jobs = validate_manifest(manifest)
        if self._remote_head() is not None:
            raise QueueError("queue already exists; manifests are immutable")
        state = {
            "schema": 1,
            "manifest": copy.deepcopy(manifest),
            "manifest_sha256": hashlib.sha256(encoded(manifest).encode()).hexdigest(),
            "job_order": [job["job_id"] for job in jobs],
            "jobs": {job["job_id"]: {"state": "pending", "generation": 0, "attempts": []} for job in jobs},
            "workers": {},
        }
        with tempfile.TemporaryDirectory(prefix="research-queue-") as directory:
            self._git(directory, "init", "--quiet")
            result = self._push(directory, state)
            if result.returncode:
                raise QueueError("queue initialization failed or another initializer won")
        return state["manifest_sha256"]

    def snapshot(self):
        with tempfile.TemporaryDirectory(prefix="research-queue-") as directory:
            return self._load(directory)[1]

    def _mutate(self, operation):
        for _ in range(self.retries):
            with tempfile.TemporaryDirectory(prefix="research-queue-") as directory:
                head, state = self._load(directory)
                before = encoded(state)
                result = operation(state)
                if encoded(state) == before:
                    return result
                try:
                    pushed = self._push(directory, state)
                except subprocess.TimeoutExpired:
                    # A timeout can occur after the server accepted the push.
                    # Re-read the remote rather than replaying stale state.
                    continue
                if pushed.returncode == 0:
                    return result
                if self._remote_head() == head:
                    raise QueueError(pushed.stderr.strip() or "queue push rejected")
                # Another transition won, or our push succeeded despite a lost
                # acknowledgement. Reload and recompute; never rebase old state.
        raise QueueError("queue contention exceeded retry allowance")

    @staticmethod
    def _job(state, job_id):
        if job_id not in state["jobs"]:
            raise QueueError("unknown job")
        return state["jobs"][job_id]

    @classmethod
    def _owned(cls, state, job_id, worker, attempt_id, generation):
        job = cls._job(state, job_id)
        if not job["attempts"]:
            raise QueueError("job has no attempt")
        attempt = job["attempts"][-1]
        if (attempt["worker"], attempt["attempt_id"], job["generation"]) != (worker, attempt_id, generation):
            raise QueueError("stale or foreign ownership token")
        return job, attempt

    @staticmethod
    def _live(job, attempt, now):
        if job["state"] != "leased" or attempt["lease_expires_at"] <= now:
            raise QueueError("attempt is no longer active or its lease expired")

    @staticmethod
    def _exhausted(job, spec):
        charged = sum(attempt.get("counts_toward_limit", True) for attempt in job["attempts"])
        availability = len(job["attempts"]) - charged
        return charged >= spec["max_attempts"] or availability >= spec.get("max_availability_attempts", 8)

    def pause_worker(self, worker, reason, retry_at=None, *, now=None):
        if not re.fullmatch(r"worker-[0-9]{2,}", worker):
            raise QueueError("use a generic worker ID")
        if retry_at is not None:
            positive(retry_at, "retry_at")

        def operation(state):
            timestamp = time.time() if now is None else now
            return self._pause(state, worker, reason, retry_at, timestamp)

        return self._mutate(operation)

    @staticmethod
    def _pause(state, worker, reason, retry_at, timestamp):
        previous = state.setdefault("workers", {}).get(worker, {})
        # A missing reset must not erase a previously known future reset or
        # silently clear a manual authentication/configuration pause.
        if previous.get("paused") and previous.get("retry_at") is None:
            retry_at = None
        elif retry_at is not None:
            retry_at = max(retry_at, previous.get("retry_at") or 0)
        elif reason == "quota" and (previous.get("retry_at") or 0) > timestamp:
            retry_at = previous["retry_at"]
        record = {"paused": True, "reason": reason, "retry_at": retry_at, "updated_at": timestamp}
        state["workers"][worker] = record
        return copy.deepcopy(record)

    def resume_worker(self, worker):
        if not re.fullmatch(r"worker-[0-9]{2,}", worker):
            raise QueueError("use a generic worker ID")
        def operation(state):
            state.setdefault("workers", {}).pop(worker, None)
            return {"worker": worker, "paused": False}

        return self._mutate(operation)

    def hold(self, job_id, worker, attempt_id, generation, reason, artifacts=None, *, now=None):
        """Quarantine ambiguous work instead of silently retrying or excluding it."""
        def operation(state):
            job, attempt = self._owned(state, job_id, worker, attempt_id, generation)
            if job["state"] == "blocked" and attempt.get("reason") == reason:
                return copy.deepcopy(attempt)
            if job["state"] != "leased":
                raise QueueError("attempt is no longer owned")
            attempt.update(status="needs_review", reason=reason, artifacts=copy.deepcopy(artifacts),
                           finished_at=time.time() if now is None else now)
            job["state"] = "blocked"
            return copy.deepcopy(attempt)

        return self._mutate(operation)

    def accept_reviewed(self, job_id, worker, attempt_id, generation, result, review_reason, *, now=None):
        """Accept preserved outputs after explicit audit of a held current attempt.

        Never reruns compute, changes the manifest, or overwrites a newer owner.
        The original failure reason/evidence remain in the attempt history.
        """
        if not isinstance(review_reason, str) or not review_reason.strip():
            raise QueueError("review requires a concrete audit reason")
        if result.get("outcome") not in {"outputs_ready", "coding_failure", "research_budget_exhausted"} or not result.get("artifacts"):
            raise QueueError("review requires an accepted outcome with preserved artifacts")
        for item in result["artifacts"]:
            if not isinstance(item.get("uri"), str) or not item["uri"] or not re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", "")):
                raise QueueError("review artifact descriptor is invalid")
        def operation(state):
            job, attempt = self._owned(state, job_id, worker, attempt_id, generation)
            if job["state"] == "completed" and attempt.get("result") == result and attempt.get("review", {}).get("reason") == review_reason:
                return copy.deepcopy(attempt)
            if job["state"] != "blocked" or attempt.get("status") != "needs_review":
                raise QueueError("only a held current attempt can be accepted after review")
            attempt["review"] = {"reason": review_reason, "prior_reason": attempt.get("reason"),
                                 "reviewed_at": time.time() if now is None else now}
            attempt.update(status="completed", result=copy.deepcopy(result))
            job["state"] = "completed"
            return copy.deepcopy(attempt)
        return self._mutate(operation)

    def claim(self, worker, capabilities, lease_seconds=300, *, request_id=None, now=None):
        if not re.fullmatch(r"worker-[0-9]{2,}", worker):
            raise QueueError("use a generic worker ID such as worker-01")
        positive(lease_seconds, "lease_seconds")
        attempt_id = request_id or uuid.uuid4().hex
        if not isinstance(attempt_id, str) or not re.fullmatch(r"[a-f0-9]{32}", attempt_id):
            raise QueueError("request_id must be a lowercase UUID hex string")

        def operation(state):
            timestamp = time.time() if now is None else now
            # Idempotent recovery if a successful push lost its acknowledgement.
            for job_id, job in state["jobs"].items():
                if job["attempts"] and job["attempts"][-1]["attempt_id"] == attempt_id:
                    self._live(job, job["attempts"][-1], timestamp)
                    spec = next(spec for spec in state["manifest"]["jobs"] if spec["job_id"] == job_id)
                    return {"job_id": job_id, **job["attempts"][-1], "spec": spec["spec"]}
            pause = state.get("workers", {}).get(worker, {})
            if pause.get("paused") and (pause.get("retry_at") is None or timestamp < pause["retry_at"]):
                return None
            if any(job["state"] == "leased" and job["attempts"][-1]["worker"] == worker for job in state["jobs"].values()):
                raise QueueError("worker already owns a lease; recover it before claiming another job")
            specs = {job["job_id"]: job for job in state["manifest"]["jobs"]}
            for job_id in state["job_order"]:
                job, spec = state["jobs"][job_id], specs[job_id]
                if job["state"] != "pending" or not set(spec["capabilities"]).issubset(capabilities):
                    continue
                if spec.get("assigned_worker") not in (None, worker):
                    continue
                if not all(state["jobs"][dep]["state"] == "completed" for dep in spec["depends_on"]):
                    continue
                if self._exhausted(job, spec):
                    raise QueueError("inconsistent retry state")
                job["generation"] += 1
                attempt = {
                    "attempt_id": attempt_id, "worker": worker, "generation": job["generation"],
                    "started_at": timestamp, "heartbeat_at": timestamp,
                    "lease_expires_at": timestamp + lease_seconds, "status": "running",
                }
                job["attempts"].append(attempt)
                job["state"] = "leased"
                return {"job_id": job_id, **attempt, "spec": spec["spec"]}
            return None

        return self._mutate(operation)

    def heartbeat(self, job_id, worker, attempt_id, generation, lease_seconds=300, *, now=None):
        positive(lease_seconds, "lease_seconds")

        def operation(state):
            timestamp = time.time() if now is None else now
            job, attempt = self._owned(state, job_id, worker, attempt_id, generation)
            self._live(job, attempt, timestamp)
            attempt.update(heartbeat_at=timestamp, lease_expires_at=max(attempt["lease_expires_at"], timestamp + lease_seconds))
            return copy.deepcopy(attempt)

        return self._mutate(operation)

    def finish(self, job_id, worker, attempt_id, generation, result, *, now=None):
        if not isinstance(result, dict) or result.get("outcome") not in {"outputs_ready", "coding_failure", "research_budget_exhausted"}:
            raise QueueError("result outcome must be outputs_ready, coding_failure, or research_budget_exhausted")
        artifacts = result.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise QueueError("result must reference at least one artifact (including an empty patch/store)")
        for artifact in artifacts:
            if (not isinstance(artifact, dict) or not isinstance(artifact.get("uri"), str)
                    or not artifact["uri"] or not isinstance(artifact.get("sha256"), str)
                    or not re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"])):
                raise QueueError("each artifact needs a URI and lowercase SHA-256 digest")
        encoded(result)

        def operation(state):
            timestamp = time.time() if now is None else now
            job, attempt = self._owned(state, job_id, worker, attempt_id, generation)
            if job["state"] == "completed" and attempt.get("result") == result:
                return copy.deepcopy(attempt)
            self._live(job, attempt, timestamp)
            attempt.update(status="completed", finished_at=timestamp, result=copy.deepcopy(result))
            job["state"] = "completed"
            return copy.deepcopy(attempt)

        return self._mutate(operation)

    @staticmethod
    def _release(state, job_id, job, attempt, status, reason, timestamp, artifacts, availability_only=False):
        spec = next(spec for spec in state["manifest"]["jobs"] if spec["job_id"] == job_id)
        attempt.update(status=status, reason=reason, finished_at=timestamp, artifacts=copy.deepcopy(artifacts),
                       counts_toward_limit=not availability_only)
        job["state"] = "blocked" if GitQueue._exhausted(job, spec) else "pending"
        return copy.deepcopy(attempt)

    def interrupt(self, job_id, worker, attempt_id, generation, reason, artifacts=None, *,
                  retry_at=None, pause_worker=None, availability_only=False, now=None):
        if reason not in {"quota", "authentication", "service", "environment"}:
            raise QueueError("interruption reason must be quota, authentication, service, or environment")
        if availability_only and reason not in {"quota", "authentication"}:
            raise QueueError("only evidenced quota/auth rejection before productive progress can be availability-only")
        if retry_at is not None:
            positive(retry_at, "retry_at")
        if pause_worker is None:
            pause_worker = reason in {"quota", "authentication"}

        def operation(state):
            timestamp = time.time() if now is None else now
            job, attempt = self._owned(state, job_id, worker, attempt_id, generation)
            if attempt["status"] == "interrupted" and attempt.get("reason") == reason and attempt.get("artifacts") == artifacts:
                return copy.deepcopy(attempt)
            self._live(job, attempt, timestamp)
            if pause_worker:
                self._pause(state, worker, reason, retry_at, timestamp)
            return self._release(state, job_id, job, attempt, "interrupted", reason, timestamp, artifacts, availability_only)

        return self._mutate(operation)

    def maintenance(self, grace_seconds=60, *, now=None):
        positive(grace_seconds, "grace_seconds")

        def operation(state):
            timestamp = time.time() if now is None else now
            reclaimed = []
            for job_id, job in state["jobs"].items():
                if job["state"] == "leased" and timestamp >= job["attempts"][-1]["lease_expires_at"] + grace_seconds:
                    self._release(state, job_id, job, job["attempts"][-1], "abandoned", "lease_expired", timestamp, None)
                    reclaimed.append(job_id)
            return {"reclaimed": reclaimed, "health": self.health(state, timestamp)}

        return self._mutate(operation)

    @staticmethod
    def health(state, now=None):
        timestamp = time.time() if now is None else now
        counts = {name: sum(job["state"] == name for job in state["jobs"].values())
                  for name in ("pending", "leased", "completed", "blocked")}
        blocked_dependencies = []
        for spec in state["manifest"]["jobs"]:
            if state["jobs"][spec["job_id"]]["state"] == "pending" and any(
                    state["jobs"][dep]["state"] == "blocked" for dep in spec["depends_on"]):
                blocked_dependencies.append(spec["job_id"])
        return {"counts": counts, "blocked_dependencies": blocked_dependencies,
                "expired_leases": [name for name, job in state["jobs"].items()
                                   if job["state"] == "leased" and job["attempts"][-1]["lease_expires_at"] <= timestamp],
                "stale_heartbeats": [name for name, job in state["jobs"].items()
                                     if job["state"] == "leased" and timestamp - job["attempts"][-1]["heartbeat_at"] > 90],
                "paused_workers": {name: value for name, value in state.get("workers", {}).items()
                                   if value.get("paused") and (value.get("retry_at") is None or value["retry_at"] > timestamp)}}

    def reclaim(self, job_id, grace_seconds=60, artifacts=None, *, now=None):
        positive(grace_seconds, "grace_seconds")

        def operation(state):
            timestamp = time.time() if now is None else now
            job = self._job(state, job_id)
            if job["state"] != "leased":
                raise QueueError("only leased jobs can be reclaimed")
            attempt = job["attempts"][-1]
            if timestamp < attempt["lease_expires_at"] + grace_seconds:
                raise QueueError("lease has not expired beyond the clock-skew grace period")
            return self._release(state, job_id, job, attempt, "abandoned", "lease_expired", timestamp, artifacts)

        return self._mutate(operation)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", required=True, help="dedicated queue repository URL or local bare repository")
    parser.add_argument("--branch", default="queue-v1")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("init").add_argument("manifest", type=Path)
    commands.add_parser("status")
    commands.add_parser("health")
    maintenance = commands.add_parser("maintenance")
    maintenance.add_argument("--grace-seconds", type=float, default=60)
    pause = commands.add_parser("pause")
    pause.add_argument("--worker", required=True)
    pause.add_argument("--reason", required=True)
    pause.add_argument("--retry-at", type=float)
    commands.add_parser("resume").add_argument("--worker", required=True)
    claim = commands.add_parser("claim")
    claim.add_argument("--worker", required=True)
    claim.add_argument("--capability", action="append", default=[])
    claim.add_argument("--lease-seconds", type=float, default=300)
    claim.add_argument("--request-id")
    for name in ("heartbeat", "finish", "interrupt"):
        command = commands.add_parser(name)
        command.add_argument("--job", required=True)
        command.add_argument("--worker", required=True)
        command.add_argument("--attempt", required=True)
        command.add_argument("--generation", required=True, type=int)
        if name == "heartbeat":
            command.add_argument("--lease-seconds", type=float, default=300)
        elif name == "finish":
            command.add_argument("--result", required=True, type=Path)
        else:
            command.add_argument("--reason", required=True)
            command.add_argument("--artifacts", type=Path)
            command.add_argument("--retry-at", type=float)
            command.add_argument("--availability-only", action="store_true")
    reclaim = commands.add_parser("reclaim")
    reclaim.add_argument("--job", required=True)
    reclaim.add_argument("--grace-seconds", type=float, default=60)
    reclaim.add_argument("--artifacts", type=Path)
    args = parser.parse_args()
    try:
        queue = GitQueue(args.remote, args.branch)
        if args.action == "init":
            result = queue.initialize(json.loads(args.manifest.read_text()))
        elif args.action == "status":
            result = queue.snapshot()
        elif args.action == "health":
            result = queue.health(queue.snapshot())
        elif args.action == "maintenance":
            result = queue.maintenance(args.grace_seconds)
        elif args.action == "pause":
            result = queue.pause_worker(args.worker, args.reason, args.retry_at)
        elif args.action == "resume":
            result = queue.resume_worker(args.worker)
        elif args.action == "claim":
            result = queue.claim(args.worker, args.capability, args.lease_seconds, request_id=args.request_id)
        elif args.action == "reclaim":
            artifacts = json.loads(args.artifacts.read_text()) if args.artifacts else None
            result = queue.reclaim(args.job, args.grace_seconds, artifacts)
        else:
            owner = (args.job, args.worker, args.attempt, args.generation)
            if args.action == "heartbeat":
                result = queue.heartbeat(*owner, args.lease_seconds)
            elif args.action == "finish":
                result = queue.finish(*owner, json.loads(args.result.read_text()))
            else:
                artifacts = json.loads(args.artifacts.read_text()) if args.artifacts else None
                result = queue.interrupt(*owner, args.reason, artifacts, retry_at=args.retry_at,
                                         availability_only=args.availability_only)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (QueueError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"queue error: {error}\n")


if __name__ == "__main__":
    main()
