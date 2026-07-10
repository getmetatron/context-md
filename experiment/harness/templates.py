"""Frozen prompt templates (PREREGISTRATION §4.1, §4.2).

Changes after prereg-v1 require DEVIATIONS.md entries.
"""

# §4.1 — consultation mechanics
CONTEXT_TOKEN_CAP = 4000  # hard cap; ledger truncated oldest-first, Intent/Constraints never truncated

CONTEXT_BLOCK = """REPOSITORY CONTEXT — operating knowledge of this repository. Consult it before planning; it constrains where fixes belong:

{context_md}
"""

# Scaffold system prompt — identical across ALL conditions and executors (§2).
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
grep -rn "config_value" src/module.py | head -20
```

{context_block}TASK:
{problem}
"""

# §4.2 — emergent learning step. Inputs: agent's OWN transcript/test output/patch.
# NEVER: gold patch, hidden tests, resolution status (oracle arm excepted, A-side only).
LEARNING_PROMPT = """You just finished working on a task in this repository. Review YOUR OWN work below and extract durable lessons a FUTURE session working on a DIFFERENT task in this repository would otherwise have to re-learn.

Rules for lessons:
- State repo-general rules or facts (conventions, where machinery lives, pitfalls), NOT how you fixed this specific task.
- No issue numbers, no task references, no line numbers. Module/file paths are allowed.
- Each lesson must be 60 words or fewer.
- Most work teaches nothing durable. If nothing generalizes, output exactly: NONE
- Output at most 3 lessons, one per line, each starting with "- ".

YOUR TRANSCRIPT (commands and outputs):
{transcript}

YOUR FINAL PATCH:
{patch}

Durable lessons (or NONE):"""

# Oracle-taught arm (§4.3): additionally shown the gold patch of instance A.
ORACLE_SUFFIX = """

THE ACTUAL FIX THE MAINTAINERS MADE (for reference — extract the general principle it embodies, not the edit itself):
{gold_patch}"""
