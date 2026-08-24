"""Paper 2 additions (PREREGISTRATION-PAPER2 §1, §5). Additive only — nothing in
templates.py (frozen under prereg-v1) is modified. Frozen at prereg2-v1.

CONTRACT_BLOCK_P2 is the shipped `metatron context setup` AGENTS.md root block,
review gate pr, kb=context, verbatim from metatron 0.12.0
(metatron/context_setup.py::_ROOT_BLOCK["pr"]).
"""
import re

CONTRACT_BLOCK_P2 = """\
AGENTS.md (repository instructions):

<!-- METATRON:START (managed by metatron context setup — safe to edit inside) -->
## Repository context — required first step

This repository carries its own operating knowledge: binding conventions
("decisions") as Open Knowledge Format markdown under `context/decisions/`.
Before you explore or edit any code:

1. Run `cat context.md` — it lists the binding conventions and where each one
   lives. In a monorepo, use the `context/` nearest the files you are touching.
2. Open the decision files relevant to your task with
   `cat context/decisions/<topic>.md`. They say where fixes belong and which
   pitfalls to avoid.
3. Only then plan your change — and state which decision files you read.

Reading these files is required, not optional: a change that contradicts a
decision will be rejected in review. Listing the directory is not reading.

To record a durable convention you discovered, add an OKF file under
`context/decisions/` on your working branch (skill: `context-okf-llm-ingest` in
`.roo/skills/`). The review gate is `pr`: it reaches the default branch only
through a human-reviewed pull request — never push decision changes there
directly. `context/candidate/` remains optional staging; content there is never
authoritative.
<!-- METATRON:END -->
"""

# Frozen consultation detector (PREREGISTRATION-PAPER2 §4).
STRICT_READ_RE = re.compile(
    r"^(cat|ls|grep|head|tail|find|sed)\b[^\n]*(context\.md|context/|AGENTS\.md)", re.M)
DEEP_READ_RE = re.compile(
    r"^(cat|head|tail|sed)\b[^\n]*(context\.md|context/decisions/\S+\.md)", re.M)
EDIT_RE = re.compile(r"sed -i|>\s*\S|EOF")


def consultation(turns):
    """turns: list of {"turn": int, "cmd": str|None}. Returns the §4 metrics."""
    first_read = first_edit = deep = None
    for rec in turns:
        cmd = rec.get("cmd") or ""
        if first_read is None and STRICT_READ_RE.search(cmd):
            first_read = rec["turn"]
        if deep is None and DEEP_READ_RE.search(cmd):
            deep = rec["turn"]
        if first_edit is None and EDIT_RE.search(cmd):
            first_edit = rec["turn"]
    return {"consulted": first_read is not None, "first_read_turn": first_read,
            "deep_read": deep is not None, "deep_read_turn": deep,
            "read_before_edit": first_read is not None
                                and (first_edit is None or first_read < first_edit)}


def write_context_files(repo_dir, seed_text, mode):
    """Arm F ('file'): monolith context.md. Arm S ('sharded'): shipped layout —
    context.md index + one OKF file per `### topic` section. Both write AGENTS.md
    (informational; the prompt carries the same contract). Returns file count."""
    (repo_dir / "AGENTS.md").write_text(
        CONTRACT_BLOCK_P2.split("\n", 2)[2])  # strip the prompt label line
    if mode == "file":
        (repo_dir / "context.md").write_text(seed_text)
        return 1
    parts = re.split(r"\n(?=### )", seed_text)
    dec = repo_dir / "context" / "decisions"
    dec.mkdir(parents=True, exist_ok=True)
    index = []
    for p in parts[1:]:
        title = p.splitlines()[0].lstrip("# ").strip()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        (dec / f"{slug}.md").write_text(
            f"---\ntype: Metatron Decision\nconfidence: high\n---\n\n{p.strip()}\n")
        index.append(f"- `context/decisions/{slug}.md` — {title}")
    (repo_dir / "context.md").write_text(
        parts[0].strip() + "\n\nCanonical decisions (open and read the relevant "
        "files before editing code — filenames alone are not enough):\n\n"
        + "\n".join(index) + "\n")
    return 1 + len(parts) - 1
