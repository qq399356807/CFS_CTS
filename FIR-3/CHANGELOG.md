# FIR-3 Archive Changelog

## 2026-11-24 — Repository management baseline

- Added research archive index, status register, frozen-protocol boundary, and analysis plan.
- Preserved existing v1.1 simulation outputs and source archives.
- Corrected the simulation point-summary helper so it no longer emits point estimates under misleading `ci_low` / `ci_high` names. Bootstrap intervals remain in explicit `bootstrap_ci95` fields.
- Added a supplementary nested predictive diagnostic comparing A-only with A+B. Exploratory; does not amend v1.1.
- Added GitHub Actions continuous validation. No public service deployment is claimed.

## 2026-11-25 — Cross-environment supplementary module

- Added four-environment synthetic response-kernel stability simulation.
- Added maximum pairwise discrepancy Gamma and mean pairwise discrepancy Omega with complete-block bootstrap intervals.
- Added stable target, drifting target, and stable additive negative-control scenarios.
- Added a Monte Carlo classification diagnostic and synthetic pilot record.
- These materials are supplementary methodological validation, not empirical evidence and not changes to frozen v1.1.

## Repository separation

- CFS-CTS Core 0.1 was extracted to the standalone [CFS-CTS repository](https://github.com/qq399356807/CFS-CTS). FIR-3 protocol definitions and frozen v1.1 remain unchanged.
