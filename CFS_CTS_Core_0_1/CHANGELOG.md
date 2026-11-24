# Changelog

## 0.1.1 — hardening work in progress

- Fail closed when the advisory ledger lock cannot be acquired or released; do not continue an append unlocked.
- Validate that event payloads are JSON objects and preserve explicitly supplied empty objects.
- Verify every checkpoint digest in the local anchor history, not only the latest checkpoint.
- Add regression tests for lock failure and intermediate checkpoint tampering.
- Add cross-platform CI for Python 3.11–3.13 on Linux, Windows, and macOS.
- Remove empty .tmp artifacts from the test directory.
- No production security claim is implied; external anchoring and batch idempotency remain unimplemented.
