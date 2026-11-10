"""Append-only JSONL ledger. Per-process/thread locking; cross-process locking is platform best-effort."""
from __future__ import annotations
import hashlib, json, os, threading, uuid
from pathlib import Path
from .audit_anchor import canonical_bytes
from .causal_tracker import CausalTracker
GENESIS='0'*64
class EventLedger:
    VERSION='CFS-CTS-LEDGER-1'
    MAX_EVENT_BYTES=1_048_576
    def __init__(self,path,timebase,causal=None): self.path=Path(path); self.timebase=timebase; self.causal=causal or CausalTracker(); self.lock=threading.RLock(); self.path.parent.mkdir(parents=True,exist_ok=True)
    def _read(self):
        if not self.path.exists(): return []
        raw=self.path.read_bytes()
        if raw and not raw.endswith(b'\n'): raise ValueError('truncated JSONL tail')
        rows=[]
        for i,line in enumerate(raw.splitlines(),1):
            try: rows.append(json.loads(line))
            except Exception as e: raise ValueError(f'invalid JSON at line {i}: {e}')
        return rows
    @staticmethod
    def _digest(core): return hashlib.sha256(canonical_bytes(core)).hexdigest()
    def append(self,event_id=None,payload=None,parents=None,related=None):
        with self.lock:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            # Sidecar lock serializes the full read/derive/append transaction across cooperating processes.
            with open(str(self.path)+'.lock','a+b') as lockfile:
                _lock(lockfile)
                try:
                    rows=self._read(); ids={r['event_id'] for r in rows}; seq=len(rows)+1
                    eid=str(event_id or uuid.uuid4())
                    if eid in ids: raise ValueError('duplicate event_id')
                    check=self.causal.validate(eid,parents or [],ids,seq,{r['event_id']:r['seq'] for r in rows})
                    if not check['ok']: raise ValueError(check)
                    ts=self.timebase.sample(); core={'version':self.VERSION,'seq':seq,'event_id':eid,'timestamp':ts,'payload':payload or {},'parents':list(parents or []),'related':list(related or []),'prev_hash':rows[-1]['hash'] if rows else GENESIS}
                    encoded=canonical_bytes(core)
                    if len(encoded)>self.MAX_EVENT_BYTES: raise ValueError('event exceeds maximum encoded size')
                    record={**core,'hash':self._digest(core)}; data=canonical_bytes(record)+b'\n'
                    with self.path.open('ab') as f:
                        f.write(data); f.flush(); os.fsync(f.fileno())
                    return record
                finally:
                    _unlock(lockfile)
    def events(self):
        with self.lock: return self._read()
    def head(self):
        rows=self.events(); return (len(rows),rows[-1]['hash'] if rows else GENESIS)
    def anchor(self,anchor):
        seq,head=self.head(); prior=anchor.latest(); n=(prior['anchor_seq']+1) if prior else 1
        from .audit_anchor import checkpoint_digest
        cp={'anchor_seq':n,'ledger_version':self.VERSION,'ledger_seq':seq,'head':head}
        cp['checkpoint_digest']=checkpoint_digest(self.VERSION,seq,head)
        return anchor.commit(cp)
def _lock(f):
    try:
        if os.name=='nt':
            import msvcrt; f.seek(0); msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl; fcntl.flock(f.fileno(),fcntl.LOCK_EX)
    except (ImportError,OSError): pass
def _unlock(f):
    try:
        if os.name=='nt':
            import msvcrt; f.seek(0); msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
        else:
            import fcntl; fcntl.flock(f.fileno(),fcntl.LOCK_UN)
    except (ImportError,OSError): pass
