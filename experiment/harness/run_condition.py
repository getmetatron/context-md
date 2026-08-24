#!/usr/bin/env python3
"""Confirmatory condition runner (PREREGISTRATION §2, §4).

Usage:
  run_condition.py --condition A|B|C|D|E|F|G --instances id1,id2 --rep 1 [--oracle]

Conditions (frozen §2):
  A frontier none          B local none
  C frontier emergent      D local emergent
  E local seeded(frontier) F local seeded(local)   G local seeded(human)

Outputs per run:
  runs/<cond>/rep<k>/<instance>.json        episode log (turns, tokens, learning, promotions)
  runs/<cond>/rep<k>/predictions.jsonl      swebench-format predictions (appended)
  runs/<cond>/rep<k>/context/<repo>.md      the evolving context store (emergent arms)

Leakage guards enforced here (§5): gold patch and hidden tests never enter
executor or learning prompts (oracle arm A-side excepted, flagged in the log).
"""
from __future__ import annotations

import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from templates import SYSTEM, CONTEXT_BLOCK, LEARNING_PROMPT, ORACLE_SUFFIX, CONTEXT_TOKEN_CAP
from templates_p2 import CONTRACT_BLOCK_P2, consultation, write_context_files
from promote import promote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "swebench_verified.parquet"
SEEDS = ROOT / "seeds"
MAX_TURNS = 20
CMD_TIMEOUT = 90
OUT_CAP = 3000
OLLAMA_URL = "http://localhost:11434/api/chat"
LOCAL_MODEL = "gemma4:e4b"
FRONTIER_MODEL = "claude-opus-4-8"

COND = {  # executor, context_mode, seed_author
    "A": ("frontier", "none", None), "B": ("local", "none", None),
    "C": ("frontier", "emergent", None), "D": ("local", "emergent", None),
    "E": ("local", "seeded", "frontier"), "F": ("local", "seeded", "local"),
    "G": ("local", "seeded", "human"),
    # Paper 2 delivery arms (PREREGISTRATION-PAPER2 §1): content = frontier seed,
    # delivery = files on disk + shipped 0.12.0 contract in the prompt. Arm I
    # (injection ceiling) is condition E; arm B is condition B.
    "FILE": ("local", "file", "frontier"), "SHARD": ("local", "sharded", "frontier"),
}
REPO_NAME = {"django/django": "django", "sphinx-doc/sphinx": "sphinx",
             "pydata/xarray": "xarray", "sympy/sympy": "sympy",
             "scikit-learn/scikit-learn": "scikit-learn",
             "matplotlib/matplotlib": "matplotlib", "astropy/astropy": "astropy",
             "pytest-dev/pytest": "pytest"}


# ---------- executors ----------

