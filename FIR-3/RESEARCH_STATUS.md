# FIR-3 Research Status and Evidence Register

Last updated: 2026-11-24

## Completed in repository

- Minimal three-relation target and no-interaction negative-control models encoded in Python.
- Theoretical four-cell probabilities, simple effects, probability-scale interaction Ψ, and mutual-information values asserted by code.
- Deterministic synthetic dataset and machine-readable results checked in.
- Complete randomized-block bootstrap intervals and held-out prediction comparison implemented.
- Research archive and CI workflow being established on `fir3/research-archive-ci`.

## Current synthetic result (not empirical)

With seed 20261124 and η=0.10:
- Target Ψ estimate: -1.6025; theoretical value: -1.6.
- Negative-control Ψ estimate: 0.01; stored 90% bootstrap interval satisfies ±0.20 equivalence margin.
- MI estimates: about 0.5364 bit (target) and 0.5269 bit (negative control), versus 0.5310 bit theoretically.
- All-relations prediction improves over a history-only constant baseline in both models. A predicts the negative-control outcome, so this is not evidence of interaction-specific predictive gain.

## Separate claim ledger

| Claim | Current status | Needed next |
|---|---|---|
| C_R: controlled causal response | Encoded in synthetic intervention design only | Controlled experiment with validated intervention implementation |
| X_R: non-additive interaction | Theory and synthetic recovery checked | Real randomized data and preregistered estimator |
| P_R: incremental predictive information | Theoretical MI and broad held-out diagnostic | Held-out real data; nested A vs A+B comparison |
| I_R: implementation independence | Not tested | Explicit baseline class, intervention semantics, invariance constraints, comparative fit / complexity analysis |

## Open gaps

1. Legacy ZIP files have not yet been inventoried file-by-file; retained unchanged.
2. No empirical dataset or external-system execution log is present.
3. No cross-object / cross-environment perturbation study is implemented.
4. No preregistered competitor-model or implementation-independence comparison exists.
5. Existing all-relations prediction does not isolate B conditional on A; the supplementary script is exploratory only.

## Evidence language

Use “synthetic validation” for generated data, “software test” for code behavior, and “empirical result” only for observed data from the intended real system. Never promote simulated results into empirical claims.
