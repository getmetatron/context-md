#!/usr/bin/env python3
"""Gemma 4 capability pilot — can a local 8B model hold a SWE-bench agent loop?

Feasibility only (excluded from confirmatory analysis, per PREREGISTRATION.md).
Measures: loop coherence, valid-command rate, patch emission, files-touched overlap
with gold patch. No context layer in any pilot run.

Protocol (mini-swe-agent style, scaffold-uniform for later frontier arms):
  - system prompt: task + rules; model must reply with ONE ```bash block per turn
  - `submit` as the command ends the episode; patch = git diff
"""
import json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "swebench_verified.parquet"
WORK = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "pilot" / "work"
CONDITION = os.environ.get("CONDITION", "control")  # control | treatment | files | files-bare
EXECUTOR = os.environ.get("EXECUTOR", "ollama")     # ollama | anthropic
CONTEXT_DIR = ROOT / "pilot" / "context"            # <reponame>.md, injected in treatment only
SEEDS = ROOT / "seeds"                               # frozen E-arm seeds (files modes)
FRONTIER_MODEL = "claude-opus-4-8"
OLLAMA = "http://localhost:11434/api/chat"
MODEL = os.environ.get("MODEL", "gemma4:e4b")
_suffix = "" if MODEL == "gemma4:e4b" else "_" + re.sub(r"[^a-z0-9]+", "-", MODEL)
LOGS = ROOT / "pilot" / "logs" / ((CONDITION if EXECUTOR == "ollama" else f"{CONDITION}_{EXECUTOR}") + _suffix)
MAX_TURNS = 20
CMD_TIMEOUT = 90
OUT_CAP = 3000  # chars of command output fed back

PILOT_INSTANCES = [
    # sphinx S1/S2 (easy)
    "sphinx-doc__sphinx-10449", "sphinx-doc__sphinx-7454", "sphinx-doc__sphinx-8459",
    "sphinx-doc__sphinx-7462", "sphinx-doc__sphinx-9230", "sphinx-doc__sphinx-9591",
    # django D1/D2 (easy)
    "django__django-15499", "django__django-16595", "django__django-12125",
    "django__django-14580",
]

SYSTEM = """You are an expert software engineer fixing a bug in a large open-source repository.
You are in the repository root. You interact ONLY by issuing shell commands.

RULES:
1. Reply with a short plan (max 3 sentences), then EXACTLY ONE bash code block containing ONE command.
2. Use grep/sed/cat/python to explore and edit. No interactive tools (no vim, no less, no git add/commit).
3. Edit files with: python3 - <<'EOF' ... EOF   (read file, modify, write back) or sed -i.
   NEVER rewrite a whole file. Make the smallest targeted edit possible (a short
   python script under 25 lines that replaces one function or a few lines).
4. Do NOT run the full test suite; it is too slow. You may run single test files.
5. When your fix is complete, reply with a bash block containing only: submit
6. You have at most {max_turns} commands. Be economical.

FORMAT EXAMPLE — your reply must look exactly like this:
Plan: I will look for the config handling.

```bash
grep -rn "autodoc_typehints" sphinx/ext/autodoc/__init__.py | head -20
```

TASK:
{problem}
"""

CMD_WORDS = ("ls", "cat", "grep", "sed", "find", "python3", "python", "git",
             "head", "tail", "rg", "awk", "echo", "submit", "cd", "wc", "diff")

# Paper-2 existence check (PAPER2-DESIGN §8.1). Shipped AGENTS.md block,
# `metatron context setup` pr gate, kb=context — verbatim from
# metatron/context_setup.py::_ROOT_BLOCK["pr"] at 0.11.0.
AGENTS_BLOCK = """\
<!-- METATRON:START (managed by metatron context setup — safe to edit inside) -->
## Codebase conventions via Metatron (files) — consult FIRST

This repo's conventions ("decisions") live as Open Knowledge Format markdown under
`context/decisions/`. In a monorepo each app has its own `context/`; use the one
**nearest** the files you are touching.

**Before you Read, Grep, Glob, or Edit code in an area — and before proposing an
implementation — first read the relevant files in the nearest `context/decisions/`
and follow them.** State that you consulted them; do not rediscover conventions
manually until you have.

When you find a durable convention not already captured, **author it as a decision
on your working branch**: a new OKF file in the nearest `context/decisions/` (see the
`context-okf-llm-ingest` skill in `.roo/skills/`). The review gate is `pr`: the
human review of your pull request is the curation act, so decision changes reach
the default branch only through a reviewed PR — never push them there directly.
`context/candidate/` remains available as optional staging for proposals not yet
ready for review; content there is never authoritative.
<!-- METATRON:END -->
"""

