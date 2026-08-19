from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from core.models import ExecutionMode, RawPage, ResourceSpec, RunContext
from core.ports import ExtractorPort

from .omie_client import OmieClient


@dataclass(slots=True)
class ExtractWorker(ExtractorPort):
    client: OmieClient
    default_page_size: int = 50
    max_pages: int | None = None

    def extract(self, resource: ResourceSpec, context: RunContext, mode: ExecutionMode) -> Iterable[RawPage]:
        extra_params: dict[str, Any] = dict(resource.metadata.get("request_defaults", {}))

        if mode == ExecutionMode.INCREMENTAL and resource.supports_incremental:
            extra_params.setdefault("filtrar_por_data_de", "")
            extra_params.setdefault("filtrar_por_data_ate", "")

        page_size = resource.page_size or self.default_page_size
        return self.client.list_pages(resource, page_size=page_size, extra_params=extra_params, max_pages=self.max_pages)
