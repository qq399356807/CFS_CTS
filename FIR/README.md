# FIR Research Archive

FIR is an operational research framework for studying relational causal control. It separates four claims:

- `C_R`: controlled causal response;
- `X_R`: non-additive interaction;
- `P_R`: incremental predictive information;
- `I_R`: implementation independence.

Evidence for one category does not automatically establish another.

## Existing assets

- Root `simulate_fir.py`: target XOR-plus-noise model and no-interaction negative control.
- Root `simulated_trials.csv` and `validation_results.json`: deterministic synthetic run.
- Existing Chinese simulation package and result reports.
- `fir_incremental_prediction.py`: supplementary A-only versus A+B prediction analysis; exploratory, not part of v1.1.
- `FIR.zip` and `FIR-simulation-v1.1-validation.zip`: retained unchanged as legacy snapshots; see [ARCHIVE_INTEGRITY_AUDIT.md](ARCHIVE_INTEGRITY_AUDIT.md) for the verified inventory and source-divergence findings.

## Research layers

1. Single-relation controlled response kernel.
2. Cross-object / cross-combination response stability.
3. Network transition dynamics.
4. Higher-order interaction contrasts.
5. Incremental predictive information.
6. Relative implementation-reduction tests against a prespecified baseline class.

## Frozen protocol boundary

The minimum three-relation v1.1 protocol remains frozen. This archive may document and supplement it, but must not silently change its model definitions, sample design, thresholds, or confirmatory claims. See [PROTOCOL_BOUNDARY.md](PROTOCOL_BOUNDARY.md).

## Evidence status

All current FIR trial rows and result summaries are synthetic. No real-world empirical dataset is registered here. See [RESEARCH_STATUS.md](RESEARCH_STATUS.md), [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md), and [CHANGELOG.md](CHANGELOG.md).

## Real-experiment readiness

[REAL_EXPERIMENT_READINESS.md](REAL_EXPERIMENT_READINESS.md) provides a gated planning template for operationalizing interventions, randomization, sample-size justification, dependence-aware analysis, cross-environment comparisons, competing implementation models, ethics, and data integrity.

It is not a preregistration or authorization to collect data. Unresolved study-specific choices remain marked TBD. Do not begin confirmatory data collection until the applicable gates are completed, reviewed, and frozen. This planning document does not amend v1.1.
