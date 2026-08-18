from __future__ import annotations

import json
from pathlib import Path

from core.models import ExecutionMode, ResourceName, RunContext
from extract.omie_client import OmieClient, OmieCredentials
from extract.pagination import build_page_params, has_more_pages
from extract.resources import CUSTOMERS
from extract.worker import ExtractWorker


def fixture_payload(name: str) -> dict:
    path = Path(__file__).parent / "fixtures" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_pagination_builds_expected_params_and_detects_next_page() -> None:
    params = build_page_params(2, 50, {"apenas_importado_api": "N"})
    assert params == {"pagina": 2, "registros_por_pagina": 50, "apenas_importado_api": "N"}
    assert has_more_pages({"total_de_paginas": 3, "clientes_cadastro": []}, 2, "clientes_cadastro")
    assert not has_more_pages({"total_de_paginas": 2, "clientes_cadastro": []}, 2, "clientes_cadastro")


def test_client_paginates_without_network(monkeypatch) -> None:
    responses = [
        {"pagina": 1, "total_de_paginas": 2, "clientes_cadastro": [{"codigo_cliente_omie": 1}]},
        {"pagina": 2, "total_de_paginas": 2, "clientes_cadastro": [{"codigo_cliente_omie": 2}]},
    ]
    class FakeOmieClient(OmieClient):
        def post(self, endpoint: str, payload: dict) -> dict:
            calls.append(payload)
            return responses[len(calls) - 1]

    calls: list[dict] = []
    client = FakeOmieClient(OmieCredentials("fake-key", "fake-secret"))
    pages = client.list_pages(CUSTOMERS, page_size=50)

    assert [page.page_number for page in pages] == [1, 2]
    assert calls[0]["app_key"] == "fake-key"
    assert "app_secret" in calls[0]


def test_extract_worker_applies_resource_defaults() -> None:
    class FakeClient:
        def list_pages(self, resource, *, page_size, extra_params):
            assert extra_params["apenas_importado_api"] == "N"
            assert page_size == 50
            return []

    pages = ExtractWorker(FakeClient()).extract(CUSTOMERS, RunContext(), ExecutionMode.FULL)
    assert pages == []


def test_fixtures_are_fictitious_and_readable() -> None:
    assert fixture_payload("customers_page_1.json")["clientes_cadastro"][0]["codigo_cliente_omie"] == 101
