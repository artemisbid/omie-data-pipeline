from __future__ import annotations

from core.models import RawPage
from extract.resources import CUSTOMERS, SERVICES
from transform.workers import transform_resource


def test_customers_transform_valid_and_rejected_records() -> None:
    pages = [
        RawPage(
            page_number=1,
            payload={
                "clientes_cadastro": [
                    {"codigo_cliente_omie": 1, "razao_social": "A"},
                    {"codigo_cliente_omie": 1, "razao_social": "Duplicado"},
                    {"razao_social": "Sem chave"},
                ]
            },
        )
    ]
    valid, rejected = transform_resource(CUSTOMERS, pages)
    assert [record.external_id for record in valid] == ["1"]
    assert {item.reason for item in rejected} == {"duplicate stable key", "missing stable key"}


def test_services_transform_uses_declared_payload_key() -> None:
    valid, rejected = transform_resource(
        SERVICES,
        [RawPage(page_number=1, payload={"cadastros": [{"codigo_servico": 10, "descricao": "S"}]})],
    )
    assert len(valid) == 1
    assert valid[0].external_id == "10"
    assert not rejected


def test_invalid_collection_is_rejected() -> None:
    valid, rejected = transform_resource(CUSTOMERS, [RawPage(page_number=1, payload={"clientes_cadastro": {}})])
    assert valid == []
    assert rejected[0].reason == "clientes_cadastro payload invalid"

