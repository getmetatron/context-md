#!/usr/bin/env python3
"""Score the 40-episode consultation hand-audit against the frozen detector.

Run after a human has filled the manual_* columns of the blinded audit file.
For each of the three registered constructs (consulted, deep_read,
read_before_edit) it reports Cohen's kappa, raw agreement, the 2x2 confusion
matrix, positive/negative counts, and every disagreement by audit_id.

Degenerate cases are reported, never papered over. Consultation runs at ~97%,
so a 40-episode sample can easily contain very few negative labels. Kappa is
undefined only when expected agreement is 1 and its denominator vanishes; a
constant label from one rater alone can instead yield a defined kappa of zero.
The script always reports raw agreement and the confusion matrix, and the sample
is never altered to make kappa behave.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

METRICS = [("consulted", "manual_consulted", "auto_consulted"),
           ("deep_read", "manual_deep_read", "auto_deep_read"),
           ("read_before_edit", "manual_read_before_edit", "auto_read_before_edit")]
TRUTHY = {"1": 1, "1.0": 1, "y": 1, "yes": 1, "true": 1, "t": 1}
FALSY = {"0": 0, "0.0": 0, "n": 0, "no": 0, "false": 0, "f": 0}
N_AUDIT = 40


def to01(v):
    if pd.isna(v):
        return None
    s = str(v).strip().lower()
    if s in TRUTHY: return 1
    if s in FALSY: return 0
    return None


def cohens_kappa(a, b):
    """Returns (kappa, note). kappa is None when undefined."""
    a, b = np.asarray(a), np.asarray(b)
    n = len(a)
    po = float((a == b).mean())
    # expected agreement under independence of the two raters' marginals
    pe = sum((a == c).mean() * (b == c).mean() for c in (0, 1))
    if np.isclose(pe, 1.0):
        return None, ("undefined: both raters used a single label for every "
                      "episode, so expected agreement is 1.0 and kappa's "
                      "denominator is zero")
    return (po - pe) / (1 - pe), None


def confusion(manual, auto):
    m, a = np.asarray(manual), np.asarray(auto)
    return {"both_positive": int(((m == 1) & (a == 1)).sum()),
            "manual_pos_auto_neg": int(((m == 1) & (a == 0)).sum()),
            "manual_neg_auto_pos": int(((m == 0) & (a == 1)).sum()),
            "both_negative": int(((m == 0) & (a == 0)).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", required=True, help="the filled human audit CSV")
    ap.add_argument("--key", required=True, help="the detector key CSV")
    args = ap.parse_args()

    h = pd.read_csv(args.audit)
    k = pd.read_csv(args.key)
    required_h = {"audit_id", "arm", "instance_id", "repetition", "manual_unclear",
                  "manual_notes", *(m for _, m, _ in METRICS)}
    required_k = {"audit_id", *(a for _, _, a in METRICS)}
    assert required_h <= set(h.columns), f"audit file lacks columns: {sorted(required_h-set(h.columns))}"
    assert required_k <= set(k.columns), f"key file lacks columns: {sorted(required_k-set(k.columns))}"
    assert len(h) == N_AUDIT, f"audit file has {len(h)} rows, expected {N_AUDIT}"
    assert len(k) == N_AUDIT, f"key file has {len(k)} rows, expected {N_AUDIT}"
    expected_ids = {f"A{i:02d}" for i in range(1, N_AUDIT + 1)}
    assert set(h.audit_id) == expected_ids, "audit file does not contain exactly A01-A40"
    assert set(k.audit_id) == expected_ids, "key file does not contain exactly A01-A40"
    df = h.merge(k, on="audit_id", validate="one_to_one")
    assert len(df) == N_AUDIT, "audit/key merge lost rows"
    print(f"audit rows: {len(df)}")

    unclear = df[df.manual_unclear.apply(lambda v: to01(v) == 1)]
    if len(unclear):
        print(f"marked unclear by the labeler: {len(unclear)} "
              f"({', '.join(unclear.audit_id)}) — excluded from kappa, reported separately")

    any_missing = False
    for name, mcol, acol in METRICS:
        print(f"\n=== {name} ===")
        sub = df[~df.audit_id.isin(unclear.audit_id)].copy()
        sub["m"] = sub[mcol].apply(to01)
        sub["a"] = sub[acol].apply(to01)
        if sub.empty:
            any_missing = True
            print("  NOT SCORED: all rows are marked unclear; adjudicate them and re-run.")
            continue
        bad = sub[sub.m.isna()]
        if len(bad):
            any_missing = True
            print(f"  NOT SCORED: {len(bad)} row(s) have no usable manual label "
                  f"({', '.join(bad.audit_id)}). Fill them and re-run.")
            continue
        m, a = sub.m.astype(int).values, sub.a.astype(int).values
        n = len(m)
        po = float((m == a).mean())
        kappa, note = cohens_kappa(m, a)
        cm = confusion(m, a)

        print(f"  n = {n}")
        print(f"  manual  positive {int(m.sum()):3}   negative {int((1-m).sum()):3}")
        print(f"  auto    positive {int(a.sum()):3}   negative {int((1-a).sum()):3}")
        print(f"  raw agreement    {po:.4f}  ({int((m==a).sum())}/{n})")
        if kappa is None:
            print(f"  Cohen's kappa    UNDEFINED — {note}")
            print("                   Report raw agreement and the confusion matrix "
                  "instead; do not resample to obtain a defined kappa.")
        else:
            print(f"  Cohen's kappa    {kappa:.4f}")
            if min(m.sum(), n - m.sum()) < 3 or min(a.sum(), n - a.sum()) < 3:
                print("                   CAUTION: one label is very rare in this "
                      "sample, so kappa is unstable; raw agreement is the more "
                      "stable summary here.")
        print("  confusion (manual x auto):")
        print(f"    both positive        {cm['both_positive']:3}")
        print(f"    manual + / auto -    {cm['manual_pos_auto_neg']:3}")
        print(f"    manual - / auto +    {cm['manual_neg_auto_pos']:3}")
        print(f"    both negative        {cm['both_negative']:3}")

        dis = sub[sub.m != sub.a]
        if len(dis):
            print(f"  disagreements ({len(dis)}):")
            for r in dis.itertuples(index=False):
                note_txt = "" if pd.isna(r.manual_notes) else f" — {r.manual_notes}"
                print(f"    {r.audit_id}  {r.arm}/{r.instance_id} rep{r.repetition}: "
                      f"manual={int(r.m)} auto={int(r.a)}{note_txt}")
        else:
            print("  disagreements: none")

    if any_missing:
        raise SystemExit("\nIncomplete: some manual labels are missing (see above).")
    print("\nAudit scored. Report raw agreement alongside kappa, and state "
          "explicitly wherever kappa is undefined or unstable.")


if __name__ == "__main__":
    main()
