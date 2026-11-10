# CFS CTS Core 0.1

Chronological Trust & Security core, Python 3.11+. Standard library only. This is a prototype audit component, **not a production tamper-proof logging system**.

## Run

```bash
python3 run_tests.py
```

The first command executes the deterministic adversarial test suite and writes `reports/test_report.json` and `.md`. The report distinguishes PASS/FAIL/BLOCKED/INCONCLUSIVE. Test data lives in temporary directories. A nonzero process status indicates a failing test.

## API quick start

```python
from src.timebase import TimeBase
from src.event_ledger import EventLedger
from src.audit_anchor import LocalSimulatedAnchor
from src.integrity_checker import IntegrityChecker

clock = TimeBase()
ledger = EventLedger('events.jsonl', clock)
event = ledger.append('evt-001', {'action': 'created'})
anchor = LocalSimulatedAnchor('anchor.jsonl')  # simulated, same-host trust only
ledger.anchor(anchor)
print(IntegrityChecker().check(ledger.events(), anchor))
```

## Components

- `TimeBase`: UTC and monotonic samples, process logical counter, boot/session ID, rollback and UTC jump flags. Default boot ID is a random process-session identifier, not an OS-certified boot UUID.
- `EventLedger`: canonical UTF-8 JSONL, sequence, unique IDs, SHA-256 chain, parent validation, bounded event size, fsync and best-effort cooperating-process lock.
- `CausalTracker`: explicit parent/related edges; timestamp proximity creates no causal edge.
- `IntegrityChecker`: independent canonical JSON/hash implementation checks sequence, IDs, chain, parent references and anchor.
- `LocalSimulatedAnchor`: append-only-on-cooperating-writes local journal with sequence/checkpoint. It is **not** an external trust root.
- `AnchorProtocol`: extension interface for remote independently administered service; no remote implementation/credentials are included.

## Security boundaries and known risks

A same-privilege attacker can replace both ledger and local anchor, or truncate both. CORE-06 deliberately tests that condition; only a separately administered, authenticated remote anchor can detect it. The current local journal is not cryptographically signed. SHA-256 is unkeyed. There is no batch API or retry idempotency. An interrupted append leaves a detectable invalid tail but no automatic recovery/repair (repair must preserve forensic evidence). `flock`/Windows locking is best-effort; network filesystems and Windows need dedicated validation. Boot ID is session-generated. Wall time is advisory, monotonic clocks reset across reboot. Checksums do not ensure confidentiality or availability. Do not use as the sole source for safety-critical or legal audit decisions.

## Layout

`src/` implementation; `tests/` attack/regression cases; `reports/` generated actual run results. Test fixtures and the tested classes are distinct; integrity verification has a separately written canonicalization/hash path. This reduces common-mode risk but is not formal verification.