def chat_local(messages, seed):
    import urllib.request
    body = json.dumps({"model": LOCAL_MODEL, "messages": messages, "stream": False,
                       "think": False,
                       "options": {"temperature": 0, "seed": seed,
                                   "num_ctx": 32768, "num_predict": 2048}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    return (resp["message"]["content"], resp.get("prompt_eval_count", 0),
            resp.get("eval_count", 0))


_CLIENT = None

def chat_frontier(messages, seed):
    global _CLIENT
    if _CLIENT is None:
        import anthropic
        key = None
        # Artifact: read the key from the environment. A local .env is honored as
        # a fallback so the original author workflow still works.
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            env = Path(os.environ.get("RCL_ENV_FILE", ".env"))
            if env.exists():
                for line in env.read_text().splitlines():
                    if line.startswith("ANTHROPIC_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"')
        if not key:
            raise SystemExit("set ANTHROPIC_API_KEY (or RCL_ENV_FILE) to use the frontier executor")
        _CLIENT = anthropic.Anthropic(api_key=key)
    resp = _CLIENT.messages.create(model=FRONTIER_MODEL, max_tokens=2048,
                                   system=messages[0]["content"], messages=messages[1:])
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text, resp.usage.input_tokens, resp.usage.output_tokens


# ---------- context store (§4.1) ----------

def truncate_context(md: str, cap_tokens: int = CONTEXT_TOKEN_CAP) -> tuple[str, bool]:
    """Approximate tokens as words/0.75. Truncate Evolved Context oldest-first;
    Intent/Constraints never truncated. Returns (text, truncated?)."""
    if len(md.split()) * 4 // 3 <= cap_tokens:
        return md, False
    m = re.split(r"(^## Evolved Context\s*$)", md, flags=re.M)
    if len(m) < 3:
        return md, False  # no ledger to truncate
    head, marker, ledger = m[0], m[1], "".join(m[2:])
    entries = [e for e in ledger.splitlines() if e.strip()]
    while entries and (len((head + marker + "\n".join(entries)).split()) * 4 // 3) > cap_tokens:
        entries.pop(0)  # oldest-first
    return head + marker + "\n" + "\n".join(entries) + "\n", True


def load_context(cond, rep_dir, repo, seed_author):
    if cond in ("A", "B"):
        return None
    if COND[cond][1] == "seeded":
        src = {"frontier": SEEDS / repo / "context.md",
               "local": SEEDS / f"{repo}-local" / "context.md",
               "human": SEEDS / f"{repo}-human" / "context.md"}[seed_author]
        return src.read_text() if src.exists() else None
    # emergent: accumulating per-repo store under the rep dir
    store = rep_dir / "context" / f"{repo}.md"
    if not store.exists():
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text("# Repository Context\n## Intent\n(accumulating store — emergent arm)\n"
                         "## Constraints\n## Evolved Context\n")
    return store.read_text()


def append_learnings(rep_dir, repo, lessons):
    store = rep_dir / "context" / f"{repo}.md"
    ts = time.strftime("%Y-%m-%d")
    with store.open("a") as f:
        for l in lessons:
            f.write(f"- [{ts}] {l}\n")


# ---------- agent loop (scaffold identical to pilot, frozen) ----------

CMD_WORDS = ("ls", "cat", "grep", "sed", "find", "python3", "python", "git",
             "head", "tail", "rg", "awk", "echo", "submit", "cd", "wc", "diff")


def extract_cmd(text):
    m = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", text, re.S)
    if m:
        return m[-1].strip()
    for p in reversed([p.strip() for p in text.split("\n\n") if p.strip()]):
        if p.split()[0].rstrip(":") in CMD_WORDS:
            return p
    return None


def run_episode(inst, repo_dir, chat, seed, context_md, log, contract=False):
    problem = " ".join(inst["problem_statement"].split())[:6000]
    ctx_block = ""
    if contract:
        # Paper 2 F/S arms: knowledge stays on disk; the prompt carries only the
        # shipped consult-first contract (mimics AGENTS.md auto-loading).
        ctx_block = CONTRACT_BLOCK_P2 + "\n"
    elif context_md:
        ctx_text, truncated = truncate_context(context_md)
        ctx_block = CONTEXT_BLOCK.format(context_md=ctx_text) + "\n"
        log["context_truncated"] = truncated
        log["context_words"] = len(ctx_text.split())
    messages = [{"role": "system", "content": SYSTEM.format(
                    max_turns=MAX_TURNS, context_block=ctx_block, problem=problem)},
                {"role": "user", "content": "Begin. Explore the code, make the fix, then submit."}]
    submitted, invalid, transcript = False, 0, []
    for turn in range(MAX_TURNS):
        try:
            reply, pt, ct = chat(messages, seed)
        except Exception as e:
            log["error"] = f"executor: {e}"; break
        log["prompt_tokens"] += pt; log["completion_tokens"] += ct
        cmd = extract_cmd(reply)
        rec = {"turn": turn, "cmd": cmd}
        if cmd is None:
            invalid += 1
            truncd = "```" in reply and not re.search(r"```(?:bash|sh|shell)?\n.*?```", reply, re.S)
            nudge = ("Your command was cut off before the closing ```. Issue a SHORTER command."
                     if truncd else "Your reply had no bash code block. Reply with exactly one bash block.")
            messages += [{"role": "assistant", "content": reply}, {"role": "user", "content": nudge}]
            log["turns"].append(rec)
            if invalid >= 3: log["error"] = "3 invalid replies"; break
            continue
        if cmd.strip() == "submit":
            d = subprocess.run(["git", "diff", "--stat"], cwd=repo_dir,
                               capture_output=True, text=True).stdout
            if not d.strip() and not log.get("empty_submit_nudged"):
                log["empty_submit_nudged"] = True
                messages += [{"role": "assistant", "content": reply},
                             {"role": "user", "content": "git diff is empty — your edits did not apply. "
                              "Run `git diff` to check, re-apply a minimal edit, verify, then submit."}]
                log["turns"].append(rec); continue
            submitted = True; log["turns"].append(rec); break
        try:
            p = subprocess.run(["bash", "-c", cmd], cwd=repo_dir, capture_output=True,
                               text=True, timeout=CMD_TIMEOUT + 30, errors="replace")
            out = (p.stdout + p.stderr)[:OUT_CAP]
            rc = p.returncode
        except subprocess.TimeoutExpired:
            out = f"TIMEOUT: command exceeded {CMD_TIMEOUT + 30}s and was killed. Use a faster command."
            rc = 124
        rec["exit"] = rc
        transcript.append(f"$ {cmd}\n(exit {rc}) {out[:500]}")
        log["turns"].append(rec)
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"exit={rc}\n{out}"}]
    patch = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True).stdout
    log["submitted"] = submitted
    log["patch_bytes"] = len(patch)
    return patch, "\n".join(transcript)


def learning_step(chat, seed, transcript, patch, oracle_gold=None):
    prompt = LEARNING_PROMPT.format(transcript=transcript[-8000:], patch=patch[:4000])
    if oracle_gold:
        prompt += ORACLE_SUFFIX.format(gold_patch=oracle_gold[:4000])
    reply, _, _ = chat([{"role": "system", "content": "You extract durable engineering lessons."},
                        {"role": "user", "content": prompt}], seed)
    if "NONE" in reply.split("\n")[0].upper() and "-" not in reply:
        return []
    return [l.lstrip("- ").strip() for l in reply.splitlines()
            if l.strip().startswith("- ")][:3]


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=list(COND))
    ap.add_argument("--instances", required=True)
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--oracle", action="store_true",
                    help="oracle-taught arm (§4.3): learning step sees gold patch. Labeled, never pooled.")
    ap.add_argument("--no-learning", action="store_true",
                    help="§4.7 pair B-side: consult the store but discard learning output (no chaining).")
    ap.add_argument("--skip-existing", action="store_true",
                    help="resume: skip instances whose episode log already exists (operational only; all Paper 2 arms are order-independent)")
    ap.add_argument("--run-dir", default=None,
                    help="override run directory (e.g. runs/D/pair_X_Y/rep1) for pair-scoped stores")
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_parquet(DATA).set_index("instance_id")
    executor, ctx_mode, seed_author = COND[args.condition]
    chat = chat_frontier if executor == "frontier" else chat_local
    rep_dir = (Path(args.run_dir) if args.run_dir else
               ROOT / "runs" / (args.condition + ("_oracle" if args.oracle else "")) / f"rep{args.rep}")
    rep_dir.mkdir(parents=True, exist_ok=True)
    cache = ROOT / "pilot" / "work" / "cache"
    preds = rep_dir / "predictions.jsonl"

    for iid in args.instances.split(","):
        if args.skip_existing and (rep_dir / f"{iid}.json").exists():
            continue
        inst = df.loc[iid].to_dict(); inst["instance_id"] = iid
        repo = REPO_NAME[inst["repo"]]
        bare = cache / f"{repo}.git"
        if not bare.exists():
            subprocess.run(["git", "clone", "--bare",
                            f"https://github.com/{inst['repo']}.git", str(bare)], check=True)
        wd = rep_dir / "work" / iid
        if wd.exists(): subprocess.run(["rm", "-rf", str(wd)])
        wd.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--shared", str(bare), str(wd)], check=True)
        subprocess.run(["git", "checkout", "-q", inst["base_commit"]], cwd=wd, check=True)

        log = {"instance_id": iid, "condition": args.condition, "rep": args.rep,
               "executor": executor, "context_mode": ctx_mode, "oracle": args.oracle,
               "seed": args.rep, "turns": [], "prompt_tokens": 0, "completion_tokens": 0,
               "t0": time.time()}
        if ctx_mode in ("file", "sharded"):
            seed_text = (SEEDS / repo / "context.md").read_text()
            log["context_files_written"] = write_context_files(wd, seed_text, ctx_mode)
            context_md, contract = None, True
        else:
            context_md, contract = load_context(args.condition, rep_dir, repo, seed_author), False
        patch, transcript = run_episode(inst, wd, chat, args.rep, context_md, log,
                                        contract=contract)
        if ctx_mode in ("file", "sharded"):
            log.update(consultation(log["turns"]))

        if ctx_mode == "emergent" and not args.no_learning:
            gold = inst["patch"] if args.oracle else None   # §4.3 A-side only
            lessons = learning_step(chat, args.rep, transcript, patch, oracle_gold=gold)
            promoted = []
            verifier = lambda p: chat([{"role": "system", "content": "Answer YES or NO only."},
                                       {"role": "user", "content": p}], args.rep)[0]
            for l in lessons:
                r = promote(l, verifier, log_path=rep_dir / "promotions.jsonl")
                if r.promoted: promoted.append(l)
            if promoted: append_learnings(rep_dir, repo, promoted)
            log["lessons_raw"] = lessons; log["lessons_promoted"] = promoted

        log["wall_s"] = round(time.time() - log.pop("t0"), 1)
        (rep_dir / f"{iid}.json").write_text(json.dumps(log, indent=1))
        with preds.open("a") as f:
            f.write(json.dumps({"instance_id": iid,
                                "model_name_or_path": f"{args.condition}-rep{args.rep}",
                                "model_patch": patch}) + "\n")
        subprocess.run(["rm", "-rf", str(wd)])
        print(f"{iid}: submitted={log.get('submitted')} patch={log['patch_bytes']}b "
              f"lessons={len(log.get('lessons_promoted', []))}", flush=True)


if __name__ == "__main__":
    main()
