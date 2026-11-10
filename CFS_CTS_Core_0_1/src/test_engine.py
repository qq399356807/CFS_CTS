"""Small test result model; never equates skipped work with success."""
from dataclasses import dataclass,asdict
@dataclass
class TestResult:
    test_id:str; status:str; initial:str; steps:list; expected:str; actual:str; rationale:str; logs:list
    def __post_init__(self):
        if self.status not in {'PASS','FAIL','BLOCKED','INCONCLUSIVE'}: raise ValueError('invalid status')
    def as_dict(self): return asdict(self)
