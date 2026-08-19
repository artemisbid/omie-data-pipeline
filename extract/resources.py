from __future__ import annotations

from core.models import ExecutionMode, ResourceName, ResourceSpec


CUSTOMERS = ResourceSpec(
    name=ResourceName.CUSTOMERS,
    endpoint="https://app.omie.com.br/api/v1/geral/clientes/",
    method="ListarClientes",
    stable_key="codigo_cliente_omie",
    supports_incremental=False,
    default_mode=ExecutionMode.INCREMENTAL,
    page_size=50,
    metadata={
        "payload_key": "clientes_cadastro",
        "target_table": "omie_customers",
        "conflict_column": "external_id",
        "request_defaults": {
            "apenas_importado_api": "N",
        },
    },
)

SERVICES = ResourceSpec(
    name=ResourceName.SERVICES,
    endpoint="https://app.omie.com.br/api/v1/servicos/servico/",
    method="ListarCadastroServico",
    stable_key="cabecalho.nCodServ",
    supports_incremental=False,
    default_mode=ExecutionMode.INCREMENTAL,
    page_size=50,
    metadata={
        "payload_key": "cadastros",
        "page_param": "nPagina",
        "page_size_param": "nRegPorPagina",
        "total_pages_key": "nTotPaginas",
        "target_table": "omie_services",
        "conflict_column": "external_id",
        "stable_key_candidates": ["cabecalho.cCodigo", "intListar.nCodServ", "intListar.cCodIntServ"],
    },
)
