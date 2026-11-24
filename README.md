# FIR-3 Research Repository

This repository is dedicated to **FIR-3**, a research program studying relational causal control, higher-order interaction, predictive information, and cross-environment stability.

## Project map

| Path | Purpose |
|---|---|
| [FIR-3/](FIR-3/README.md) | Research index, status, protocol boundaries, analysis plan, and cross-environment protocol |
| [simulate_fir3.py](simulate_fir3.py) | Synthetic target and negative-control simulation |
| [fir3_incremental_prediction.py](fir3_incremental_prediction.py) | Supplementary nested prediction diagnostic |
| [fir3_cross_environment.py](fir3_cross_environment.py) | Cross-environment stability simulation |
| [fir3_cross_environment_operating_check.py](fir3_cross_environment_operating_check.py) | Monte Carlo operating-characteristic diagnostic |

## Reproduce

```bash
python -m pip install numpy pandas
python simulate_fir3.py --outdir outputs --seed 20261124 --bootstrap 10000
python fir3_incremental_prediction.py --input outputs/simulated_trials.csv --outdir outputs/incremental
python fir3_cross_environment.py --outdir outputs/cross_environment --seed 20261125 --blocks 60 --repeats-per-cell 10 --bootstrap 5000 --gamma-margin 0.10
python fir3_cross_environment_operating_check.py --outdir outputs/cross_environment --seed 30000 --replicates 50 --bootstrap 500 --blocks 60 --repeats-per-cell 10 --gamma-margin 0.10
```

All checked-in FIR-3 trial data and validation outputs are synthetic, not empirical evidence. FIR-3 v1.1 remains a frozen protocol; supplementary diagnostics do not silently alter it.

## Separate project

**CFS-CTS Core 0.1** has been extracted into its own repository: [qq399356807/CFS-CTS](https://github.com/qq399356807/CFS-CTS). It has its own source tree, security model, checksum manifest, test reports, and cross-platform CI. No CFS-CTS implementation is maintained in this FIR-3 repository.

## Continuous integration

GitHub Actions runs Python syntax checks, FIR-3 synthetic validation, the supplementary prediction diagnostic, and cross-environment stability simulations. Reports are uploaded as workflow artifacts.

## Research governance

1. Treat FIR-3 v1.1 as frozen; supplementary work must not silently alter it.
2. Distinguish synthetic validation, software tests, and empirical evidence.
3. Keep protocol changes, analysis changes, and exploratory diagnostics explicitly versioned.
4. Review changes on dedicated branches before merging to `main`.
5. CI validation is not evidence of empirical validity or a public production deployment.

See [FIR-3 research status](FIR-3/RESEARCH_STATUS.md), [protocol boundary](FIR-3/PROTOCOL_BOUNDARY.md), and [cross-environment design](FIR-3/CROSS_ENVIRONMENT_PROTOCOL.md).
