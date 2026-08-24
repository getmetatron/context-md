#!/usr/bin/env python3
"""Frontier consultation check via Gemini CLI (subscription, no API cost).

Sibling of run_claude_code.py: same seeded checkouts (shipped v2 contract), same
question — does the native agent framework consult context/decisions/ unprompted?

Gemini CLI loads GEMINI.md by default, not AGENTS.md; a per-repo
.gemini/settings.json with contextFileName ["AGENTS.md","GEMINI.md"] points it at
the shipped artifact (a real Gemini-CLI Metatron user would need the same setting —
product note, not a hack).

Usage: python pilot/run_gemini_cli.py [iid,iid|all]
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

os.environ.setdefault("CONDITION", "files-v2")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_pilot as rp

ROOT = rp.ROOT
LOGS = ROOT / "pilot" / "logs" / "gemini-cli_files-v2"
WORK = rp.ROOT / "pilot" / "work"

PROMPT = """Fix the following bug in this repository. Make the smallest targeted
code change that resolves it. Do not run the full test suite (single test files
are fine). Do not commit; leave the fix as uncommitted working-tree changes.

BUG REPORT:
{problem}"""

CTX_PATH = re.compile(r"context\.md|context/|AGENTS\.md")
DEEP_PATH = re.compile(r"context\.md|context/decisions/\S+\.md")


def classify(events):
    """Tolerant tool-call scan: gemini stream-json event shapes vary by version;
    look for tool-call-ish events and probe their args for context paths."""
    consulted = deep = None
    n_tools = 0
    for ev in events:
        blob = json.dumps(ev)
        etype = str(ev.get("type", ""))
        if "tool" not in etype and "tool_use" not in blob[:200] and "toolCall" not in blob[:200]:
            continue
        n_tools += 1
        if consulted is None and CTX_PATH.search(blob):
            consulted = n_tools
        name = str(ev.get("name", "") or ev.get("tool_name", "") or "")
        args = json.dumps(ev.get("args", ev.get("input", ev.get("parameters", {}))))
        is_read = name.lower() in ("read_file", "readfile", "read_many_files", "read")
        is_cat = bool(re.search(r"\b(cat|head|tail|sed)\b", args))
        if deep is None and (is_read or is_cat) and DEEP_PATH.search(args):
            deep = n_tools
    return {"consulted": consulted is not None, "first_read_tool": consulted,
            "deep_read": deep is not None, "deep_read_tool": deep, "n_tool_calls": n_tools}


def run(inst, repo_dir):
    t0 = time.time()
    (repo_dir / ".gemini").mkdir(exist_ok=True)
    (repo_dir / ".gemini" / "settings.json").write_text(json.dumps(
        {"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}}))
    env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY",)}
    p = subprocess.run(
        ["gemini", "-p", PROMPT.format(problem=" ".join(inst["problem_statement"].split())[:6000]),
         "-o", "stream-json", "--approval-mode", "yolo"],
        cwd=repo_dir, capture_output=True, text=True, timeout=1200, env=env)
    events = []
    for line in p.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    patch = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True).stdout
    gold = set(re.findall(r"^diff --git a/(\S+)", inst["patch"], re.M))
    edited = {f for f in re.findall(r"^diff --git a/(\S+)", patch, re.M)
              if not f.startswith("context") and f not in ("AGENTS.md", "GEMINI.md")}
    log = {"instance_id": inst["instance_id"], "runner": "gemini-cli",
           "exit": p.returncode, "wall_s": round(time.time() - t0, 1),
           "gold_files": sorted(gold), "edited_files": sorted(edited),
           "file_overlap": sorted(gold & edited), "patch_bytes": len(patch),
           **classify(events)}
    (LOGS / f"{inst['instance_id']}.json").write_text(json.dumps(log, indent=1))
    (LOGS / f"{inst['instance_id']}.events.jsonl").write_text(p.stdout)
    if p.returncode != 0:
        (LOGS / f"{inst['instance_id']}.stderr.txt").write_text(p.stderr[-5000:])
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
        rd = WORK / f"gm_{iid}"
        if rd.exists():
            subprocess.run(["rm", "-rf", str(rd)])
        subprocess.run(["git", "clone", "--shared", str(bare), str(rd)], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-q", inst["base_commit"]], cwd=rd, check=True, capture_output=True)
        rp.setup_files(rd, name)
        print(f"=== {iid} ===", flush=True)
        log = run(inst, rd)
        print(json.dumps({k: log[k] for k in ("consulted", "deep_read", "n_tool_calls",
              "file_overlap", "patch_bytes", "wall_s", "exit")}), flush=True)


if __name__ == "__main__":
    main()
