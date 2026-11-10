"""Explicit causal relationships; proximity in time is never treated as causality."""
class CausalTracker:
    def validate(self, event_id, parents, known_ids, current_seq=None, parent_seq=None):
        parents=list(parents or [])
        if len(set(parents)) != len(parents): return {'ok':False,'issue':'DUPLICATE_PARENT'}
        missing=[p for p in parents if p not in known_ids]
        if missing: return {'ok':False,'issue':'MISSING_PARENT','missing':missing}
        if parent_seq and current_seq is not None and any(parent_seq.get(p, current_seq) >= current_seq for p in parents):
            return {'ok':False,'issue':'CAUSAL_ORDER'}
        return {'ok':True,'issue':None}
    @staticmethod
    def unknown(): return {'causality':'unknown','parents':[]}
