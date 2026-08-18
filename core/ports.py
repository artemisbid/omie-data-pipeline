from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Protocol

from .models import (
    ExecutionMode,
    NormalizedRecord,
    RawPage,
    RawRunManifest,
    RejectedRecord,
    ResourceSpec,
    RunContext,
)


class ResourceCatalog(Protocol):
    def list(self) -> Sequence[ResourceSpec]: ...

    def get(self, name: str) -> ResourceSpec: ...


class ExtractorPort(Protocol):
    def extract(self, resource: ResourceSpec, context: RunContext, mode: ExecutionMode) -> Iterable[RawPage]: ...


class RawStorePort(Protocol):
    def write_page(self, context: RunContext, resource: ResourceSpec, page: RawPage) -> None: ...

    def write_manifest(self, context: RunContext, manifest: RawRunManifest) -> None: ...

    def write_rejections(
        self,
        context: RunContext,
        resource: ResourceSpec,
        rejected: Sequence[RejectedRecord],
    ) -> None: ...

    def read_pages(self, context: RunContext, resource: ResourceSpec) -> Sequence[RawPage]: ...


class TransformerPort(Protocol):
    def transform(self, resource: ResourceSpec, pages: Iterable[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]: ...


class LoaderPort(Protocol):
    def load(self, resource: ResourceSpec, records: Sequence[NormalizedRecord]) -> None: ...


class CheckpointStorePort(Protocol):
    def get(self, resource_name: str) -> str | None: ...

    def set(self, resource_name: str, checkpoint: str) -> None: ...
