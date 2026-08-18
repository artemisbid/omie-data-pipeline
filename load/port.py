from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from core.models import NormalizedRecord, ResourceSpec


class SupabaseWriterPort(Protocol):
    def upsert(self, resource: ResourceSpec, records: Sequence[NormalizedRecord]) -> None: ...

