"""Mechanical candidate->decision promotion (PREREGISTRATION §4.4).

A candidate is promoted iff ALL hold:
  1. States a rule/fact about the repository in general terms  (LLM verifier, fixed prompt)
  2. No instance identifier, issue number, or "this task" reference (regex)
  3. No specific line numbers; file/module references allowed      (regex)
  4. <= 60 words                                                   (deterministic)

No human judgment per-item. Every decision is logged. Frozen at prereg-v1;
any change after freeze requires a DEVIATIONS.md entry.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict

# --- deterministic checks (criteria 2-4) ---

INSTANCE_ID_RE = re.compile(
    r"(django__|sphinx-doc__|pydata__|scikit-learn__|sympy__)"   # benchmark ids
    r"|#\d{3,6}\b"                                                # issue numbers
    r"|\bissue\s+\d+"                                             # "issue 1234"
    r"|\b(this|the current|the present)\s+(task|issue|bug|instance|ticket)\b",
    re.I,
)
LINE_NUMBER_RE = re.compile(r"\bline\s+\d+|\bL\d{2,}\b|:\d+\s*$")
MAX_WORDS = 60

VERIFIER_PROMPT = """You are a strict verifier in a research pipeline. Answer with exactly one word: YES or NO.

A "repo-general rule" states a fact, convention, or constraint about a codebase that would apply to MANY future tasks (e.g. "Operations must propagate attrs; the helpers live in core/options.py"). It is NOT repo-general if it describes how one specific bug was fixed, prescribes an edit to specific code ("change X to Y in function Z"), or only makes sense for a single task.

Is the following candidate a repo-general rule or fact?

CANDIDATE:
{candidate}

Answer (YES or NO):"""


@dataclass
class PromotionResult:
    candidate: str
    promoted: bool
    c2_no_instance_refs: bool
    c3_no_line_numbers: bool
    c4_word_count: int
    c4_within_limit: bool
    c1_general_rule: bool | None  # None if deterministic checks already failed
    verifier_raw: str | None
    ts: float


def check_deterministic(candidate: str) -> tuple[bool, bool, int]:
    c2 = not INSTANCE_ID_RE.search(candidate)
    c3 = not LINE_NUMBER_RE.search(candidate)
    c4_words = len(candidate.split())
    return c2, c3, c4_words


def verify_general(candidate: str, llm_call) -> tuple[bool, str]:
    """llm_call: fn(prompt:str)->str. Fixed prompt, temperature-0 semantics
    where the backend supports it. The verifier model is recorded in the run log."""
    raw = llm_call(VERIFIER_PROMPT.format(candidate=candidate)).strip().upper()
    return raw.startswith("YES"), raw[:40]


def promote(candidate: str, llm_call, log_path=None) -> PromotionResult:
    c2, c3, c4_words = check_deterministic(candidate)
    c4 = c4_words <= MAX_WORDS
    c1, raw = (None, None)
    if c2 and c3 and c4:
        c1, raw = verify_general(candidate, llm_call)
    res = PromotionResult(
        candidate=candidate, promoted=bool(c1) and c2 and c3 and c4,
        c2_no_instance_refs=c2, c3_no_line_numbers=c3,
        c4_word_count=c4_words, c4_within_limit=c4,
        c1_general_rule=c1, verifier_raw=raw, ts=time.time(),
    )
    if log_path:
        with open(log_path, "a") as f:
            f.write(json.dumps(asdict(res)) + "\n")
    return res
