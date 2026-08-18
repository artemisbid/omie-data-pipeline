from __future__ import annotations

from dataclasses import dataclass

from collections.abc import Sequence

from core.models import NormalizedRecord, ResourceSpec

from .port import SupabaseWriterPort


@dataclass(slots=True)
class LoadWorker:
    sink: SupabaseWriterPort

    def load(self, resource: ResourceSpec, records: Sequence[NormalizedRecord]) -> None:
        self.sink.upsert(resource, records)
