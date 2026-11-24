# FIR-3 Cross-Environment — Synthetic Pilot Record

**Evidence class:** synthetic methodological validation only. No empirical data were used.

## Pilot setup

- Four environments.
- Three mechanisms: stable XOR target, drifting XOR target, stable additive negative control.
- 60 randomized blocks per environment and mechanism.
- 10 repetitions per A×B cell per block.
- 28,800 rows total.
- 5,000 complete-block bootstrap replicates for the final deterministic run.
- Illustrative Gamma margin: 0.10.

## Deterministic run (seed 20261125)

| Mechanism | Theoretical Gamma | Estimated Gamma | 95% block-bootstrap interval | Omega | Classification |
|---|---:|---:|---:|---:|---|
| Stable target | 0.00 | 0.0383 | [0.0317, 0.0767] | 0.0142 | Equivalent within illustrative margin |
| Drifting target | 0.18 | 0.2083 | [0.1867, 0.2517] | 0.1063 | Heterogeneity exceeds illustrative margin |
| Stable negative control | 0.00 | 0.0483 | [0.0367, 0.0833] | 0.0163 | Equivalent within illustrative margin |

The per-environment interaction estimates for the drifting target change from approximately -1.597 to -0.842 as the noise rate rises. The stable target remains near -1.6. This demonstrates that the implementation detects the selected synthetic drift.

## Monte Carlo diagnostic

A separate 50-replicate diagnostic with 500 bootstrap draws per analysis, 60 blocks per environment, and the same illustrative margin classified:
- stable target: equivalent in 50/50 runs;
- drifting target: heterogeneity beyond margin in 50/50 runs;
- stable additive negative control: equivalent in 50/50 runs.

These counts are specific to the chosen synthetic scenarios, seeds, sample size, and rule. They are not guaranteed false-positive rates, formal power estimates, or evidence of real-world stability.

## Interpretation boundary

The results show that this implementation distinguishes the selected stable and drifting synthetic kernels under this design. They do not establish cross-object invariance in a physical system, transportability, or implementation independence. The margin 0.10 is illustrative and must be justified before empirical use.
