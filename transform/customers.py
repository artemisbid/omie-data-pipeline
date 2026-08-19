from __future__ import annotations

from collections.abc import Mapping
from html import unescape
from typing import Any

from core.models import NormalizedRecord, RawPage, RejectedRecord, ResourceName, ResourceSpec


def _text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = unescape(str(value)).strip()
    return normalized or None


def _date(value: Any) -> str | None:
    text = _text(value)
    if not text:
        return None
    parts = text.split("/")
    if len(parts) == 3 and len(parts[2]) == 4:
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    return text


def _emails(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [email.strip().lower() for email in value.split(",") if email.strip()]


def _normalize_customer(item: Mapping[str, Any]) -> dict[str, Any]:
    info = item.get("info", {}) if isinstance(item.get("info"), Mapping) else {}
    recommendations = item.get("recomendacoes", {}) if isinstance(item.get("recomendacoes"), Mapping) else {}
    tags = item.get("tags", [])
    tag_names = [str(tag.get("tag")).strip() for tag in tags if isinstance(tag, Mapping) and tag.get("tag")]

    return {
        "customer_id": item.get("codigo_cliente_omie"),
        "integration_code": _text(item.get("codigo_cliente_integracao")),
        "legal_name": _text(item.get("razao_social")),
        "trade_name": _text(item.get("nome_fantasia")),
        "tax_id": _text(item.get("cnpj_cpf")),
        "person_type": "individual" if item.get("pessoa_fisica") == "S" else "company",
        "state_registration": _text(item.get("inscricao_estadual")),
        "municipal_registration": _text(item.get("inscricao_municipal")),
        "cnae": _text(item.get("cnae")),
        "city": _text(item.get("cidade")),
        "state": _text(item.get("estado")),
        "city_ibge": _text(item.get("cidade_ibge")),
        "country_code": _text(item.get("codigo_pais")),
        "postal_code": _text(item.get("cep")),
        "address": _text(item.get("endereco")),
        "address_number": _text(item.get("endereco_numero")),
        "address_complement": _text(item.get("complemento")),
        "neighborhood": _text(item.get("bairro")),
        "emails": _emails(item.get("email")),
        "phone_1": _text(f"{item.get('telefone1_ddd', '')}{item.get('telefone1_numero', '')}"),
        "phone_2": _text(f"{item.get('telefone2_ddd', '')}{item.get('telefone2_numero', '')}"),
        "active": _text(item.get("inativo")) != "S",
        "is_abroad": _text(item.get("exterior")) == "S",
        "is_simple_national": _text(item.get("optante_simples_nacional")) == "S",
        "billing_blocked": _text(item.get("bloquear_faturamento")) == "S",
        "generates_billing": _text(recommendations.get("gerar_boletos")) == "S",
        "tags": tag_names,
        "imported_by_api": _text(info.get("cImpAPI")) == "S",
        "created_at": _date(info.get("dInc")),
        "updated_at": _date(info.get("dAlt")),
    }


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
                value: object = item
                for part in str(candidate).split("."):
                    value = value.get(part, "") if isinstance(value, Mapping) else ""
                external_id = str(value).strip()
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
    normalized: list[NormalizedRecord] = []
    rejected: list[RejectedRecord] = []
    seen_ids: set[str] = set()
    payload_key = str(resource.metadata.get("payload_key", "clientes_cadastro"))

    for page in pages:
        items = page.payload.get(payload_key, [])
        if not isinstance(items, list):
            rejected.append(RejectedRecord(resource.name, page.payload, f"{payload_key} payload invalid"))
            continue

        for item in items:
            if not isinstance(item, Mapping):
                rejected.append(RejectedRecord(resource.name, page.payload, "item payload invalid"))
                continue
            external_id = str(item.get("codigo_cliente_omie", "")).strip()
            if not external_id:
                rejected.append(RejectedRecord(resource.name, item, "missing stable key"))
                continue
            if external_id in seen_ids:
                rejected.append(RejectedRecord(resource.name, item, "duplicate stable key"))
                continue
            seen_ids.add(external_id)
            normalized.append(
                NormalizedRecord(
                    source=resource.name,
                    external_id=external_id,
                    data=_normalize_customer(item),
                    source_payload=item,
                )
            )

    return normalized, rejected
