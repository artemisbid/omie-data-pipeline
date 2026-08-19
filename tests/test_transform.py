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
        [RawPage(
            page_number=1,
            payload={
                "cadastros": [
                    {
                        "cabecalho": {"nCodServ": 10},
                        "descricao": {"cDescrCompleta": "S"},
                        "intListar": {"nCodServ": 10},
                    }
                ]
            },
        )],
    )
    assert len(valid) == 1
    assert valid[0].external_id == "10"
    assert valid[0].data["service_id"] == 10
    assert valid[0].data["active"] is True
    assert not rejected


def test_services_transform_flattens_real_api_sections() -> None:
    valid, rejected = transform_resource(
        SERVICES,
        [
            RawPage(
                page_number=1,
                payload={
                    "cadastros": [
                        {
                            "cabecalho": {
                                "cCodigo": "S-1",
                                "cDescricao": "Serviço",
                                "nPrecoUnit": 10.5,
                            },
                            "descricao": {"cDescrCompleta": "Texto &quot;completo&quot;"},
                            "impostos": {"nAliqISS": 2},
                            "info": {"inativo": "N", "dAlt": "05/01/2026"},
                            "intListar": {"nCodServ": 99},
                        }
                    ]
                },
            )
        ],
    )
    assert not rejected
    assert valid[0].data["service_code"] == "S-1"
    assert valid[0].data["description"] == 'Texto "completo"'
    assert valid[0].data["updated_at"] == "2026-01-05"
    assert valid[0].data["iss_rate"] == 2


def test_invalid_collection_is_rejected() -> None:
    valid, rejected = transform_resource(CUSTOMERS, [RawPage(page_number=1, payload={"clientes_cadastro": {}})])
    assert valid == []
    assert rejected[0].reason == "clientes_cadastro payload invalid"


def test_customers_transform_flattens_real_api_fields() -> None:
    valid, rejected = transform_resource(
        CUSTOMERS,
        [
            RawPage(
                page_number=1,
                payload={
                    "clientes_cadastro": [
                        {
                            "codigo_cliente_omie": 123,
                            "codigo_cliente_integracao": "CLI-123",
                            "razao_social": "Empresa Fictícia",
                            "nome_fantasia": "Empresa",
                            "cnpj_cpf": "00.000.000/0001-00",
                            "pessoa_fisica": "N",
                            "cidade": "Recife",
                            "estado": "PE",
                            "email": " Contato@exemplo.com, financeiro@exemplo.com ",
                            "telefone1_ddd": "81",
                            "telefone1_numero": "999999999",
                            "inativo": "N",
                            "optante_simples_nacional": "S",
                            "tags": [{"tag": "Cliente"}],
                            "info": {"dInc": "06/08/2025", "dAlt": "07/08/2025", "cImpAPI": "N"},
                        }
                    ]
                },
            )
        ],
    )
    assert not rejected
    assert valid[0].external_id == "123"
    assert valid[0].data["legal_name"] == "Empresa Fictícia"
    assert valid[0].data["emails"] == ["contato@exemplo.com", "financeiro@exemplo.com"]
    assert valid[0].data["phone_1"] == "81999999999"
    assert valid[0].data["is_simple_national"] is True
    assert valid[0].data["created_at"] == "2025-08-06"
