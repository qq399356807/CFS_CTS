"""Independent integrity verifier. Uses a separately written canonicalization/hash path."""
import hashlib, json
GENESIS='0'*64
class IntegrityChecker:
    @staticmethod
    def _oracle_hash(core):
        # Deliberately separate from ledger._digest; this implementation is an independent test/verification path.
        text=json.dumps(core,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    def check(self,events,anchor=None):
        issues=[]; ids=set(); prev=GENESIS
        for idx,e in enumerate(events,1):
            if e.get('seq')!=idx: issues.append({'type':'SEQUENCE','at':idx,'found':e.get('seq')})
            if e.get('event_id') in ids: issues.append({'type':'DUPLICATE_ID','at':idx})
            ids.add(e.get('event_id'))
            if e.get('prev_hash')!=prev: issues.append({'type':'ORDER_OR_DELETION','at':idx})
            core={k:v for k,v in e.items() if k!='hash'}
            try: expected=self._oracle_hash(core)
            except Exception as ex: issues.append({'type':'CANONICALIZATION','at':idx,'detail':str(ex)}); expected=None
            if expected != e.get('hash'): issues.append({'type':'HASH_MISMATCH','at':idx})
            prev=e.get('hash','')
            for p in e.get('parents',[]):
                if p not in ids-{e.get('event_id')}: issues.append({'type':'MISSING_OR_FORWARD_PARENT','at':idx,'parent':p})
        if anchor is not None:
            latest=anchor.latest()
            if latest:
                if latest.get('ledger_seq')!=len(events) or latest.get('head')!=(events[-1].get('hash') if events else GENESIS): issues.append({'type':'ANCHOR_MISMATCH'})
                from .audit_anchor import checkpoint_digest
                if latest.get('checkpoint_digest')!=checkpoint_digest(latest.get('ledger_version'),latest.get('ledger_seq'),latest.get('head')): issues.append({'type':'ANCHOR_DIGEST_MISMATCH'})
                hist=getattr(anchor,'history',lambda:[])()
                if any(hist[i].get('anchor_seq') != hist[i-1].get('anchor_seq',0)+1 for i in range(1,len(hist))): issues.append({'type':'ANCHOR_ROLLBACK_OR_GAP'})
        return {'ok':not issues,'count':len(events),'issues':issues,'head':prev}
