# FIR-3 — Research and validation workspace

This repository contains the FIR-3 research protocol, synthetic validation, and supplementary diagnostics.

## Project map

| Path | Purpose |
|---|---|
| [FIR-3/](FIR-3/README.md) | Research index, status, protocol boundaries and analysis plan |
| [simulate_fir3.py](simulate_fir3.py) | Synthetic target and negative-control simulation |
| [fir3_incremental_prediction.py](fir3_incremental_prediction.py) | Exploratory nested prediction diagnostic |
| [fir3_cross_environment.py](fir3_cross_environment.py) | Cross-environment stability simulation |
| [fir3_cross_environment_operating_check.py](fir3_cross_environment_operating_check.py) | Monte Carlo operating-characteristic diagnostic |

## Reproduce

Install the research dependencies:

```bash
python -m pip install numpy pandas
```

Run the primary synthetic validation:

```bash
python simulate_fir3.py --outdir outputs --seed 20261124 --bootstrap 10000
```

Run the supplementary nested-prediction diagnostic:

```bash
python fir3_incremental_prediction.py --input outputs/simulated_trials.csv --outdir outputs/incremental
```

All checked-in FIR-3 trial data are synthetic, not empirical evidence.

## Continuous integration

GitHub Actions compiles the FIR-3 Python entry points and runs:
- primary synthetic validation;
- supplementary nested-prediction diagnostic;
- cross-environment stability simulation;
- cross-environment Monte Carlo operating check.

Validation artifacts are uploaded by the workflow.

## Governance

1. Treat FIR-3 v1.1 as frozen; supplementary work must not silently alter it.
2. Distinguish synthetic validation, software tests, and empirical evidence.
3. Propose changes on a dedicated branch and review before merging to `main`.
4. CI validation is not a public production deployment.

The independent CFS-CTS Core 0.1 project now lives in [qq399356807/CFS-CTS](https://github.com/qq399356807/CFS-CTS) and is no longer maintained in this repository.

See [FIR-3 research status](FIR-3/RESEARCH_STATUS.md), [protocol boundary](FIR-3/PROTOCOL_BOUNDARY.md), and [cross-environment design](FIR-3/CROSS_ENVIRONMENT_PROTOCOL.md).
