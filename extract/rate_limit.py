from __future__ import annotations

from dataclasses import dataclass
from time import sleep


@dataclass(slots=True)
class RetryPolicy:
    max_retries: int = 3
    base_delay_seconds: float = 1.0

    def wait(self, attempt: int) -> None:
        sleep(self.base_delay_seconds * max(1, attempt))

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_retries
