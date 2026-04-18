from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class RoundTimer:
    duration_seconds: float
    _start_time: float | None = field(default=None, init=False)

    def start(self) -> None:
        self._start_time = time.monotonic()

    @property
    def elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.monotonic() - self._start_time

    @property
    def remaining(self) -> float:
        return max(0.0, self.duration_seconds - self.elapsed)

    @property
    def is_expired(self) -> bool:
        return self.remaining <= 0.0
