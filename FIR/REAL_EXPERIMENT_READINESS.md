# FIR Real-Experiment Readiness Framework

**Status:** planning template; not a preregistration, ethics approval, or authorization to collect data.  
**Protocol boundary:** this document does not amend the frozen minimum three-relation v1.1 protocol.

## Purpose and evidence boundary

This framework turns the repository's open research gaps into a reviewable sequence for a possible real-world study. It is deliberately a template: unknown design choices remain unresolved rather than being filled with convenient defaults.

The current checked-in trials and result summaries are synthetic. Passing repository CI or reproducing a synthetic result is software/method validation only. It is not evidence that a real system has the target causal structure.

Keep the four claims separate:

- **C_R — controlled response:** an outcome changes under a well-defined intervention.
- **X_R — non-additive interaction:** the joint response is not explained by the prespecified additive contrast.
- **P_R — incremental prediction:** a relation input improves held-out prediction beyond the specified baseline.
- **I_R — implementation independence:** the observed response cannot be adequately represented by a prespecified competing implementation class.

Evidence for one claim must not be promoted into evidence for another.

## Gate 0 — Freeze the study question and scope

Complete and version the following before recruitment, data acquisition, or outcome inspection:

| Required item | Required record |
|---|---|
| Study question | One primary question, stated in observable terms |
| Target system and unit | Physical/organizational/software system; unit of assignment and unit of analysis |
| Object and environment sampling frame | Inclusion frame, selection procedure, exclusions, and intended generalization |
| Intervention interface | What is physically or operationally changed to set A and B |
| Outcome | Observable definition, coding, time window, and measurement instrument |
| Study scope | Which of C_R, X_R, P_R, and I_R are primary, secondary, exploratory, or out of scope |
| Version control | Protocol version, date, authors, immutable repository commit, and deviation log |

**Stop condition:** if A and B cannot be independently assigned or manipulated under a defensible intervention semantics, do not describe the design as a test of independent interventions. Redesign the question or label the work observational.

## Gate 1 — Operationalize interventions and measurement

For each intervention, document:

1. assignment mechanism and who/what executes it;
2. treatment levels and exact operational procedure;
3. compliance and fidelity measures;
4. possible interference between units;
5. carryover, washout, and order effects;
6. masking/blinding where feasible;
7. manipulation checks that do not redefine the outcome after observing results.

For the outcome, specify instrument calibration, coding rules, assessor reliability, missingness capture, and any transformations. Preserve raw observations separately from derived analysis tables.

Define the causal estimand in terms of the actual intervention interface. Do not use do(A=a) or do(B=b) as shorthand for a manipulation that has not been operationally specified.

## Gate 2 — Design, randomization, and sample-size justification

Before data collection, record:

- randomization unit, blocking factors, allocation sequence generation, concealment, and implementation;
- four-cell coverage for A×B in every environment included in a cross-environment comparison;
- object/environment assignment and whether the same units appear in multiple conditions;
- clustering, repeated measurements, dependence, interference, and expected attrition;
- primary precision or power target, smallest scientifically relevant effect, nuisance assumptions, and simulation code;
- stopping rule and any interim looks;
- multiplicity strategy across outcomes, environments, and contrasts.

The frozen v1.1 minimum design records 400 effective trials per input cell per model. This is a protocol boundary, not a universal sample-size guarantee for a new physical system. Effective sample size must account for clustering, repeated measures, noncompliance, and the actual assignment unit. Do not copy the synthetic simulation's 40-block layout or bootstrap count as a real-world sample-size justification.

If the study is intended to claim equivalence or stability, justify the equivalence margin before observing outcomes using measurement precision, practical consequences, and scientific context. The illustrative cross-environment margin Γ=0.10 in the synthetic module is not an empirical default.

## Gate 3 — Prespecify estimands and analysis

### Frozen v1.1 contrasts

For binary outcomes and the frozen three-relation design, retain the definitions in [PROTOCOL_BOUNDARY.md](PROTOCOL_BOUNDARY.md):

- four cell risks p_ab;
- simple effects ΔA(b) and ΔB(a);
- probability-scale interaction Ψ = p11 - p10 - p01 + p00;
- target direction and negative-control equivalence rules exactly as frozen.

Do not alter coding, thresholds, or confirmatory status after seeing data. If a real system requires a different outcome scale or estimand, treat that as a separately versioned protocol amendment rather than silently changing v1.1.

### Dependence-aware inference

The analysis plan must identify the actual independent assignment/resampling unit. Use cluster- or block-aware uncertainty estimates consistent with the randomization and sampling design. Do not resample individual rows when the design randomizes or samples clusters.

Specify in advance:
- estimator and interval construction for every primary estimand;
- treatment of noncompliance and protocol deviations;
- missing-data assumptions and sensitivity analyses;
- exclusion rules that can be applied without outcome-driven judgment;
- multiplicity and subgroup handling;
- software versions, random seeds where applicable, and deterministic reproduction commands.

