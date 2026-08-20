from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceSpec


def _text(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def transform_categories(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    valid: list[NormalizedRecord] = []
    rejected: list[RejectedRecord] = []
    seen: set[str] = set()
    candidates = resource.metadata.get("payload_key_candidates", ())

    for page in pages:
        items: list[Mapping[str, Any]] | None = None
        for key in candidates:
            value = page.payload.get(str(key))
            if isinstance(value, list):
                items = [item for item in value if isinstance(item, Mapping)]
                break
        if items is None:
            rejected.append(RejectedRecord(resource.name, page.payload, "categories payload invalid"))
            continue
        for item in items:
            external_id = _text(item.get("codigo"))
            if not external_id:
                rejected.append(RejectedRecord(resource.name, item, "missing stable key"))
                continue
            if external_id in seen:
                rejected.append(RejectedRecord(resource.name, item, "duplicate stable key"))
                continue
            seen.add(external_id)
            parts = external_id.split(".")
            valid.append(
                NormalizedRecord(
                    resource.name,
                    external_id,
                    {
                        "category_id": item.get("codigo"),
                        "category_code": external_id,
                        "parent_category_code": ".".join(parts[:-1]) if len(parts) > 1 else None,
                        "category_level": len(parts),
                        "name": _text(item.get("descricao")),
                        "standard_name": _text(item.get("descricao_padrao")),
                        "parent_category": _text(item.get("categoria_superior")),
                        "dre_code": _text(item.get("codigo_dre")),
                        "nature": _text(item.get("natureza")),
                        "category_type": _text(item.get("tipo_categoria")),
                        "inactive": _text(item.get("conta_inativa")) == "S",
                    },
                    item,
                )
            )
    return valid, rejected
