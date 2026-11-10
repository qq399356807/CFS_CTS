#!/usr/bin/env python3
import json, platform, sys, traceback, time
from pathlib import Path
from src.test_engine import TestResult
from src.timebase import TimeBase
from src.event_ledger import EventLedger
from src.integrity_checker import IntegrityChecker
from src.audit_anchor import LocalSimulatedAnchor
from src.causal_tracker import CausalTracker
from tests import test_core_01,test_core_02,test_core_03,test_core_04,test_core_05,test_core_06,test_core_07,test_security_extra as sec

def main():
 cases=[('CORE-01','UTC rollback',test_core_01.run),('CORE-02','UTC jump',test_core_02.run),('CORE-03','event deletion',test_core_03.run),('CORE-04','content tamper',test_core_04.run),('CORE-05','event reorder',test_core_05.run),('CORE-06','local ledger+anchor rebuild',test_core_06.run),('CORE-07','simulated reboot',test_core_07.run),('SEC-01','concurrent writes',sec.test_concurrency),('SEC-02','duplicate event ID',sec.test_duplicate_id),('SEC-03','partial write/crash tail',sec.test_crash_partial),('SEC-04','JSONL truncation',sec.test_truncation),('SEC-05','anchor rollback boundary',sec.test_anchor_rollback),('SEC-06','missing parent',sec.test_missing_parent),('SEC-07','oversized event',sec.test_large_event),('SEC-08','Unicode/canonicalization',sec.test_unicode_canonical),('SEC-09','duplicate batch submit',sec.test_duplicate_batch),('SEC-10','invalid clock input',sec.test_bad_clock)]
 out=[]
 for ident,name,fn in cases:
  started=time.time()
  try:
   actual=fn()
   blocked=isinstance(actual,dict) and actual.get('status')=='BLOCKED'
   status='BLOCKED' if blocked else 'PASS'
   out.append(TestResult(ident,status,'isolated temporary directory or deterministic injected clock',[f'execute {name}'], 'security property or explicit boundary behavior',json.dumps(actual,ensure_ascii=False,sort_keys=True), 'PASS means the expected test oracle assertion held; CORE-06 PASS specifically confirms the limitation, not external security.',[f'elapsed={time.time()-started:.6f}s',repr(actual)]).as_dict())
  except Exception as e:
   out.append(TestResult(ident,'FAIL','isolated temporary directory or deterministic injected clock',[f'execute {name}'],'expected assertion',f'{type(e).__name__}: {e}','exception or assertion means observed behavior did not match test expectation',[traceback.format_exc()]).as_dict())
 report={'project':'CFS CTS Core','version':'0.1','python':sys.version,'platform':platform.platform(),'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'external_anchor_configured':False,'summary':{s:sum(x['status']==s for x in out) for s in ('PASS','FAIL','BLOCKED','INCONCLUSIVE')},'tests':out,'limitations':['CORE-06 uses only a local simulated anchor; full local rewrite is intentionally shown undetectable.','No remote independently operated anchor is configured.','Windows cross-process locking is best-effort and requires validation on Windows.','Batch idempotency API is not implemented.']}
 Path('reports/test_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 lines=['# CFS CTS Core 0.1 — 实测报告','',f"运行环境：Python {sys.version.split()[0]} / {platform.platform()}",'',f"汇总：{report['summary']}",'','> 报告为本项目运行器生成。CORE-06 的 PASS 仅表示“本地同时重建可成功”的安全边界演示，不代表抵御攻击。无外部锚点。','','| ID | 测试 | 状态 | 实际结果摘要 |','|---|---|---|---|']
 for x in out: lines.append(f"| {x['test_id']} | {x['steps'][0]} | **{x['status']}** | {x['actual'][:220].replace('|','\\|')} |")
 lines += ['','## 风险/未实现','']+[f'- {v}' for v in report['limitations']]
 Path('reports/test_report.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(report['summary'],ensure_ascii=False)); print(f"Reports: reports/test_report.json and reports/test_report.md")
 return 1 if report['summary']['FAIL'] else 0
if __name__=='__main__': raise SystemExit(main())
