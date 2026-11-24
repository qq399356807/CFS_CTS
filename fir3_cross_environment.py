#!/usr/bin/env python3
"""FIR-3 cross-environment response-kernel stability simulation.

Synthetic methodological validation only. Compares a shared target kernel,
an environment-drifting target kernel, and a shared no-interaction control.
The unit of resampling is a complete randomized block within each environment.
"""
from __future__ import annotations
import argparse
import json
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd

ENVIRONMENTS = ("env_1", "env_2", "env_3", "env_4")
MECHANISMS = ("stable_target", "drifting_target", "stable_negative_control")
ETA_STABLE = 0.10
ETA_DRIFT = (0.10, 0.16, 0.22, 0.28)
GAMMA_MARGIN = 0.10
DEFAULT_BLOCKS = 60
DEFAULT_REPEATS = 10
DEFAULT_BOOTSTRAP = 5000


def cell_probabilities(df: pd.DataFrame) -> np.ndarray:
    """Return p[e,a,b]; every environment must contain all four input cells."""
    out = np.full((len(ENVIRONMENTS), 2, 2), np.nan, dtype=float)
    for ei, env in enumerate(ENVIRONMENTS):
        sub = df[df.environment == env]
        for a in (0, 1):
            for b in (0, 1):
                cell = sub[(sub.A_t == a) & (sub.B_t == b)]
                if len(cell) == 0:
                    raise ValueError(f"Missing common-support cell: {env}, A={a}, B={b}")
                out[ei, a, b] = cell.C_next.mean()
    return out


def kernel_discrepancies(p: np.ndarray) -> tuple[float, float]:
    """Gamma=max and Omega=mean pairwise TV discrepancy.

    For Bernoulli outcomes, total variation distance equals the absolute
    difference between success probabilities.
    """
    distances = []
    for i, j in combinations(range(p.shape[0]), 2):
        distances.extend(np.abs(p[i] - p[j]).ravel().tolist())
    return float(np.max(distances)), float(np.mean(distances))


def psi_by_environment(p: np.ndarray) -> list[float]:
    return [float(p[e, 1, 1] - p[e, 1, 0] - p[e, 0, 1] + p[e, 0, 0])
            for e in range(p.shape[0])]


