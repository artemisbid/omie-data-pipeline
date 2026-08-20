from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceName, ResourceSpec


def _text(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _items(resource: ResourceSpec, page: RawPage) -> list[Mapping[str, Any]] | None:
    for key in resource.metadata.get("payload_key_candidates", ()):
        value = page.payload.get(str(key))
        if isinstance(value, list):
            return [item for item in value if isinstance(item, Mapping)]
    # Some non-paginated API responses are already represented as a list by a fixture.
    if isinstance(page.payload, list):
        return [item for item in page.payload if isinstance(item, Mapping)]
    return None


def _data(resource_name: ResourceName, item: Mapping[str, Any]) -> dict[str, Any]:
    if resource_name == ResourceName.DRE_ACCOUNTS:
        return {
            "dre_code": _text(item.get("codigoDRE")),
            "description": _text(item.get("descricaoDRE")),
            "hidden": _text(item.get("naoExibirDRE")) == "S",
            "level": item.get("nivelDRE"),
            "sign": _text(item.get("sinalDRE")),
            "totalizer": _text(item.get("totalizaDRE")) == "S",
        }
    if resource_name == ResourceName.DEPARTMENTS:
        return {"department_code": _text(item.get("codigo")), "name": _text(item.get("descricao")), "structure": _text(item.get("estrutura")), "inactive": _text(item.get("inativo")) == "S"}
    if resource_name == ResourceName.PROJECTS:
        return {"project_id": item.get("codigo"), "integration_code": _text(item.get("codInt")), "name": _text(item.get("nome")), "inactive": _text(item.get("inativo")) == "S"}
    return {
        "bank_account_id": item.get("nCodCC"),
        "integration_code": _text(item.get("cCodCCInt")),
        "name": _text(item.get("descricao")),
        "bank_code": _text(item.get("codigo_banco")),
        "branch_code": _text(item.get("codigo_agencia")),
        "account_number": _text(item.get("numero_conta_corrente")),
        "account_type": _text(item.get("tipo_conta_corrente")),
        "inactive": _text(item.get("inativo")) == "S",
        "blocked": _text(item.get("bloqueado")) == "S",
        "excluded_from_cash_flow": _text(item.get("nao_fluxo")) == "S",
        "excluded_from_summary": _text(item.get("nao_resumo")) == "S",
    }


def transform_dimension(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
    valid: list[NormalizedRecord] = []
    rejected: list[RejectedRecord] = []
    seen: set[str] = set()
    for page in pages:
        items = _items(resource, page)
        if items is None:
            rejected.append(RejectedRecord(resource.name, page.payload, "dimension payload invalid"))
            continue
        for item in items:
            key = "codigoDRE" if resource.name == ResourceName.DRE_ACCOUNTS else "nCodCC" if resource.name == ResourceName.BANK_ACCOUNTS else "codigo"
            external_id = _text(item.get(key))
            if not external_id:
                rejected.append(RejectedRecord(resource.name, item, "missing stable key"))
                continue
            if external_id in seen:
                rejected.append(RejectedRecord(resource.name, item, "duplicate stable key"))
                continue
            seen.add(external_id)
            valid.append(NormalizedRecord(resource.name, external_id, _data(resource.name, item), item))
    return valid, rejected
