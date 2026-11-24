# FIR-3 Cross-Environment Stability — Supplementary Design

**Status:** methodological simulation protocol, not an amendment to frozen v1.1 and not an empirical preregistration.

## Question

Does the controlled response kernel remain approximately invariant across a prespecified set of environments / object combinations?

For environment c and binary interventions A,B:

```
K_c(y | do(A=a), do(B=b))
p_c(a,b) = P(C_next=1 | do(A=a), do(B=b), c)
```

All four input cells must be represented in every environment. Outcome coding, intervention implementation, and measurement must be comparable. A common-support failure makes the cross-environment contrast undefined for unsupported cells.

## Discrepancy measures

For Bernoulli outcomes, total variation distance is the absolute difference in success probabilities. Define:

```
Gamma = max_(c<c') max_(a,b) |p_c(a,b) - p_c'(a,b)|
Omega = mean_(c<c') mean_(a,b) |p_c(a,b) - p_c'(a,b)|
```

Gamma captures the largest environment-pair / input-cell discrepancy. Omega summarizes average discrepancy and must not replace Gamma for worst-case stability.

The supplementary script uses complete randomized blocks as the resampling unit, resampled independently within each environment. It reports two-sided 95% percentile bootstrap intervals.

## Illustrative decision rule

The simulation uses an illustrative Gamma margin of 0.10:
- equivalent within margin if upper 95% interval < 0.10;
- heterogeneity exceeds margin if lower 95% interval > 0.10;
- otherwise inconclusive.

This margin is only a software-demonstration value. An empirical study must justify its margin using measurement precision, practical consequences, and scientific context before observing outcomes. Failure to establish heterogeneity is not evidence of equivalence.

## Synthetic scenarios

- stable target: XOR response with eta=0.10 in each of four environments;
- drifting target: XOR response with eta=(0.10,0.16,0.22,0.28);
- stable negative control: additive A-only response with eta=0.10 in all environments.

Default simulation: 4 environments × 3 mechanisms × 60 blocks × 4 cells × 10 trials = 28,800 synthetic trials. Bootstrap count defaults to 5,000.

## Important limitations

This validates a statistical workflow under known synthetic kernels. It does not establish that real interventions are implemented correctly, that environments are sampled representatively, that objects are exchangeable, or that a relation is implementation-independent. The drift is imposed through a noise-rate change; other forms of drift (interaction sign, baseline risk, nonlinear response, measurement error) require additional scenarios.

The Monte Carlo operating check is a small illustrative diagnostic, not a formal power analysis. Empirical sample size must be chosen from a prespecified smallest relevant drift, block-level variance, environment count, multiplicity policy, and desired precision.

## Separation from v1.1

This entire module is supplementary. It does not change the frozen three-relation v1.1 model, sample design, thresholds, or confirmatory endpoints.
