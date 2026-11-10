import tempfile
from pathlib import Path
from src.timebase import TimeBase
from src.event_ledger import EventLedger
from src.audit_anchor import LocalSimulatedAnchor
from src.integrity_checker import IntegrityChecker
class Clock:
 def __init__(self,u=1000,m=10): self.u=u; self.m=m
 def utc(self): return self.u
 def mono(self): return self.m
class Fixture:
 def __init__(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.clock=Clock(); self.tb=TimeBase(self.clock.utc,self.clock.mono,boot_id='boot-A',jump_threshold=2); self.ledger=EventLedger(self.root/'events.jsonl',self.tb); self.checker=IntegrityChecker(); self.anchor=LocalSimulatedAnchor(self.root/'anchor.jsonl')
 def add(self,eid='e1',payload=None,parents=None): return self.ledger.append(eid,payload or {'v':1},parents)
 def close(self): self.tmp.cleanup()
