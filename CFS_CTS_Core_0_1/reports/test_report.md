# CFS CTS Core 0.1 — 实测报告

运行环境：Python 3.12.3 / Linux-6.18.38+-x86_64-with-glibc2.39

汇总：{'PASS': 16, 'FAIL': 0, 'BLOCKED': 1, 'INCONCLUSIVE': 0}

> 报告为本项目运行器生成。CORE-06 的 PASS 仅表示“本地同时重建可成功”的安全边界演示，不代表抵御攻击。无外部锚点。

| ID | 测试 | 状态 | 实际结果摘要 |
|---|---|---|---|
| CORE-01 | execute UTC rollback | **PASS** | {"after": {"anomalies": ["UTC_ROLLBACK", "UTC_JUMP"], "boot_id": "boot-A", "logical": 2, "monotonic": 11.0, "utc": "1970-01-01T00:16:20+00:00", "utc_epoch": 980.0}, "before": {"anomalies": [], "boot_id": "boot-A", "logic |
| CORE-02 | execute UTC jump | **PASS** | {"anomalies": ["UTC_JUMP"], "boot_id": "boot-A", "logical": 2, "monotonic": 11.0, "utc": "1970-01-01T00:18:20+00:00", "utc_epoch": 1100.0} |
| CORE-03 | execute event deletion | **PASS** | {"count": 2, "head": "0aa5505c22a53df49a806d499925e435b327c78067f41ff78d9432db97b9cf15", "issues": [{"at": 2, "found": 3, "type": "SEQUENCE"}, {"at": 2, "type": "ORDER_OR_DELETION"}], "ok": false} |
| CORE-04 | execute content tamper | **PASS** | {"count": 1, "head": "b08d8b2adcc0a875ba7b47020ec5aabbaa179646794625219baf7dff89b2ac03", "issues": [{"at": 1, "type": "HASH_MISMATCH"}], "ok": false} |
| CORE-05 | execute event reorder | **PASS** | {"count": 3, "head": "38083b0e3cf067e3dd0bcb438be680958c2326e68deed721866ffbed8bd0200c", "issues": [{"at": 2, "found": 3, "type": "SEQUENCE"}, {"at": 2, "type": "ORDER_OR_DELETION"}, {"at": 3, "found": 2, "type": "SEQUEN |
| CORE-06 | execute local ledger+anchor rebuild | **PASS** | {"classification": "LIMITATION_CONFIRMED", "external_anchor": "NOT_CONFIGURED", "local_rebuild_detected": false} |
| CORE-07 | execute simulated reboot | **PASS** | {"after_restart": {"anomalies": [], "boot_id": "boot-B", "logical": 1, "monotonic": 10.0, "utc": "1970-01-01T00:16:40+00:00", "utc_epoch": 1000.0}, "before": {"anomalies": [], "boot_id": "boot-A", "logical": 1, "monotoni |
| SEC-01 | execute concurrent writes | **PASS** | {"events": 12, "exitcodes": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} |
| SEC-02 | execute duplicate event ID | **PASS** | {"rejected": true} |
| SEC-03 | execute partial write/crash tail | **PASS** | {"detail": "truncated JSONL tail", "detected": true} |
| SEC-04 | execute JSONL truncation | **PASS** | {"detail": "truncated JSONL tail", "detected": true} |
| SEC-05 | execute anchor rollback boundary | **PASS** | {"append_only_history": 2, "rollback_of_local_file": "not protected against same-privilege rewrite"} |
| SEC-06 | execute missing parent | **PASS** | {"rejected": true} |
| SEC-07 | execute oversized event | **PASS** | {"detail": "event exceeds maximum encoded size", "rejected": true} |
| SEC-08 | execute Unicode/canonicalization | **PASS** | {"oracle": "independent checker implementation", "utf8_roundtrip": true} |
| SEC-09 | execute duplicate batch submit | **BLOCKED** | {"reason": "batch submit API is not implemented in 0.1", "status": "BLOCKED"} |
| SEC-10 | execute invalid clock input | **PASS** | {"detail": "clock source invalid: non-finite or negative clock", "rejected": true} |

## 风险/未实现

- CORE-06 uses only a local simulated anchor; full local rewrite is intentionally shown undetectable.
- No remote independently operated anchor is configured.
- Windows cross-process locking is best-effort and requires validation on Windows.
- Batch idempotency API is not implemented.
