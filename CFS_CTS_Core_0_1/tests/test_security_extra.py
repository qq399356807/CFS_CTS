import json, multiprocessing, os, tempfile, time
from pathlib import Path
from .common import Fixture
from src.integrity_checker import IntegrityChecker

def _worker(path,n):
 from src.event_ledger import EventLedger
 from src.timebase import TimeBase
 l=EventLedger(path,TimeBase()); l.append(f'concurrent-{n}',{'n':n})

def test_concurrency():
 with tempfile.TemporaryDirectory() as d:
  p=str(Path(d)/'l.jsonl'); ps=[multiprocessing.Process(target=_worker,args=(p,i)) for i in range(12)]
  [x.start() for x in ps]; [x.join(10) for x in ps]; assert all(x.exitcode==0 for x in ps)
  rows=[json.loads(x) for x in Path(p).read_text().splitlines()]; assert len(rows)==12 and len({x['event_id'] for x in rows})==12 and IntegrityChecker().check(rows)['ok']; return {'events':len(rows),'exitcodes':[x.exitcode for x in ps]}
def test_duplicate_id():
 f=Fixture(); f.add('same')
 try: f.add('same')
 except ValueError: return {'rejected':True}
 raise AssertionError('duplicate accepted')
def test_crash_partial():
 f=Fixture(); f.add(); with_open=f.ledger.path
 with with_open.open('ab') as s: s.write(b'{"partial":')
 try: f.ledger.events()
 except ValueError as e: assert 'truncated' in str(e); return {'detected':True,'detail':str(e)}
 raise AssertionError('truncated tail accepted')
def test_truncation(): return test_crash_partial()
def test_anchor_rollback():
 f=Fixture(); f.add(); f.ledger.anchor(f.anchor); first=f.anchor.latest(); f.add('second'); f.ledger.anchor(f.anchor); hist=f.anchor.history(); assert len(hist)==2 and hist[0]==first and hist[1]['anchor_seq']==2; return {'append_only_history':len(hist),'rollback_of_local_file':'not protected against same-privilege rewrite'}
def test_missing_parent():
 f=Fixture()
 try: f.add('child',parents=['absent'])
 except ValueError: return {'rejected':True}
 raise AssertionError('missing parent accepted')
def test_large_event():
 f=Fixture()
 try: f.add('large',{'blob':'x'*(EventLedgerLimit())})
 except ValueError as e: return {'rejected':True,'detail':str(e)}
 raise AssertionError('oversize event accepted')
def EventLedgerLimit(): return 1_100_000
def test_unicode_canonical():
 f=Fixture(); f.add('unicode',{'text':'雪☃️ café','number':1.0}); assert f.checker.check(f.ledger.events())['ok']; return {'utf8_roundtrip':True,'oracle':'independent checker implementation'}
def test_duplicate_batch():
 # No batch API exists; per-event idempotent retries are explicitly not implemented.
 return {'status':'BLOCKED','reason':'batch submit API is not implemented in 0.1'}
def test_bad_clock():
 from src.timebase import TimeBase
 def bad(): return float('nan')
 try: TimeBase(bad,lambda:1).sample()
 except RuntimeError as e: return {'rejected':True,'detail':str(e)}
 raise AssertionError('bad clock accepted')
