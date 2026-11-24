# FIR-3 Analysis Plan — Supplementary and Future Work

This plan does not modify frozen v1.1.

## A. Supplementary nested predictive diagnostic

The existing validation compares history-only against history plus all current relations. Since A alone predicts the negative-control outcome, that comparison cannot isolate B's predictive contribution.

Compare:
1. history-only;
2. A-only;
3. A+B;
4. A+B+C_t.

Primary supplementary contrast:

```
ΔL_(B|A) = L(A-only) - L(A+B)
```

Positive values mean adding B after A reduces held-out log loss. Report paired held-out-block bootstrap intervals. This is exploratory, not a v1.1 confirmatory endpoint.

Expected qualitative behavior: target XOR model, B adds predictive value conditional on A; negative control, B adds no systematic predictive value conditional on A; independent C_t should not systematically improve prediction.

## B. Cross-environment experiment

Before data collection define environment factors, object identities and sampling frame, independently manipulable interventions, common support, outcome measurement, missingness, precision targets, environment-held-out validation, equivalence margins, and multiplicity handling.

Estimate combination-specific kernels K_c(y|x,r) on common support. Report maximum pairwise and average discrepancy. Failure to reject heterogeneity is not evidence of equivalence; use a prespecified equivalence test or confidence bound.

## C. Implementation-independence challenge

Predefine the baseline model class:
- allowed latent variables and cardinality / complexity;
- whether latent variables may respond to interventions on R;
- modularity and parameter invariance across environments;
- observable response family to match;
- predictive and interventional test sets;
- complexity penalty / scoring rule.

A flexible latent model can encode the relation variable. “Not reducible” must remain relative to an explicit baseline class and intervention interface.

## D. Release gates

Do not label FIR-3 empirically validated until real intervention implementation, raw data, exclusions, analysis scripts, confirmatory results, replication scope, and alternative shared-module explanations are documented.
