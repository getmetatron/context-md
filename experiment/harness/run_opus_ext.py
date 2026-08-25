#!/usr/bin/env python3
"""Opus extension tier: 4 arms x 88 instances x 1 rep via Claude Code CLI.

Registered as an extension module (PREREGISTRATION-PAPER2 §2, not part of the
primary confirmatory analysis). Executor: claude-opus-4-8 via `claude -p`
(subscription-billed, same product surface as an end user runs). Args match
run_condition.py nomenclature; logs are compatible with analyze_p2.py.

Usage:
    python harness/run_opus_ext.py --condition B   # no context
    python harness/run_opus_ext.py --condition E   # injected seed
    python harness/run_opus_ext.py --condition FILE
    python harness/run_opus_ext.py --condition SHARD
    # or resume_opus_ext.sh for the full matrix
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

RATE_LIMIT_KEYWORDS = (
    "rate limit", "usage limit", "quota exceeded", "too many requests",
    "429", "slowdown", "capacity", "try again later",
)
RATE_LIMIT_WALL_MAX = 10  # seconds: fast fail with 0 tokens = likely rate limited

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from templates_p2 import CONTRACT_BLOCK_P2, write_context_files

SEEDS = ROOT / "seeds"
DATA = ROOT / "data" / "swebench_verified.parquet"
INSTANCES_FILE = ROOT / "harness" / "instances_opus_ext.json"
RUNS = ROOT / "runs" / "opus_ext"

REPO_MAP = {"astropy": "astropy/astropy", "django": "django/django",
            "matplotlib": "matplotlib/matplotlib", "pydata": "pydata/xarray",
            "pytest-dev": "pytest-dev/pytest", "scikit-learn": "scikit-learn/scikit-learn",
            "sphinx-doc": "sphinx-doc/sphinx", "sympy": "sympy/sympy"}

MAX_TURNS = 60
TIMEOUT = 1800  # 30 min

SYSTEM_PROMPT = (
    CONTRACT_BLOCK_P2 + "\n\n" +
    "Fix the following bug in this repository. Make the smallest targeted "
    "code change that resolves it. Do not run the full test suite (single test "
    "files are fine). Do not commit; leave the fix as uncommitted working-tree "
    "changes.\n\nBUG REPORT:\n{problem}"
)

BARE_PROMPT = (
    "Fix the following bug in this repository. Make the smallest targeted "
    "code change that resolves it. Do not run the full test suite (single test "
    "files are fine). Do not commit; leave the fix as uncommitted working-tree "
    "changes.\n\nBUG REPORT:\n{problem}"
)

CTX_PATH = re.compile(r"context\.md|context/|AGENTS\.md")
DEEP_PATH = re.compile(r"(?:^|/)context\.md$|context/decisions/[^\s]+\.md$")
DIFF_FILE = re.compile(r"^diff --git a/(\S+) b/", re.M)


def classify_events(events):
    consulted = deep = first_edit = None
    n = 0
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for blk in ev.get("message", {}).get("content", []):
            if blk.get("type") != "tool_use":
                continue
            n += 1
            inp = blk.get("input", {})
            probe = " ".join(str(inp.get(k, "")) for k in
                             ("file_path", "path", "command", "pattern", "glob"))
            if consulted is None and CTX_PATH.search(probe):
                consulted = n
            fp = str(inp.get("file_path", ""))
            cmd = str(inp.get("command", ""))
            is_deep = (blk["name"] == "Read" and DEEP_PATH.search(fp)) or \
                      (blk["name"] == "Bash" and re.search(
                          r"^(cat|head|tail|sed)\b.*(context\.md|context/decisions/\S+\.md)", cmd, re.M))
            if deep is None and is_deep:
                deep = n
            is_edit = blk["name"] in ("Write", "Edit", "MultiEdit") or \
                      (blk["name"] == "Bash" and re.search(r"sed -i|>\s*\S", cmd))
            if first_edit is None and is_edit:
                first_edit = n
    return {"consulted": consulted is not None, "first_read_tool": consulted,
            "deep_read": deep is not None, "deep_read_tool": deep,
            "read_before_edit": consulted is not None and (first_edit is None or consulted < first_edit),
            "n_tool_calls": n}


def token_counts(events):
    pt = ct = 0
    for ev in events:
        usage = ev.get("message", {}).get("usage", {})
        pt += usage.get("input_tokens", 0)
        ct += usage.get("output_tokens", 0)
    return pt, ct


def is_rate_limited(exit_code, wall_s, pt, stderr):
    if pt == 0 and exit_code != 0 and wall_s < RATE_LIMIT_WALL_MAX:
        return True
    stderr_lower = (stderr or "").lower()
    return any(kw in stderr_lower for kw in RATE_LIMIT_KEYWORDS)


def build_prompt(cond, seed_text, problem):
    if cond == "B":
        return BARE_PROMPT.format(problem=problem)
    if cond == "E":
        return (
            "Repository context (read this before making any changes):\n\n"
            + seed_text + "\n\n"
            + "Fix the following bug in this repository. Make the smallest targeted "
            "code change that resolves it. Do not run the full test suite (single test "
            "files are fine). Do not commit; leave the fix as uncommitted working-tree "
            "changes.\n\nBUG REPORT:\n" + problem
        )
    return SYSTEM_PROMPT.format(problem=problem)  # FILE / SHARD


def run_episode(iid, inst, repo_dir, cond, seed_text):
    problem = " ".join(inst["problem_statement"].split())[:8000]
    prompt = build_prompt(cond, seed_text, problem)

    env = {k: v for k, v in os.environ.items()
           if k not in ("ANTHROPIC_API_KEY", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}

    # write context artifacts for FILE/SHARD
    ctx_files = 0
    if cond in ("FILE", "SHARD"):
        mode = "file" if cond == "FILE" else "sharded"
        ctx_files = write_context_files(repo_dir, seed_text, mode)
        (repo_dir / "CLAUDE.md").write_text("@AGENTS.md\n")
    elif cond == "E":
        # injected context: no files, contract+seed in system prompt (already in prompt)
        pass

    t0 = time.time()
    try:
        p = subprocess.run(
            ["claude", "-p", prompt,
             "--model", "claude-opus-4-8",
             "--output-format", "stream-json", "--verbose",
             "--dangerously-skip-permissions", "--max-turns", str(MAX_TURNS)],
            cwd=repo_dir, capture_output=True, text=True, timeout=TIMEOUT, env=env)
        timed_out = False
    except subprocess.TimeoutExpired:
        timed_out = True
        p = type("P", (), {"returncode": 124, "stdout": "", "stderr": ""})()

    events = []
    for line in p.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    patch = subprocess.run(["git", "diff"], cwd=repo_dir,
                           capture_output=True, text=True).stdout
    gold_files = set(DIFF_FILE.findall(inst["patch"]))
    edited = {f for f in DIFF_FILE.findall(patch)
              if not f.startswith("context") and f != "AGENTS.md"}
    pt, ct = token_counts(events)

    log = {
        "instance_id": iid, "condition": cond, "rep": 1,
        "executor": "claude-opus-4-8", "runner": "claude-code-cli",
        "context_files_written": ctx_files,
        "patch_bytes": len(patch),
        "submitted": bool(patch.strip()),
        "gold_hit": bool(gold_files & edited),
        "file_overlap": sorted(gold_files & edited),
        "prompt_tokens": pt, "completion_tokens": ct,
        "n_tool_calls": 0,  # filled below
        "timed_out": timed_out,
        "exit": p.returncode,
        "wall_s": round(time.time() - t0, 1),
        **classify_events(events),
    }
    return log, patch, p.stderr


def main():
    import argparse
    import pandas as pd

    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=["B", "E", "FILE", "SHARD"])
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--rate-limit-wait", type=int, default=3600,
                    help="Seconds to wait when a rate-limit is detected (default 3600)")
    ap.add_argument("--max-retries", type=int, default=8,
                    help="Max rate-limit retries per episode before skipping (default 8)")
    args = ap.parse_args()

    cond = args.condition
    instances = json.load(open(INSTANCES_FILE))["instances"]

    df = pd.read_parquet(DATA).set_index("instance_id")
    out_dir = RUNS / cond / "rep1"
    out_dir.mkdir(parents=True, exist_ok=True)

    cache = RUNS / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    work = RUNS / "work"
    work.mkdir(parents=True, exist_ok=True)

    done = 0
    for iid in instances:
        log_f = out_dir / f"{iid}.json"
        if args.skip_existing and log_f.exists():
            done += 1
            continue

        inst = df.loc[iid].to_dict()
        repo_slug = inst["repo"].split("/")[1]
        repo_key = iid.split("__")[0]
        gh_repo = REPO_MAP[repo_key]

        # bare clone cache (only needed once per repo)
        bare = cache / f"{repo_slug}.git"
        if not bare.exists():
            print(f"  cloning {gh_repo}...", flush=True)
            subprocess.run(["git", "clone", "--bare",
                            f"https://github.com/{gh_repo}.git", str(bare)], check=True)

        # seed text (constant across retries)
        seed_text = ""
        if cond in ("E", "FILE", "SHARD"):
            sf = SEEDS / repo_slug / "context.md"
            seed_text = sf.read_text() if sf.exists() else ""

        rd = work / f"opus_{iid}"
        print(f"=== {cond} {iid} ===", flush=True)

        for rl_attempt in range(args.max_retries + 1):
            if rl_attempt > 0:
                print(f"  RATE_LIMIT: waiting {args.rate_limit_wait}s "
                      f"(attempt {rl_attempt}/{args.max_retries})...", flush=True)
                time.sleep(args.rate_limit_wait)

            # fresh working tree — re-clone on every attempt (clean state)
            for clone_attempt in range(2):
                if rd.exists():
                    subprocess.run(["rm", "-rf", str(rd)])
                r = subprocess.run(["git", "clone", "--shared", str(bare), str(rd)],
                                   capture_output=True)
                if r.returncode == 0:
                    break
                time.sleep(5 + clone_attempt * 10)
            else:
                print(f"  SKIP {iid}: git clone failed twice", flush=True)
                break
            subprocess.run(["git", "checkout", "-q", inst["base_commit"]],
                           cwd=rd, check=True, capture_output=True)

            try:
                log, patch, stderr = run_episode(iid, inst, rd, cond, seed_text)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                break

            if is_rate_limited(log["exit"], log["wall_s"], log["prompt_tokens"], stderr):
                if rl_attempt < args.max_retries:
                    print(f"  RATE_LIMIT detected (exit={log['exit']} "
                          f"wall={log['wall_s']}s pt={log['prompt_tokens']})", flush=True)
                    continue
                else:
                    print(f"  RATE_LIMIT: max retries exceeded, skipping {iid}", flush=True)
                    break

            # non-rate-limit result — save and move on
            log_f.write_text(json.dumps(log, indent=1))
            pred_f = out_dir / "predictions.jsonl"
            with pred_f.open("a") as fh:
                fh.write(json.dumps({"instance_id": iid,
                                     "model_name_or_path": f"opus-{cond}-rep1",
                                     "model_patch": patch}) + "\n")
            done += 1
            print(f"  gold_hit={log['gold_hit']} consulted={log['consulted']} "
                  f"deep_read={log['deep_read']} pt={log['prompt_tokens']} "
                  f"ct={log['completion_tokens']} wall={log['wall_s']}s", flush=True)
            break

    print(f"\n{cond} DONE: {done}/{len(instances)}", flush=True)


if __name__ == "__main__":
    main()
