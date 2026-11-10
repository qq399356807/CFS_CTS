"""Local simulated anchor and protocol interface. Local file is NOT an external trust root."""
from __future__ import annotations
import hashlib, json, os, threading
from pathlib import Path

def canonical_bytes(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def checkpoint_digest(version, seq, head): return hashlib.sha256(canonical_bytes({'version':version,'seq':seq,'head':head})).hexdigest()
class AnchorProtocol:
    def commit(self, checkpoint: dict) -> dict: raise NotImplementedError
    def latest(self) -> dict | None: raise NotImplementedError
class LocalSimulatedAnchor(AnchorProtocol):
    SIMULATED=True
    def __init__(self,path): self.path=Path(path); self.lock=threading.Lock()
    def _load(self):
        if not self.path.exists(): return []
        raw=self.path.read_bytes()
        if raw and not raw.endswith(b'\n'): raise ValueError('truncated anchor journal')
        return [json.loads(x) for x in raw.splitlines() if x]
    def commit(self, checkpoint):
        with self.lock:
            history=self._load()
            if history and checkpoint['anchor_seq'] != history[-1]['anchor_seq']+1: raise ValueError('anchor sequence must increment')
            if not history and checkpoint['anchor_seq'] != 1: raise ValueError('first anchor sequence must be 1')
            if history and checkpoint['ledger_seq'] < history[-1]['ledger_seq']: raise ValueError('ledger rollback')
            data=canonical_bytes(checkpoint)+b'\n'
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open('ab') as f: f.write(data); f.flush(); os.fsync(f.fileno())
            return checkpoint
    def latest(self):
        with self.lock:
            h=self._load(); return h[-1] if h else None
    def history(self): return self._load()
