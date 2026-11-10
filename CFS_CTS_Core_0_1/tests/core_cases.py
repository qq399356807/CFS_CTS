import json
from .common import Fixture

def core01():
 f=Fixture(); a=f.tb.sample(); f.clock.u-=20; f.clock.m+=1; b=f.tb.sample(); assert b['logical']>a['logical'] and 'UTC_ROLLBACK' in b['anomalies']; return {'before':a,'after':b}
def core02():
 f=Fixture(); f.tb.sample(); f.clock.u+=100; f.clock.m+=1; x=f.tb.sample(); assert 'UTC_JUMP' in x['anomalies']; return x
def core03():
 f=Fixture(); [f.add(f'e{i}') for i in range(3)]; rows=f.ledger.events(); f.ledger.path.write_text(json.dumps(rows[0])+'\n'+json.dumps(rows[2])+'\n'); r=f.checker.check(f.ledger.events()); assert any(i['type']=='ORDER_OR_DELETION' for i in r['issues']); return r
def core04():
 f=Fixture(); f.add(); rows=f.ledger.events(); rows[0]['payload']['v']=99; f.ledger.path.write_text(''.join(json.dumps(x)+'\n' for x in rows)); r=f.checker.check(f.ledger.events()); assert any(i['type']=='HASH_MISMATCH' for i in r['issues']); return r
def core05():
 f=Fixture(); [f.add(f'e{i}') for i in range(3)]; rows=f.ledger.events(); rows[1],rows[2]=rows[2],rows[1]; f.ledger.path.write_text(''.join(json.dumps(x)+'\n' for x in rows)); r=f.checker.check(f.ledger.events()); assert r['issues']; return r
def core06():
 f=Fixture(); f.add('original',{'value':'trusted'}); f.ledger.anchor(f.anchor); f.ledger.path.unlink(); f.anchor.path.unlink(); f.add('forged',{'value':'rewritten'}); f.ledger.anchor(f.anchor); r=f.checker.check(f.ledger.events(),f.anchor); assert r['ok']; return {'local_rebuild_detected':False,'external_anchor':'NOT_CONFIGURED','classification':'LIMITATION_CONFIRMED'}
def core07():
 f=Fixture(); old=f.tb.sample(); fresh=type(f.tb)(f.clock.utc,f.clock.mono,boot_id='boot-B'); now=fresh.sample(); assert old['boot_id']!=now['boot_id'] and now['logical']==1; return {'before':old,'after_restart':now}
