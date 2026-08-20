from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceSpec


def _text(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


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
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            continue
    return text


def transform_payables(resource: ResourceSpec, pages: list[RawPage]) -> tuple[list[NormalizedRecord], list[RejectedRecord]]:
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
            rejected.append(RejectedRecord(resource.name, page.payload, "payables payload invalid"))
            continue
        for item in items:
            external_id = _text(item.get("codigo_lancamento_omie"))
            if not external_id:
                rejected.append(RejectedRecord(resource.name, item, "missing stable key"))
                continue
            if external_id in seen:
                rejected.append(RejectedRecord(resource.name, item, "duplicate stable key"))
                continue
            seen.add(external_id)
            valid.append(NormalizedRecord(resource.name, external_id, {
                "payable_id": _number(item.get("codigo_lancamento_omie")),
                "integration_code": _text(item.get("codigo_lancamento_integracao")),
                "supplier_id": _number(item.get("codigo_cliente_fornecedor")),
                "category_code": _text(item.get("codigo_categoria")),
                "project_id": _number(item.get("codigo_projeto")),
                "issued_at": _date(item.get("data_emissao")),
                "entry_at": _date(item.get("data_entrada")),
                "due_at": _date(item.get("data_vencimento")),
                "forecast_at": _date(item.get("data_previsao_pagamento")),
                "registered_at": _date(item.get("data_registro")),
                "installment_number": _text(item.get("numero_parcela")),
                "document_number": _text(item.get("numero_documento")),
                "document_fiscal_number": _text(item.get("numero_documento_fiscal")),
                "status": _text(item.get("status_titulo")),
                "original_amount": _number(item.get("valor_documento")),
                "ir_amount": _number(item.get("valor_ir")),
                "iss_amount": _number(item.get("valor_iss")),
                "pis_amount": _number(item.get("valor_pis")),
                "cofins_amount": _number(item.get("valor_cofins")),
                "csll_amount": _number(item.get("valor_csll")),
                "inss_amount": _number(item.get("valor_inss")),
                "withholds_ir": _text(item.get("retem_ir")),
                "withholds_iss": _text(item.get("retem_iss")),
                "withholds_pis": _text(item.get("retem_pis")),
                "withholds_cofins": _text(item.get("retem_cofins")),
                "withholds_csll": _text(item.get("retem_csll")),
                "withholds_inss": _text(item.get("retem_inss")),
            }, item))
    return valid, rejected
