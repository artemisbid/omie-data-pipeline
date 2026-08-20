# Contrato de dados financeiros — lote inicial

Este documento inicia o contrato entre a API Omie, o ETL Python e o Supabase.
O primeiro lote aprovado contém **Contas a Receber** e **Categorias**.

Campos e chaves marcados como `a confirmar` não devem ser fixados em código ou
migration antes de uma resposta real da API Omie.

## Recursos aprovados

| Recurso interno | Endpoint | Operação | Estado |
|---|---|---|---|
| `receivables` | `/api/v1/financas/contareceber/` | `ListarContasReceber` | contrato inicial |
| `categories` | `/api/v1/geral/categorias/` | `ListarCategorias` | contrato inicial |

Ambos usam paginação no padrão `pagina` e `registros_por_pagina`, conforme o
extrator legado. A extração local confirmou que o script legado consolidou os
itens em listas com 2.933 recebíveis e 227 categorias.

## Contas a Receber

### Objetivo analítico

Servir de base para receita bruta, receita líquida, contas previstas, contas
recebidas e os fatos financeiros derivados.

### Campos candidatos do modelo legado

| Campo normalizado | Campo de origem esperado | Regra | Estado |
|---|---|---|---|
| `external_id` | `codigo_lancamento_omie` | chave técnica de upsert | confirmado |
| `installment_number` | `numero_parcela` | inteiro ou texto preservado | candidato |
| `customer_id` | `codigo_cliente_fornecedor` | referência à dimensão de clientes | confirmado |
| `service_order_id` | `codigo_os` | referência opcional | candidato |
| `contract_number` | `numero_contrato` | referência opcional | candidato |
| `category_code` | `codigo_categoria` | texto normalizado | confirmado |
| `dre_account` | conta DRE | texto normalizado | candidato |
| `department_code` | departamento | texto normalizado | candidato |
| `issued_at` | `data_emissao` | data ISO | confirmado |
| `due_at` | `data_vencimento` | data ISO | confirmado |
| `reference_at` | `data_previsao` | data ISO | confirmado |
| `received_at` | `data_recebimento` | data ISO ou nulo | candidato |
| `original_amount` | `valor_documento` | número decimal | confirmado |
| `allocation_rate` | `percentual_rateio` | percentual normalizado | candidato |
| `allocated_amount` | `valor_rateado` | valor original × rateio | derivado |
| `net_received_amount` | `valor_liquido_recebido` | valor efetivamente recebido | candidato |
| `status` | `status_titulo` | vocabulário a confirmar | campo confirmado |
| `reconciled` | movimento conciliado | booleano | candidato |
| `source_payload` | payload completo | preservado sem credenciais | obrigatório |

Impostos e retenções serão adicionados somente após confirmar os nomes e a
semântica no payload real. Não devemos inferir `pago`, `recebido`, `cancelado`
ou `previsto` apenas pelo nome de uma coluna.

## Categorias

### Objetivo analítico

Fornecer a classificação usada para DRE, fluxo de caixa, custos e despesas.

### Campos candidatos

| Campo normalizado | Campo de origem esperado | Estado |
|---|---|---|
| `external_id` | `codigo` | confirmado |
| `name` | `descricao` | confirmado |
| `dre_account` | `codigo_dre` | confirmado |
| `category_type` | `tipo_categoria` | confirmado |
| `active` | `conta_inativa` | confirmado |
| `source_payload` | payload completo | obrigatório |

## Aprovação necessária antes do código

Antes de aplicar a migration em produção, confirmar na resposta original da API
(antes da consolidação do script legado):

1. chave da coleção (`conta_receber_cadastro`, `categoria_cadastro` ou outra);
2. vocabulário de status (`status_titulo`);
3. estrutura de `categorias` e `distribuicao` dos recebíveis;
4. possibilidade de paginação incremental.

Até essa confirmação, este documento é um contrato de trabalho e não uma
especificação final de schema.

## Próximos artefatos

- fixture fictícia de Contas a Receber;
- fixture fictícia de Categorias;
- `ResourceSpec` dos dois recursos;
- transformadores e testes unitários;
- migration somente após validar os payloads.
