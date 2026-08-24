#!/usr/bin/env python3
"""Frontier consultation check via Claude Code (subscription, no API cost).

Runs the real product surface: a seeded checkout carrying `metatron context setup`
artifacts (shipped v2 contract in AGENTS.md, context.md entry, sharded
context/decisions/), with Claude Code headless (`claude -p`) asked to fix the
SWE-bench bug. Claude Code auto-loads AGENTS.md natively — no scaffold prompt.

Measures, from the stream-json event log: consultation (any Read/Grep/Glob/Bash
touching context artifacts), deep read (contents of context.md or a decision file
actually opened), gold-file overlap of the resulting diff.

Pilot-grade, feasibility only. NOT scaffold-uniform with run_pilot.py — this cell
answers "does a frontier agent framework adhere to the shipped contract?", not an
arm of the Paper 2 matrix.

Usage: python pilot/run_claude_code.py [iid,iid|all]
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

os.environ.setdefault("CONDITION", "files-v2")  # shipped contract for setup_files
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_pilot as rp  # reuse instances, checkout cache, setup_files

ROOT = rp.ROOT
LOGS = ROOT / "pilot" / "logs" / "claude-code_files-v2"
WORK = ROOT / "pilot" / "work"
MAX_TURNS = 40

PROMPT = """Fix the following bug in this repository. Make the smallest targeted
code change that resolves it. Do not run the full test suite (single test files
are fine). Do not commit; leave the fix as uncommitted working-tree changes.

BUG REPORT:
{problem}"""

CTX_PATH = re.compile(r"context\.md|context/|AGENTS\.md")
DEEP_PATH = re.compile(r"context\.md$|context/decisions/[^\s]+\.md$")


def classify(events):
    consulted = deep = None
    n_tools = 0
    for i, ev in enumerate(events):
        if ev.get("type") != "assistant":
            continue
        for blk in ev.get("message", {}).get("content", []):
            if blk.get("type") != "tool_use":
                continue
            n_tools += 1
            inp = blk.get("input", {})
            probe = " ".join(str(inp.get(k, "")) for k in
                             ("file_path", "path", "command", "pattern", "glob"))
            if consulted is None and CTX_PATH.search(probe):
                consulted = n_tools
            fp = str(inp.get("file_path", ""))
            cmd = str(inp.get("command", ""))
            is_deep = (blk.get("name") == "Read" and DEEP_PATH.search(fp)) or \
                      (blk.get("name") == "Bash" and re.search(
                          r"^(cat|head|tail|sed)\b.*(context\.md|context/decisions/\S+\.md)", cmd, re.M))
            if deep is None and is_deep:
                deep = n_tools
    return {"consulted": consulted is not None, "first_read_tool": consulted,
            "deep_read": deep is not None, "deep_read_tool": deep, "n_tool_calls": n_tools}


def run(inst, repo_dir):
    t0 = time.time()
    env = {k: v for k, v in os.environ.items()
           if k not in ("ANTHROPIC_API_KEY", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    p = subprocess.run(
        ["claude", "-p", PROMPT.format(problem=" ".join(inst["problem_statement"].split())[:6000]),
         "--output-format", "stream-json", "--verbose",
         "--dangerously-skip-permissions", "--max-turns", str(MAX_TURNS)],
        cwd=repo_dir, capture_output=True, text=True, timeout=1200, env=env)
    events = []
    for line in p.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    patch = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True).stdout
    # context artifacts are untracked, but exclude any tracked-file noise under context/
    gold = set(re.findall(r"^diff --git a/(\S+)", inst["patch"], re.M))
    edited = {f for f in re.findall(r"^diff --git a/(\S+)", patch, re.M)
              if not f.startswith("context") and f != "AGENTS.md"}
    log = {"instance_id": inst["instance_id"], "runner": "claude-code",
           "exit": p.returncode, "wall_s": round(time.time() - t0, 1),
           "gold_files": sorted(gold), "edited_files": sorted(edited),
           "file_overlap": sorted(gold & edited), "patch_bytes": len(patch),
           "result_head": next((e.get("result", "")[:300] for e in events
                                if e.get("type") == "result"), ""),
           **classify(events)}
    (LOGS / f"{inst['instance_id']}.json").write_text(json.dumps(log, indent=1))
    (LOGS / f"{inst['instance_id']}.events.jsonl").write_text(p.stdout)
    return log


def main():
    import pandas as pd
    df = pd.read_parquet(rp.DATA).set_index("instance_id")
    LOGS.mkdir(parents=True, exist_ok=True)
    cache = WORK / "cache"; cache.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else rp.PILOT_INSTANCES
    for iid in only:
        inst = df.loc[iid].to_dict(); inst["instance_id"] = iid
        name = inst["repo"].split("/")[1]
        bare = cache / f"{name}.git"
        if not bare.exists():
            subprocess.run(["git", "clone", "--bare", f"https://github.com/{inst['repo']}.git", str(bare)], check=True)
        rd = WORK / f"cc_{iid}"
        if rd.exists():
            subprocess.run(["rm", "-rf", str(rd)])
        subprocess.run(["git", "clone", "--shared", str(bare), str(rd)], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-q", inst["base_commit"]], cwd=rd, check=True, capture_output=True)
        rp.setup_files(rd, name)
        # Claude Code headless loads CLAUDE.md, not AGENTS.md (probed 2026-07-15);
        # bridge with an @import — the fix `context setup` itself needs upstream.
        (rd / "CLAUDE.md").write_text("@AGENTS.md\n")
        print(f"=== {iid} ===", flush=True)
        log = run(inst, rd)
        print(json.dumps({k: log[k] for k in ("consulted", "deep_read", "n_tool_calls",
              "file_overlap", "patch_bytes", "wall_s", "exit")}), flush=True)


if __name__ == "__main__":
    main()
