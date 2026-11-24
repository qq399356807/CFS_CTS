# CFS_CTS — Research and audit workspace

Two separately governed workstreams live here:

- **FIR-3**: research on relational causal control, interaction, predictive information, and implementation independence.
- **CFS-CTS Core 0.1**: a chronological event-integrity and audit prototype, not a production tamper-proof system.

## Project map

| Path | Purpose |
|---|---|
| [FIR-3/](FIR-3/README.md) | Research index, status, protocol boundaries and analysis plan |
| [simulate_fir3.py](simulate_fir3.py) | Synthetic target and negative-control simulation |
| [fir3_incremental_prediction.py](fir3_incremental_prediction.py) | Exploratory nested prediction diagnostic |
| [CFS_CTS_Core_0_1/](CFS_CTS_Core_0_1/README.md) | Independent audit-core prototype and tests |

## Reproduce

```bash
python -m pip install numpy pandas
python simulate_fir3.py --outdir outputs --seed 20261124 --bootstrap 10000
python fir3_incremental_prediction.py --input outputs/simulated_trials.csv --outdir outputs/incremental
```

All checked-in FIR-3 trial data are synthetic, not empirical evidence.

## Continuous integration

GitHub Actions runs Python syntax checks, FIR-3 synthetic validation, the supplementary prediction diagnostic, and the CFS-CTS test runner. Reports are uploaded as workflow artifacts.

## Governance

1. Treat FIR-3 v1.1 as frozen; supplementary work must not silently alter it.
2. Keep FIR-3 and CFS-CTS as distinct workstreams.
3. Distinguish synthetic validation, software tests, and empirical evidence.
4. Propose changes on a dedicated branch and review before merging to `main`.
5. CI validation is not a public production deployment.

See [FIR-3 research status](FIR-3/RESEARCH_STATUS.md), [protocol boundary](FIR-3/PROTOCOL_BOUNDARY.md), and [cross-environment design](FIR-3/CROSS_ENVIRONMENT_PROTOCOL.md).