def generate_data(seed: int, blocks: int, repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    eta_by_mechanism = {
        "stable_target": [ETA_STABLE] * len(ENVIRONMENTS),
        "drifting_target": list(ETA_DRIFT),
        "stable_negative_control": [ETA_STABLE] * len(ENVIRONMENTS),
    }
    for mechanism in MECHANISMS:
        for ei, env in enumerate(ENVIRONMENTS):
            eta = eta_by_mechanism[mechanism][ei]
            for block in range(blocks):
                cells = [(a, b) for a in (0, 1) for b in (0, 1) for _ in range(repeats)]
                rng.shuffle(cells)
                for trial, (a, b) in enumerate(cells):
                    noise = int(rng.random() < eta)
                    y = (a ^ noise) if mechanism == "stable_negative_control" else (a ^ b ^ noise)
                    rows.append((mechanism, env, ei, block, trial, a, b, int(y), noise, eta))
    return pd.DataFrame(rows, columns=[
        "mechanism", "environment", "environment_index", "block",
        "trial_in_block", "A_t", "B_t", "C_next", "N_t", "eta",
    ])


def block_bootstrap(df: pd.DataFrame, rng: np.random.Generator, n_boot: int):
    """Resample complete blocks independently within each environment."""
    env_blocks = {}
    for env in ENVIRONMENTS:
        sub = df[df.environment == env]
        blocks = sorted(sub.block.unique())
        if len(blocks) < 2:
            raise ValueError("At least two blocks per environment are required.")
        env_blocks[env] = [
            sub[sub.block == block][["A_t", "B_t", "C_next"]].to_numpy(dtype=int)
            for block in blocks
        ]
    gamma = np.empty(n_boot, dtype=float)
    omega = np.empty(n_boot, dtype=float)
    for rep in range(n_boot):
        p = np.empty((len(ENVIRONMENTS), 2, 2), dtype=float)
        for ei, env in enumerate(ENVIRONMENTS):
            blocks = env_blocks[env]
            draw = rng.integers(0, len(blocks), size=len(blocks))
            sample = np.concatenate([blocks[k] for k in draw], axis=0)
            for a in (0, 1):
                for b in (0, 1):
                    mask = (sample[:, 0] == a) & (sample[:, 1] == b)
                    if not np.any(mask):
                        raise RuntimeError("Bootstrap replicate lost a randomized cell.")
                    p[ei, a, b] = sample[mask, 2].mean()
        gamma[rep], omega[rep] = kernel_discrepancies(p)
    return gamma, omega


def analyze_mechanism(df: pd.DataFrame, seed: int, n_boot: int, gamma_margin: float) -> dict:
    p = cell_probabilities(df)
    gamma_hat, omega_hat = kernel_discrepancies(p)
    boot_gamma, boot_omega = block_bootstrap(df, np.random.default_rng(seed), n_boot)
    gamma_ci = [float(np.quantile(boot_gamma, 0.025)), float(np.quantile(boot_gamma, 0.975))]
    omega_ci = [float(np.quantile(boot_omega, 0.025)), float(np.quantile(boot_omega, 0.975))]
    if gamma_ci[1] < gamma_margin:
        decision = "equivalent_within_margin"
    elif gamma_ci[0] > gamma_margin:
        decision = "heterogeneity_exceeds_margin"
    else:
        decision = "inconclusive"
    return {
        "cell_probabilities_by_environment": {
            env: [[float(p[i, 0, 0]), float(p[i, 0, 1])],
                  [float(p[i, 1, 0]), float(p[i, 1, 1])]]
            for i, env in enumerate(ENVIRONMENTS)
        },
        "psi_by_environment": dict(zip(ENVIRONMENTS, psi_by_environment(p))),
        "gamma_max_pairwise_tv": {"estimate": gamma_hat, "bootstrap_ci95": gamma_ci},
        "omega_mean_pairwise_tv": {"estimate": omega_hat, "bootstrap_ci95": omega_ci},
        "gamma_equivalence_margin": gamma_margin,
        "decision_rule": (
            "equivalent if upper 95% bootstrap CI < margin; "
            "heterogeneous if lower 95% CI > margin; otherwise inconclusive"
        ),
        "decision": decision,
        "bootstrap_replicates": n_boot,
        "bootstrap_unit": "complete randomized block, resampled independently within environment",
    }


def theoretical_gamma(mechanism: str) -> float:
    if mechanism in ("stable_target", "stable_negative_control"):
        return 0.0
    return max(ETA_DRIFT) - min(ETA_DRIFT)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="outputs/cross_environment")
    ap.add_argument("--seed", type=int, default=20261125)
    ap.add_argument("--blocks", type=int, default=DEFAULT_BLOCKS)
    ap.add_argument("--repeats-per-cell", type=int, default=DEFAULT_REPEATS)
    ap.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAP)
    ap.add_argument("--gamma-margin", type=float, default=GAMMA_MARGIN)
    args = ap.parse_args()
    if args.blocks < 10:
        raise SystemExit("Use at least 10 blocks per environment for this simulation.")
    if args.repeats_per_cell < 2:
        raise SystemExit("Use at least 2 repeats per cell per block.")
    if args.bootstrap < 100:
        raise SystemExit("Use at least 100 bootstrap replicates.")
    if not 0 < args.gamma_margin < 1:
        raise SystemExit("gamma margin must be between 0 and 1.")
    data = generate_data(args.seed, args.blocks, args.repeats_per_cell)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data.to_csv(outdir / "cross_environment_trials.csv", index=False)
    results = {
        "notice": "Synthetic methodological validation only; not empirical evidence and not part of frozen v1.1.",
        "settings": {
            "seed": args.seed, "environments": list(ENVIRONMENTS), "mechanisms": list(MECHANISMS),
            "blocks_per_environment_per_mechanism": args.blocks,
            "repeats_per_cell_per_block": args.repeats_per_cell,
            "trials_per_environment_per_mechanism": args.blocks * 4 * args.repeats_per_cell,
            "trials_total": len(data), "bootstrap_replicates": args.bootstrap,
            "gamma_margin": args.gamma_margin, "stable_eta": ETA_STABLE,
            "drifting_eta_by_environment": dict(zip(ENVIRONMENTS, ETA_DRIFT)),
        },
        "theoretical_gamma": {m: theoretical_gamma(m) for m in MECHANISMS},
        "results": {},
    }
    for i, mechanism in enumerate(MECHANISMS):
        results["results"][mechanism] = analyze_mechanism(
            data[data.mechanism == mechanism].copy(), args.seed + 100 + i,
            args.bootstrap, args.gamma_margin,
        )
    (outdir / "cross_environment_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = [
        "# FIR-3 Cross-Environment Stability — Synthetic Validation", "",
        "> Synthetic methodological validation only. Not empirical evidence and does not modify frozen v1.1.", "",
        f"- Environments: {', '.join(ENVIRONMENTS)}",
        f"- Blocks per environment and mechanism: {args.blocks}",
        f"- Repeats per input cell per block: {args.repeats_per_cell}",
        f"- Bootstrap replicates: {args.bootstrap}",
        f"- Illustrative Gamma equivalence margin: {args.gamma_margin:.3f}", "",
        "| Mechanism | Theoretical Gamma | Estimated Gamma (95% block-bootstrap CI) | Estimated Omega | Decision |",
        "|---|---:|---:|---:|---|",
    ]
    for mechanism in MECHANISMS:
        r = results["results"][mechanism]
        g, o = r["gamma_max_pairwise_tv"], r["omega_mean_pairwise_tv"]
        lines.append(
            f"| {mechanism} | {results['theoretical_gamma'][mechanism]:.3f} "
            f"| {g['estimate']:.4f} [{g['bootstrap_ci95'][0]:.4f}, {g['bootstrap_ci95'][1]:.4f}] "
            f"| {o['estimate']:.4f} | {r['decision']} |"
        )
    lines += [
        "", "## Interpretation", "",
        "For Bernoulli outcomes, total-variation distance between two response kernels equals the absolute difference in success probabilities. Gamma is the maximum such difference over environment pairs and the four common-support input cells. Omega is the mean pairwise difference.",
        "",
        "Classify as equivalent only when the upper 95% block-bootstrap bound for Gamma is below the illustrative margin. Establish heterogeneity beyond the margin only when the lower bound is above it. Overlap with the margin is inconclusive; failure to establish heterogeneity is not proof of invariance.",
        "",
        "The stable target and stable negative control check false drift detection in two different response structures. The drifting target checks sensitivity to an environment-dependent response kernel.",
        "",
        "The simulation assumes randomized A,B, all four cells in every environment, common outcome measurement, and independent blocks. It does not validate real interventions, object sampling, transportability, or implementation independence.",
        "",
        "This supplementary margin, environment schedule, and sample size do not amend FIR-3 v1.1 and require separate justification before empirical use.", "",
    ]
    (outdir / "cross_environment_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {outdir / 'cross_environment_trials.csv'}")
    print(f"Wrote {outdir / 'cross_environment_results.json'}")
    print(f"Wrote {outdir / 'cross_environment_report.md'}")


if __name__ == "__main__":
    main()
