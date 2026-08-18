from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from core.models import NormalizedRecord, ResourceSpec

from .port import SupabaseWriterPort


@dataclass(slots=True)
class InMemorySupabaseSink(SupabaseWriterPort):
    written: list[tuple[str, int]] = field(default_factory=list)
    records: dict[tuple[str, str], NormalizedRecord] = field(default_factory=dict)

    def upsert(self, resource: ResourceSpec, records: Sequence[NormalizedRecord]) -> None:
        for record in records:
            self.records[(resource.name.value, record.external_id)] = record
        self.written.append((resource.name.value, len(records)))
