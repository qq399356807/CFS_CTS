#!/usr/bin/env python3
"""Exploratory FIR nested predictive diagnostic; not a v1.1 endpoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

DEFAULT_SEED = 20261124
HOLDOUT_BLOCKS = 8
N_BOOT = 10_000
MODELS = ("target", "negative_control")


def fit_predict_logloss(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> np.ndarray:
    y = train["C_next"].to_numpy(dtype=int)
    global_p = (y.sum() + 0.5) / (len(y) + 1.0)
    if not features:
        probs = np.full(len(test), global_p, dtype=float)
    else:
        grouped = train.groupby(features, dropna=False)["C_next"].agg(["sum", "count"])
        keys = [tuple(row) for row in test[features].itertuples(index=False, name=None)]
        probs = np.empty(len(test), dtype=float)
        for i, key in enumerate(keys):
            lookup = key[0] if len(key) == 1 else key
            if lookup in grouped.index:
                cell = grouped.loc[lookup]
                probs[i] = (float(cell["sum"]) + 0.5) / (float(cell["count"]) + 1.0)
            else:
                probs[i] = global_p
    probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
    outcome = test["C_next"].to_numpy(dtype=int)
    return -(outcome * np.log(probs) + (1 - outcome) * np.log(1 - probs))


def block_bootstrap_delta(test, loss_a, loss_b, rng, n_boot):
    paired = pd.DataFrame({
        "block": test["block"].to_numpy(),
        "difference": loss_a - loss_b,
    }).groupby("block")["difference"].mean()
    values = paired.to_numpy(dtype=float)
    if len(values) < 2:
        raise ValueError("At least two held-out blocks are required.")
    draws = rng.integers(0, len(values), size=(n_boot, len(values)))
    boot = values[draws].mean(axis=1)
    return {
        "estimate": float(values.mean()),
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        "n_heldout_blocks": int(len(values)),
    }


def analyze_model(df, seed, n_boot):
    blocks = sorted(df["block"].unique().tolist())
    if len(blocks) <= HOLDOUT_BLOCKS:
        raise ValueError(f"Need more than {HOLDOUT_BLOCKS} blocks.")
    split_rng = np.random.default_rng(seed)
    holdout = sorted(split_rng.choice(blocks, size=HOLDOUT_BLOCKS, replace=False).tolist())
    train = df[~df["block"].isin(holdout)].copy()
    test = df[df["block"].isin(holdout)].copy()
    feature_sets = {
        "history_only": [],
        "A_only": ["A_t"],
        "A_plus_B": ["A_t", "B_t"],
        "A_plus_B_plus_C": ["A_t", "B_t", "C_t"],
    }
    losses = {name: fit_predict_logloss(train, test, cols) for name, cols in feature_sets.items()}
    rng = np.random.default_rng(seed + 1000)
    comparisons = {
        "A_increment_over_history": block_bootstrap_delta(test, losses["history_only"], losses["A_only"], rng, n_boot),
        "B_increment_given_A": block_bootstrap_delta(test, losses["A_only"], losses["A_plus_B"], rng, n_boot),
        "C_increment_given_AB": block_bootstrap_delta(test, losses["A_plus_B"], losses["A_plus_B_plus_C"], rng, n_boot),
        "all_relations_over_history": block_bootstrap_delta(test, losses["history_only"], losses["A_plus_B_plus_C"], rng, n_boot),
    }
    return {
        "holdout_blocks": holdout,
        "train_trials": int(len(train)),
        "test_trials": int(len(test)),
        "mean_logloss": {name: float(loss.mean()) for name, loss in losses.items()},
        "comparisons": comparisons,
        "interpretation": (
            "Positive delta means lower held-out log loss after adding predictors. "
            "B_increment_given_A is predictive, not causal, and is exploratory rather than a v1.1 endpoint."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="outputs/simulated_trials.csv")
    parser.add_argument("--outdir", default="outputs/incremental")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--bootstrap", type=int, default=N_BOOT)
    args = parser.parse_args()
    if args.bootstrap < 100:
        raise SystemExit("Use at least 100 bootstrap replicates.")
    data = pd.read_csv(args.input)
    required = {"model", "block", "A_t", "B_t", "C_t", "C_next"}
    missing = required - set(data.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {sorted(missing)}")
    result = {
        "notice": "Exploratory supplementary analysis of synthetic data; not empirical evidence.",
        "settings": {
            "seed": args.seed, "bootstrap_replicates": args.bootstrap,
            "bootstrap_unit": "held-out complete block", "heldout_blocks": HOLDOUT_BLOCKS,
        },
        "models": {},
    }
    for model in MODELS:
        subset = data[data["model"] == model].copy()
        result["models"][model] = analyze_model(
            subset, args.seed + (31 if model == "target" else 32), args.bootstrap
        )
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "incremental_prediction.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# FIR Supplementary Nested Prediction Diagnostic", "",
        "> Synthetic-data exploratory analysis only. Does not amend frozen v1.1.", "",
        "| Model | A increment over history | B increment given A | C increment given AB |",
        "|---|---:|---:|---:|",
    ]
    for model in MODELS:
        comparisons = result["models"][model]["comparisons"]
        cells = []
        for key in ("A_increment_over_history", "B_increment_given_A", "C_increment_given_AB"):
            item = comparisons[key]
            cells.append(f'{item["estimate"]:.5f} [{item["ci95"][0]:.5f}, {item["ci95"][1]:.5f}]')
        lines.append(f"| {model} | " + " | ".join(cells) + " |")
    lines += [
        "", "Positive values indicate held-out log-loss improvement from adding the named predictor block.",
        "The B-given-A contrast is predictive, not causal. An interval containing zero does not prove equivalence.", "",
    ]
    (outdir / "incremental_prediction.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {outdir / 'incremental_prediction.json'}")
    print(f"Wrote {outdir / 'incremental_prediction.md'}")


if __name__ == "__main__":
    main()