# v2 contract — shipped in metatron 0.11.1 (PR #116): consultation means opening
# the files, not listing the directory. Condition files-v2 uses this text.
AGENTS_BLOCK_V2 = AGENTS_BLOCK.replace(
    """**Before you Read, Grep, Glob, or Edit code in an area — and before proposing an
implementation — first read the relevant files in the nearest `context/decisions/`
and follow them.** State that you consulted them; do not rediscover conventions
manually until you have.""",
    """**Before you Read, Grep, Glob, or Edit code in an area — and before proposing an
implementation — first read the contents of the relevant files in the nearest
`context/decisions/` and follow them.** Open the files themselves — listing the
directory is not consulting. State that you consulted them; do not rediscover conventions
manually until you have.""")
assert AGENTS_BLOCK_V2 != AGENTS_BLOCK

# Contract iteration (product side-project): CONDITION=files-vN with a matching
# pilot/contracts/files-vN.md overrides the block text (prompt + on-disk AGENTS.md).
_contract_file = ROOT / "pilot" / "contracts" / f"{CONDITION}.md"
CONTRACT_TEXT = (_contract_file.read_text() if _contract_file.exists()
                 else AGENTS_BLOCK_V2 if CONDITION == "files-v2" else AGENTS_BLOCK)


def setup_files(repo_dir, name):
    """Write the shipped Metatron layout into the checkout: context.md entry
    point (intent + decision index), sharded context/decisions/*.md (one OKF
    file per seed `### topic` section), AGENTS.md with the shipped block.
    Content = frozen Paper 1 E-arm seed, delivery = files (nothing injected)."""
    seed = (SEEDS / name / "context.md").read_text()
    parts = re.split(r"\n(?=### )", seed)
    dec_dir = repo_dir / "context" / "decisions"
    dec_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for p in parts[1:]:
        title = p.splitlines()[0].lstrip("# ").strip()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        (dec_dir / f"{slug}.md").write_text(
            f"---\ntype: Metatron Decision\nscope: {name}\nconfidence: high\n---\n\n{p.strip()}\n")
        index.append(f"- `context/decisions/{slug}.md` — {title}")
    hint = ("open and read the relevant files before editing code — filenames alone are not enough"
            if CONDITION == "files-v2" else "read the relevant ones before editing code")
    entry = (parts[0].strip() + f"\n\nCanonical decisions ({hint}):\n\n"
             + "\n".join(index) + "\n")
    (repo_dir / "context.md").write_text(entry)
    (repo_dir / "AGENTS.md").write_text(CONTRACT_TEXT)


CTX_READ_RE = re.compile(r"^(cat|ls|grep|head|tail|find|sed)\b[^\n]*(context\.md|context/|AGENTS\.md)", re.M)
DEEP_READ_RE = re.compile(r"^(cat|head|tail|sed)\b[^\n]*(context\.md|context/decisions/\S+\.md)", re.M)


def consultation(log):
    """First-class Paper 2 metric (pilot version; frozen detector comes at
    prereg2 freeze). Returns dict: read at any turn, first read turn, and
    whether the first read preceded the first file-modifying command."""
    edit_re = re.compile(r"sed -i|>\s*\S|EOF")
    first_read = first_edit = None
    for rec in log["turns"]:
        cmd = rec.get("cmd") or ""
        if first_read is None and CTX_READ_RE.search(cmd):
            first_read = rec["turn"]
        if first_edit is None and edit_re.search(cmd):
            first_edit = rec["turn"]
    deep = next((r["turn"] for r in log["turns"] if DEEP_READ_RE.search(r.get("cmd") or "")), None)
    return {"consulted": first_read is not None, "first_read_turn": first_read,
            "deep_read": deep is not None, "deep_read_turn": deep,
            "read_before_edit": first_read is not None and (first_edit is None or first_read < first_edit)}


