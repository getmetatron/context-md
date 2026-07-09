#!/usr/bin/env python3
"""Power simulation for the RCL transfer study (PREREGISTRATION §8).

Design: N (A,B) pairs; per pair, r reps of B under control and r under treatment.
Per-pair heterogeneity via Beta-distributed baselines. Paired permutation test on
mean per-pair success-rate difference (10k sims per cell would be slow; 2k sims,
1k permutations is adequate for MDE bracketing).

Two metric regimes:
  resolve  — low baseline (floor): p0 in {.05, .10, .20}; treatment adds delta
  process  — wrong-file-edit rate (high baseline, from pilot: 0.8); treatment SUBTRACTS delta
"""
import numpy as np

rng = np.random.default_rng(42)
N_SIMS, N_PERM, ALPHA = 2000, 1000, 0.05


def simulate_power(n_pairs, reps, p0, delta, kappa=10):
    """kappa: Beta concentration (heterogeneity across pairs; lower = more spread)."""
    hits = 0
    for _ in range(N_SIMS):
        base = rng.beta(p0 * kappa, (1 - p0) * kappa, n_pairs)
        treat = np.clip(base + delta, 0, 1)
        c = rng.binomial(reps, base) / reps
        t = rng.binomial(reps, treat) / reps
        d = t - c
        obs = d.mean()
        # sign-flip permutation test (paired)
        signs = rng.choice([-1, 1], size=(N_PERM, n_pairs))
        perm = (signs * d).mean(axis=1)
        p = (np.abs(perm) >= abs(obs)).mean()
        hits += p < ALPHA
    return hits / N_SIMS


def mde(n_pairs, reps, p0, direction=+1, target=0.8):
    """Smallest |delta| reaching target power, 2.5pp grid."""
    for dd in np.arange(0.025, 0.60, 0.025):
        if simulate_power(n_pairs, reps, p0, direction * dd) >= target:
            return dd
    return float("nan")


if __name__ == "__main__":
    print(f"sims={N_SIMS} perms={N_PERM} alpha={ALPHA} power_target=0.8 kappa=10\n")
    print("== RESOLVE regime (delta = improvement in B resolve rate) ==")
    print(f"{'pairs':>6} {'reps':>5} {'p0':>5} {'MDE':>7}")
    for n in (15, 25, 40):
        for reps in (3, 5):
            for p0 in (0.05, 0.10, 0.20):
                print(f"{n:>6} {reps:>5} {p0:>5.2f} {mde(n, reps, p0):>7.3f}", flush=True)
    print("\n== PROCESS regime (delta = reduction in wrong-file-edit rate, p0=0.8) ==")
    for n in (15, 25, 40):
        for reps in (3, 5):
            print(f"{n:>6} {reps:>5} {0.80:>5.2f} {mde(n, reps, 0.80, direction=-1):>7.3f}", flush=True)
