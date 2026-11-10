"""UTC, monotonic and logical clocks; UTC is advisory, never the sole trust source."""
from __future__ import annotations
import uuid, time
from datetime import datetime, timezone
from typing import Callable

class TimeBase:
    def __init__(self, utc: Callable[[], float] = time.time, mono: Callable[[], float] = time.monotonic,
                 boot_id: str | None = None, jump_threshold: float = 5.0):
        self._utc, self._mono = utc, mono
        self.boot_id = boot_id or str(uuid.uuid4())
        self.jump_threshold = float(jump_threshold)
        self._last_utc = None
        self._last_mono = None
        self.logical = 0
    def sample(self) -> dict:
        try:
            u, m = float(self._utc()), float(self._mono())
            if not (u >= 0 and m >= 0 and u < float('inf') and m < float('inf')): raise ValueError('non-finite or negative clock')
        except Exception as e:
            raise RuntimeError(f'clock source invalid: {e}') from e
        flags=[]
        if self._last_utc is not None:
            du, dm = u-self._last_utc, m-self._last_mono
            if du < 0: flags.append('UTC_ROLLBACK')
            if dm < 0: flags.append('MONOTONIC_ROLLBACK')
            if abs(du-dm) > self.jump_threshold: flags.append('UTC_JUMP')
        self.logical += 1
        self._last_utc, self._last_mono = u,m
        return {'utc': datetime.fromtimestamp(u, timezone.utc).isoformat(), 'utc_epoch':u,
                'monotonic':m,'logical':self.logical,'boot_id':self.boot_id,'anomalies':flags}
