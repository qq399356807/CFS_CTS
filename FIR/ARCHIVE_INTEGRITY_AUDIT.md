# FIR Archive Integrity Audit

**Audit date:** 2026-11-24  
**Scope:** the two ZIP archives tracked at the repository root on the audited `main` commit.  
**Purpose:** document archive contents and identify divergence from the current source tree. This audit does not rewrite or delete historical archives.

## Executive result

The archives are readable ZIP files, but they are legacy snapshots rather than byte-for-byte packages of the current repository state.

- `FIR.zip` contains 12 entries: six substantive entries and six macOS `__MACOSX/._*` metadata sidecars.
- `FIR.zip` embeds `FIR-3-simulation-v1.1-validation.zip`; that embedded ZIP is byte-identical to the separately tracked `FIR-simulation-v1.1-validation.zip` (24,198 bytes; CRC-32 `e5dec6fb`). The outer archive therefore duplicates the standalone validation archive.
- Both archives retain the old `FIR-3` naming.
- The archived Python source and two Markdown documents differ from the current root files. The CSV and JSON payloads match the current root files by CRC-32.
- Preserve these archives as historical snapshots unless a separately reviewed migration explicitly replaces them. Do not cite them as the canonical current source package.

## Tracked archive objects

| Path | Size | Git blob SHA |
|---|---:|---|
| `FIR.zip` | 50,328 bytes | `d37c97074c02e1b78ce7998ce39fe7388ed470df` |
| `FIR-simulation-v1.1-validation.zip` | 24,198 bytes | `e198c0ba757410bdb59f1926c060148e5dcaf118` |

Git blob SHA identifies the repository object; it is not a ZIP-file checksum.

## Internal inventory and comparison

CRC-32 values below are taken from ZIP central-directory records and compared with CRC-32 computed from the corresponding current root file bytes.

| Archived item | Archived size | Archived CRC-32 | Current root file CRC-32 | Result |
|---|---:|---|---|---|
| `simulate_fir3.py` / current `simulate_fir.py` | 16,191 | `30a98db0` | `1c73d855` | Different; legacy source snapshot |
| archived README / `FIR 仿真验证包.md` | 3,565 | `7bd56fce` | `3497dfb0` | Different; legacy document |
| archived report / `FIR 仿真验证结果.md` | 3,626 | `5420df6f` | `1e2112d0` | Different; legacy document |
| `simulated_trials.csv` | 116,862 | `4a146edf` | `4a146edf` | Match |
| `validation_results.json` | 5,842 | `be4e6df8` | `be4e6df8` | Match |

The standalone validation ZIP contains seven entries: three directory entries and four files (Python source, README, CSV, JSON, and validation report; the directory entries account for the remaining two entries). The source and Markdown mismatches above also apply to the standalone ZIP's corresponding payloads.

## Interpretation and maintenance

1. Treat the ZIPs as frozen historical deliverables. Their old filenames and embedded `FIR-3` paths are provenance, not the current project identity.
2. Use the current tracked source files and current CI artifacts for present-day validation. The matching CSV/JSON payloads do not make the entire ZIP current.
3. Do not silently replace or delete historical archives. If a refreshed package is needed, build a new archive from a clean, versioned source tree; omit macOS sidecars; use current `FIR` naming; include a manifest with file hashes, source commit, protocol version, and build command.
4. Keep synthetic validation clearly labelled as synthetic. Archive consistency is a packaging/provenance check, not empirical validation of FIR's causal claims.

## Reproduction

The audit was performed by listing each ZIP central directory, recording entry names/sizes/CRC-32 values, and comparing archived payload CRC-32 values with the corresponding current root files. The nested and standalone validation ZIPs were compared by size and whole-file CRC-32.

This document records the state of the archives at the audit date; rerun the checks if either ZIP or its source files change.
