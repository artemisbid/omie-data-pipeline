from __future__ import annotations

from collections.abc import Mapping

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceName, ResourceSpec


def transform_records(
    resource: ResourceSpec,
    pages: list[RawPage],
    payload_key: str,
) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    normalized: list[NormalizedRecord] = []
    rejected: list[RejectedRecord] = []
    seen_keys: set[str] = set()

    for page in pages:
        items = page.payload.get(payload_key, [])
        if not isinstance(items, list):
            rejected.append(
                RejectedRecord(source=resource.name, source_payload=page.payload, reason=f"{payload_key} payload invalid")
            )
            continue

        for item in items:
            if not isinstance(item, Mapping):
                rejected.append(
                    RejectedRecord(source=resource.name, source_payload=page.payload, reason="item payload invalid")
                )
                continue

            stable_key_candidates = [resource.stable_key, *resource.metadata.get("stable_key_candidates", [])]
            external_id = ""
            for candidate in stable_key_candidates:
                external_id = str(item.get(candidate, "")).strip()
                if external_id:
                    break

            if not external_id:
                rejected.append(RejectedRecord(source=resource.name, source_payload=item, reason="missing stable key"))
                continue

            if external_id in seen_keys:
                rejected.append(RejectedRecord(source=resource.name, source_payload=item, reason="duplicate stable key"))
                continue
            seen_keys.add(external_id)

            normalized.append(
                NormalizedRecord(
                    source=resource.name,
                    external_id=external_id,
                    data=dict(item),
                    source_payload=page.payload,
                )
            )

    return normalized, rejected


def transform_customers(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    return transform_records(resource, pages, payload_key=str(resource.metadata.get("payload_key", "clientes")))
