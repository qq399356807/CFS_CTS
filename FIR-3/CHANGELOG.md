# FIR-3 Archive Changelog

## 2026-11-24 — Repository management baseline

- Added research archive index, status register, frozen-protocol boundary, and analysis plan.
- Preserved existing v1.1 simulation outputs and source archives.
- Corrected the simulation point-summary helper so it no longer emits point estimates under misleading `ci_low` / `ci_high` names. Bootstrap intervals remain in explicit `bootstrap_ci95` fields.
- Added a supplementary nested predictive diagnostic comparing A-only with A+B. Exploratory; does not amend v1.1.
- Added GitHub Actions continuous validation. No public service deployment is claimed.
