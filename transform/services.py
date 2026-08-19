from __future__ import annotations

from collections.abc import Mapping
from html import unescape
from typing import Any

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceSpec


def _get(item: Mapping[str, Any], path: str, default: Any = "") -> Any:
    value: Any = item
    for part in path.split("."):
        if not isinstance(value, Mapping):
            return default
        value = value.get(part, default)
    return value


def _text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = unescape(str(value)).strip()
    return normalized or None


def _number(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def _date(value: Any) -> str | None:
    text = _text(value)
    if not text:
        return None
    parts = text.split("/")
    if len(parts) == 3 and len(parts[2]) == 4:
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return text


def _normalize_service(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "service_id": _number(_get(item, "intListar.nCodServ")),
        "integration_code": _text(_get(item, "intListar.cCodIntServ")),
        "service_code": _text(_get(item, "cabecalho.cCodigo")),
        "name": _text(_get(item, "cabecalho.cDescricao")),
        "description": _text(_get(item, "descricao.cDescrCompleta")),
        "category_code": _text(_get(item, "cabecalho.cCodCateg")),
        "municipal_service_code": _text(_get(item, "cabecalho.cCodServMun")),
        "lc116_code": _text(_get(item, "cabecalho.cCodLC116")),
        "taxation_code": _text(_get(item, "cabecalho.cIdTrib")),
        "nbs_code": _text(_get(item, "cabecalho.nIdNBS")),
        "unit_price": _number(_get(item, "cabecalho.nPrecoUnit")),
        "discount_value": _number(_get(item, "cabecalho.nValorDesc")),
        "discount_rate": _number(_get(item, "cabecalho.nAliqDesc")),
        "iss_rate": _number(_get(item, "impostos.nAliqISS")),
        "pis_rate": _number(_get(item, "impostos.nAliqPIS")),
        "cofins_rate": _number(_get(item, "impostos.nAliqCOFINS")),
        "csll_rate": _number(_get(item, "impostos.nAliqCSLL")),
        "ir_rate": _number(_get(item, "impostos.nAliqIR")),
        "inss_rate": _number(_get(item, "impostos.nAliqINSS")),
        "iss_withheld": _text(_get(item, "impostos.cRetISS")),
        "pis_withheld": _text(_get(item, "impostos.cRetPIS")),
        "cofins_withheld": _text(_get(item, "impostos.cRetCOFINS")),
        "inss_withheld": _text(_get(item, "impostos.cRetINSS")),
        "active": _text(_get(item, "info.inativo")) != "S",
        "imported_by_api": _text(_get(item, "info.cImpAPI")) == "S",
        "created_at": _date(_get(item, "info.dInc")),
        "updated_at": _date(_get(item, "info.dAlt")),
    }


def transform_services(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    normalized: list[NormalizedRecord] = []
    rejected: list[RejectedRecord] = []
    seen_ids: set[str] = set()
    payload_key = str(resource.metadata.get("payload_key", "cadastros"))

    for page in pages:
        items = page.payload.get(payload_key, [])
        if not isinstance(items, list):
            rejected.append(RejectedRecord(resource.name, page.payload, f"{payload_key} payload invalid"))
            continue

        for item in items:
            if not isinstance(item, Mapping):
                rejected.append(RejectedRecord(resource.name, page.payload, "item payload invalid"))
                continue
            external_id = str(_get(item, "intListar.nCodServ", "")).strip()
            if not external_id:
                rejected.append(RejectedRecord(resource.name, item, "missing service id"))
                continue
            if external_id in seen_ids:
                rejected.append(RejectedRecord(resource.name, item, "duplicate stable key"))
                continue
            seen_ids.add(external_id)
            normalized.append(
                NormalizedRecord(
                    source=resource.name,
                    external_id=external_id,
                    data=_normalize_service(item),
                    source_payload=item,
                )
            )

    return normalized, rejected
