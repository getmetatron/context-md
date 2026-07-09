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
CONDITION = os.environ.get("CONDITION", "control")  # control | treatment
EXECUTOR = os.environ.get("EXECUTOR", "ollama")     # ollama | anthropic
CONTEXT_DIR = ROOT / "pilot" / "context"            # <reponame>.md, injected in treatment only
LOGS = ROOT / "pilot" / "logs" / (CONDITION if EXECUTOR == "ollama" else f"{CONDITION}_{EXECUTOR}")
FRONTIER_MODEL = "claude-opus-4-8"
OLLAMA = "http://localhost:11434/api/chat"
MODEL = "gemma4:e4b"
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


def _anthropic_client():
    import anthropic
    key = None
    for line in (Path("/Users/pavel/dev/getmetatron/metatron/.env")).read_text().splitlines():
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
        print(f"=== {iid} ===", flush=True)
        log = run(inst, rd)
        print(json.dumps({k: log[k] for k in
              ("submitted", "n_turns", "invalid_replies", "patch_bytes", "file_overlap", "wall_s")}), flush=True)


if __name__ == "__main__":
    main()