def _anthropic_client():
    import anthropic
    key = None
    for line in Path(os.environ.get("RCL_ENV_FILE", ".env")).read_text().splitlines():
        if line.startswith("ANTHROPIC_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"')
    return anthropic.Anthropic(api_key=key)


_CLIENT = None


def chat_anthropic(messages):
    """Frontier executor. Same scaffold: system prompt + alternating turns.
    No sampling params (removed on Opus 4.8); thinking off by default."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = _anthropic_client()
    system = messages[0]["content"]
    resp = _CLIENT.messages.create(
        model=FRONTIER_MODEL, max_tokens=2048,
        system=system, messages=messages[1:],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text, resp.usage.input_tokens, resp.usage.output_tokens


def chat(messages):
    if EXECUTOR == "anthropic":
        return chat_anthropic(messages)
    body = json.dumps({
        "model": MODEL, "messages": messages, "stream": False, "think": False,
        "options": {"temperature": 0, "num_ctx": 32768, "num_predict": 2048},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    msg = resp["message"]
    if not msg.get("content"):
        dbg = {k: str(v)[:200] for k, v in msg.items()}
        print(f"  [empty content] msg={dbg} done_reason={resp.get('done_reason')} eval={resp.get('eval_count')}", flush=True)
    return msg["content"], resp.get("prompt_eval_count", 0), resp.get("eval_count", 0)


def extract_cmd(text):
    m = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", text, re.S)
    if m:
        return m[-1].strip()
    # fallback: last paragraph that starts with a shell-ish word (small models
    # sometimes drop the fence; frontier models never hit this path)
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    for p in reversed(paras):
        if p.split()[0].rstrip(":") in CMD_WORDS:
            return p
    return None


def run(instance, repo_dir):
    t0 = time.time()
    log = {"instance_id": instance["instance_id"],
           "model": FRONTIER_MODEL if EXECUTOR == "anthropic" else MODEL,
           "executor": EXECUTOR, "condition": CONDITION,
           "turns": [], "prompt_tokens": 0, "completion_tokens": 0}
    problem = " ".join(instance["problem_statement"].split())[:6000]
    ctx_file = CONTEXT_DIR / (instance["repo"].split("/")[1] + ".md")
    ctx_block = ""
    if CONDITION == "treatment" and ctx_file.exists():
        ctx_block = ("\nREPOSITORY CONTEXT — operating knowledge of this repository. "
                     "Consult it before planning; it constrains where fixes belong:\n\n"
                     + ctx_file.read_text() + "\n")
        log["context_file"] = str(ctx_file)
    elif CONDITION.startswith("files") and CONDITION != "files-bare":
        ctx_block = "\nAGENTS.md (repository instructions):\n\n" + CONTRACT_TEXT + "\n"
    # files-bare: artifacts exist in the tree, prompt says nothing (strict
    # "unprompted" reading of the roadmap existence check).
    problem = ctx_block + "TASK:\n" + problem if ctx_block else problem
    messages = [{"role": "system", "content": SYSTEM.format(max_turns=MAX_TURNS, problem=problem)},
                {"role": "user", "content": "Begin. Explore the code, make the fix, then submit."}]
    submitted, invalid = False, 0
    for turn in range(MAX_TURNS):
        try:
            reply, pt, ct = chat(messages)
        except Exception as e:
            log["error"] = f"ollama: {e}"; break
        log["prompt_tokens"] += pt; log["completion_tokens"] += ct
        cmd = extract_cmd(reply)
        rec = {"turn": turn, "reply_head": reply[:400], "cmd": cmd}
        if cmd is None:
            invalid += 1
            truncated = "```" in reply and not re.search(r"```(?:bash|sh|shell)?\n.*?```", reply, re.S)
            rec["result"] = "TRUNCATED" if truncated else "NO_COMMAND"
            nudge = ("Your command was cut off before the closing ```. Issue a SHORTER command — "
                     "edit only a few lines at a time." if truncated else
                     "Your reply had no bash code block. Reply with exactly one bash block.")
            messages += [{"role": "assistant", "content": reply},
                         {"role": "user", "content": nudge}]
            log["turns"].append(rec)
            if invalid >= 3: log["error"] = "3 invalid replies"; break
            continue
        if cmd.strip() == "submit":
            d = subprocess.run(["git", "diff", "--stat"], cwd=repo_dir, capture_output=True, text=True).stdout
            if not d.strip() and not log.get("empty_submit_nudged"):
                log["empty_submit_nudged"] = True
                rec["result"] = "SUBMIT_EMPTY_NUDGED"; log["turns"].append(rec)
                messages += [{"role": "assistant", "content": reply},
                             {"role": "user", "content": "git diff is empty — your edits did not apply. "
                              "Run `git diff` to check, re-apply a minimal edit, verify, then submit."}]
                continue
            submitted = True; rec["result"] = "SUBMIT"; log["turns"].append(rec); break
        p = subprocess.run(["bash", "-c", cmd], cwd=repo_dir, capture_output=True,
                           text=True, timeout=CMD_TIMEOUT + 30, errors="replace",
                           env={"PATH": "/usr/bin:/bin:/usr/sbin:/opt/homebrew/bin", "HOME": str(WORK)},
                           ) if True else None
        out = (p.stdout + p.stderr)[:OUT_CAP]
        rec["exit"] = p.returncode; rec["out_head"] = out[:300]
        log["turns"].append(rec)
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"exit={p.returncode}\n{out}"}]
    patch = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True).stdout
    gold_files = set(re.findall(r"^diff --git a/(\S+)", instance["patch"], re.M))
    edit_files = set(re.findall(r"^diff --git a/(\S+)", patch, re.M))
    log.update({
        "submitted": submitted, "n_turns": len(log["turns"]),
        "invalid_replies": invalid, "patch_bytes": len(patch),
        "gold_files": sorted(gold_files), "edited_files": sorted(edit_files),
        "file_overlap": sorted(gold_files & edit_files), "wall_s": round(time.time() - t0, 1),
    })
    (LOGS / f"{instance['instance_id']}.patch").write_text(patch)
    (LOGS / f"{instance['instance_id']}.json").write_text(json.dumps(log, indent=1))
    return log


def main():
    import pandas as pd
    df = pd.read_parquet(DATA).set_index("instance_id")
    LOGS.mkdir(parents=True, exist_ok=True); WORK.mkdir(parents=True, exist_ok=True)
    cache = WORK / "cache"; cache.mkdir(exist_ok=True)
    only = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else PILOT_INSTANCES
    for iid in only:
        inst = df.loc[iid].to_dict(); inst["instance_id"] = iid
        repo = inst["repo"]; name = repo.split("/")[1]
        bare = cache / f"{name}.git"
        if not bare.exists():
            subprocess.run(["git", "clone", "--bare", f"https://github.com/{repo}.git", str(bare)], check=True)
        rd = WORK / iid
        if rd.exists(): subprocess.run(["rm", "-rf", str(rd)])
        subprocess.run(["git", "clone", "--shared", str(bare), str(rd)], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-q", inst["base_commit"]], cwd=rd, check=True, capture_output=True)
        if CONDITION.startswith("files"):
            setup_files(rd, name)
        print(f"=== {iid} ===", flush=True)
        log = run(inst, rd)
        if CONDITION.startswith("files"):
            log.update(consultation(log))
            (LOGS / f"{iid}.json").write_text(json.dumps(log, indent=1))
        keys = ["submitted", "n_turns", "invalid_replies", "patch_bytes", "file_overlap", "wall_s"]
        keys += ["consulted", "deep_read", "first_read_turn", "read_before_edit"] if CONDITION.startswith("files") else []
        print(json.dumps({k: log.get(k) for k in keys}), flush=True)


if __name__ == "__main__":
    main()
