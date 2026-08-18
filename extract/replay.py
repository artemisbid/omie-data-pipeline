from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from core.models import ExecutionMode, RawPage, ResourceSpec, RunContext
from core.ports import ExtractorPort

from .raw_store import LocalRawStore


@dataclass(slots=True)
class ReplayExtractor(ExtractorPort):
    raw_store: LocalRawStore

    def extract(self, resource: ResourceSpec, context: RunContext, mode: ExecutionMode) -> Iterable[RawPage]:
        if mode != ExecutionMode.REPLAY:
            raise ValueError("ReplayExtractor only supports replay mode")
        return self.raw_store.read_pages(context, resource)