### Incremental prediction

If P_R is evaluated, compare nested models on held-out units/blocks, not randomly split rows from the same dependent cluster. At minimum distinguish history-only, A-only, A+B, and A+B+C_t baselines where these are scientifically meaningful.

The contrast ΔL_(B|A) = L(A-only) - L(A+B) is supplementary/exploratory unless explicitly included in a newly approved confirmatory protocol. A positive predictive improvement is not, by itself, evidence of causal interaction or implementation independence.

## Gate 4 — Cross-environment stability

Use [CROSS_ENVIRONMENT_PROTOCOL.md](CROSS_ENVIRONMENT_PROTOCOL.md) as a methodological starting point, not as an empirical preregistration.

Before comparing environments, define:

- the environment factors and why they represent the target population;
- object identities, sampling frame, and whether objects are exchangeable;
- common-support requirements for every intervention cell;
- measurement and intervention comparability;
- the kernel discrepancy estimand (including worst-case Γ and any average Ω summary);
- an empirically justified equivalence margin and interval/decision rule;
- environment-held-out validation and multiplicity handling.

A failure to reject heterogeneity is not evidence of equivalence. If common support is absent, report the contrast as undefined for unsupported cells rather than extrapolating silently.

## Gate 5 — Competing implementation models (I_R)

An implementation-independence claim is meaningful only relative to an explicit, bounded competitor class and a declared intervention interface.

Before outcomes are examined, specify:

| Competitor dimension | Prespecification required |
|---|---|
| Latent state | Allowed variables, cardinality/complexity bounds, and observability assumptions |
| Intervention response | Whether and how latent variables may respond to A and B |
| Modularity | Which mechanisms/parameters must remain invariant across interventions or environments |
| Observable fit | Which response distributions and conditional predictions must be matched |
| Test data | Held-out interventional and predictive conditions |
| Complexity | Penalty, scoring rule, or other comparison criterion |
| Robustness | Alternative plausible competitor classes and sensitivity analyses |

A sufficiently flexible hidden module may encode the same response distribution as an explicit relation variable. Failure of one narrow competitor is not proof of implementation independence. State the scope of the tested class and retain the possibility of unmodeled shared mechanisms.

## Gate 6 — Data integrity, ethics, and reproducibility

Before collection, document applicable ethics review/consent, safety review, privacy and retention rules, access controls, and data-sharing constraints. Do not place identifiable or sensitive raw data in this public repository.

Maintain:
- immutable raw-data snapshots in an appropriately controlled location;
- a data dictionary and provenance record;
- checksums for released, non-sensitive analysis inputs;
- versioned cleaning and analysis scripts;
- a complete exclusion/deviation log;
- environment and dependency lock information;
- a reproduction report that distinguishes unavailable private inputs from failed code.

Publish only data and materials that can lawfully and ethically be shared. Synthetic fixtures may be committed here; real participant or proprietary data require a separate controlled data location.

## Preregistration record — fill before data collection

Copy and complete this section in a separately versioned, dated protocol record. Unfilled fields mean the study is not ready for confirmatory data collection.

- **Protocol ID / version / date:** TBD
- **Primary claim(s):** TBD
- **Target system, units, and sampling frame:** TBD
- **A and B intervention procedures:** TBD
- **Outcome definition and measurement window:** TBD
- **Randomization and blocking:** TBD
- **Primary estimand(s) and estimator(s):** TBD
- **Sample-size / precision justification and code:** TBD
- **Equivalence margins and justification (if applicable):** TBD
- **Missingness, exclusions, deviations, and sensitivity analyses:** TBD
- **Multiplicity and stopping rules:** TBD
- **Held-out validation plan:** TBD
- **Competitor model class for I_R (if claimed):** TBD
- **Ethics / consent / privacy approvals:** TBD
- **Data custody and release plan:** TBD
- **Immutable protocol commit / registration location:** TBD

## Go / no-go decision

A confirmatory real-world study is **not ready** until all applicable Gate 0–6 items are resolved, reviewed, and frozen. A reviewer should be able to reconstruct the intervention, estimand, sample-size rationale, decision rules, and competitor class without relying on post-outcome explanations.

After data collection, report deviations and all prespecified outcomes, including inconclusive results. Do not label FIR empirically validated merely because code, synthetic simulations, or CI pass.

## Relationship to existing materials

- [Frozen v1.1 boundary](PROTOCOL_BOUNDARY.md)
- [Supplementary analysis plan](ANALYSIS_PLAN.md)
- [Cross-environment methodological design](CROSS_ENVIRONMENT_PROTOCOL.md)
- [Research status and evidence register](RESEARCH_STATUS.md)

This framework is a planning artifact. It does not itself freeze a study, constitute a preregistration, amend v1.1, or authorize data collection.
