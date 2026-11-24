#!/usr/bin/env python3
"""Illustrative Monte Carlo classification check; not a formal power analysis."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from fir_cross_environment import (
    MECHANISMS, generate_data, analyze_mechanism,
    DEFAULT_BLOCKS, DEFAULT_REPEATS, GAMMA_MARGIN,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="outputs/cross_environment")
    ap.add_argument("--seed", type=int, default=30000)
    ap.add_argument("--replicates", type=int, default=50)
    ap.add_argument("--bootstrap", type=int, default=500)
    ap.add_argument("--blocks", type=int, default=DEFAULT_BLOCKS)
    ap.add_argument("--repeats-per-cell", type=int, default=DEFAULT_REPEATS)
    ap.add_argument("--gamma-margin", type=float, default=GAMMA_MARGIN)
    args = ap.parse_args()
    if args.replicates < 1 or args.bootstrap < 100:
        raise SystemExit("Require at least 1 Monte Carlo replicate and 100 bootstrap draws.")
    counts = {
        m: {"equivalent_within_margin": 0, "heterogeneity_exceeds_margin": 0, "inconclusive": 0}
        for m in MECHANISMS
    }
    for rep in range(args.replicates):
        data = generate_data(args.seed + rep, args.blocks, args.repeats_per_cell)
        for i, mechanism in enumerate(MECHANISMS):
            result = analyze_mechanism(
                data[data.mechanism == mechanism],
                args.seed + 10000 + rep * len(MECHANISMS) + i,
                args.bootstrap, args.gamma_margin,
            )
            counts[mechanism][result["decision"]] += 1
    summary = {
        "notice": "Illustrative Monte Carlo diagnostic only; not formal power analysis or empirical evidence.",
        "settings": {
            "seed": args.seed, "replicates": args.replicates,
            "bootstrap_per_analysis": args.bootstrap, "blocks_per_environment": args.blocks,
            "repeats_per_cell_per_block": args.repeats_per_cell, "gamma_margin": args.gamma_margin,
        },
        "classification_counts": counts,
        "classification_proportions": {
            m: {k: v / args.replicates for k, v in row.items()}
            for m, row in counts.items()
        },
    }
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cross_environment_operating_check.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Cross-Environment Simulation Operating Check", "",
        "> Illustrative Monte Carlo diagnostic only. Not formal power analysis and not empirical evidence.", "",
        f"- Replications: {args.replicates}; bootstrap draws per analysis: {args.bootstrap}",
        f"- Blocks per environment: {args.blocks}; repeats per cell per block: {args.repeats_per_cell}",
        f"- Gamma margin: {args.gamma_margin:.3f}", "",
        "| Mechanism | Equivalent | Heterogeneity | Inconclusive |",
        "|---|---:|---:|---:|",
    ]
    for mechanism, row in counts.items():
        lines.append(f"| {mechanism} | {row['equivalent_within_margin']} | {row['heterogeneity_exceeds_margin']} | {row['inconclusive']} |")
    lines += [
        "", "These finite simulation counts describe only the specified synthetic scenarios and seeds. They are not guaranteed error rates, general power, or performance in real experiments.", "",
    ]
    (out / "cross_environment_operating_check.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out / 'cross_environment_operating_check.json'}")


if __name__ == "__main__":
    main()
