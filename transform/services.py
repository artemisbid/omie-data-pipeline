from __future__ import annotations

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceSpec

from .customers import transform_records


def transform_services(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    return transform_records(resource, pages, payload_key=str(resource.metadata.get("payload_key", "cadastros")))
