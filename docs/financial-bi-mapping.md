# Mapeamento do BI Financeiro para a Nova Stack

## Objetivo

Catalogar as principais medidas do BI financeiro atual e definir como os resultados podem ser reproduzidos no ETL Python e no Supabase, preservando a linhagem:

```text
Omie API -> ETL Python -> PostgreSQL/Supabase -> fatos analíticos -> views -> Lovable
```

Este documento é uma ponte técnica entre o BI legado e a implementação futura. Ele não contém valores financeiros, clientes ou outros dados sensíveis.

## Status da catalogação

- Medidas DAX: inventariadas a partir da tabela `#Medidas`.
- Modelo semântico: confirmado por imagens, XMLs e modelo conceitual AS-IS.
- ETL legado: analisado em `extract_omie.py`, `transform_entradas.py`, `transform_saidas.py`, `load.py` e `main.py`.
- Periodicidade informada: aproximadamente 7 execuções diárias por cron/workers.
- Nova stack atual: implementa apenas os recursos Omie de clientes e serviços.
- Páginas e visuais: identificados nas telas do mockup; o uso exato de cada medida ainda deve ser validado no relatório.

## Linhagem atual

```text
Endpoints Omie
  -> JSONs brutos
  -> transform_entradas.py / transform_saidas.py
  -> entradas.xlsx / saidas.xlsx
  -> public.omie_entradas / public.omie_saidas
  -> fEntradas / fSaidas no Power BI
  -> UNION, FILTER e SELECTCOLUMNS em DAX
  -> fatos derivados
  -> dimensões de classificação e ordenação
  -> medidas DAX
  -> páginas e visuais
```

O modelo conceitual confirma que `fEntradas` e `fSaidas` são as fontes semânticas originais. As demais fatos são derivadas dessas duas tabelas e as dimensões de apoio organizam os grupos, linhas e ordens de apresentação.

## Medidas prioritárias

### Base da DRE

| Medida | Função atual | Dependências principais | Destino recomendado |
|---|---|---|---|
| `Valor Base DRE` | Soma o valor da movimentação no contexto filtrado | `fMovimentacaoDRE[Valor]` | `analytics.vw_dre_movements` ou view mensal |
| `Valor DRE` | Seleciona o cálculo conforme grupo e linha da DRE | `dDRE`, `fMovimentacaoDRE`, `Valor Base DRE` | Regra SQL da view analítica |
| `DRE Receita Bruta` | Soma categorias de receita bruta | `Categoria`, `GrupoDRE` | `analytics.vw_dre_summary` |
| `DRE Deducoes` | Calcula ISS, PIS, COFINS, ICMS, devoluções e retenções | Campos de imposto e retenção | SQL/Python; preferencialmente SQL após normalização |
| `DRE Receita Liquida` | Receita bruta menos deduções | `DRE Receita Bruta`, `DRE Deducoes` | Coluna calculada na view |
| `DRE Custos` | Soma custos classificados na DRE | `Conta_DRE` | `analytics.vw_dre_summary` |
| `DRE Resultado Bruto` | Receita líquida menos custos | `DRE Receita Liquida`, `DRE Custos` | Coluna calculada na view |
| `DRE Despesas Operacionais` | Soma despesas administrativas, pessoais, marketing e variáveis | `Conta_DRE` | `analytics.vw_dre_summary` |
| `DRE Resultado Financeiro` | Consolida receitas e despesas financeiras | `GrupoDRE` | `analytics.vw_dre_summary` |
| `DRE Resultado Antes IR` | Resultado bruto menos despesas e resultado financeiro | Medidas da DRE | Coluna calculada na view |
| `DRE IR CSLL` | Consolida impostos federais classificados | `GrupoDRE` e valores de imposto | SQL/Python conforme regra validada |
| `DRE Resultado Liquido` | Resultado antes do IR menos IR/CSLL | Medidas da DRE | Coluna calculada na view |

### KPIs executivos

| Medida | Função atual | Destino recomendado |
|---|---|---|
| `Receita Bruta Card` | Receita bruta para cartão executivo | `analytics.vw_kpi_financeiro` |
| `Receita Líquida Card` | Receita após deduções e retenções | `analytics.vw_kpi_financeiro` |
| `Resultado Bruto Card` | Resultado após custos | `analytics.vw_kpi_financeiro` |
| `Resultado Líquido Card` | Resultado final após despesas e impostos | `analytics.vw_kpi_financeiro` |
| `Margem Líquida % Card` | Resultado líquido dividido pela receita líquida | `analytics.vw_kpi_financeiro` |
| `Receita Bruta YoY %` | Variação contra o mesmo período anterior | View mensal com janela temporal |
| `Receita Líquida YoY %` | Variação anual da receita líquida | View mensal com janela temporal |
| `Resultado Bruto YoY %` | Variação anual do resultado bruto | View mensal com janela temporal |
| `Resultado Líquido YoY %` | Variação anual do resultado líquido | View mensal com janela temporal |
| `Margem Líquida Var p.p` | Diferença de margem em pontos percentuais | View mensal com janela temporal |

### Fluxo de caixa

| Medida | Fato atual | Regra principal | Destino recomendado |
|---|---|---|---|
| `Valor Base Fluxo Previsto` | `fFluxoPrevisto` | Separa entradas/saídas, status e impostos | `analytics.vw_cash_flow_projected` |
| `Fluxo Caixa Previsto` | `fFluxoPrevisto` | Agrupa por grupo, DRE e linha | View analítica projetada |
| `Valor Base Fluxo Realizado` | `fFluxoRealizado` | Considera valores efetivamente recebidos/pagos | `analytics.vw_cash_flow_realized` |
| `Fluxo Caixa Realizado` | `fFluxoRealizado` | Agrupa por data realizada e classificação | View analítica realizada |
| `Valor Base Fluxo Investimentos` | `fFluxoInvestimentos` | Aplica tipo e status ao fluxo de investimentos | View de investimentos |
| `Fluxo Caixa Investimentos` | `fFluxoInvestimentos` | Classifica entradas, saídas e caixa líquido | View de investimentos |
| `Valor Base Fluxo Financiamento` | `fFluxoFinanciamento` | Aplica tipo e status ao financiamento | View de financiamentos |
| `Fluxo Caixa Financiamento` | `fFluxoFinanciamento` | Classifica entradas, saídas e caixa líquido | View de financiamentos |
| `Resultado Financeiro` | Fluxos previsto, investimento e financiamento | Consolida linhas do resultado financeiro | `analytics.vw_financial_result` |
| `Resultado Financeiro Realizado` | Fluxos realizados | Consolida o resultado efetivo | `analytics.vw_financial_result_realized` |
| `Caixa Liquido Total Previsto` | Fluxo operacional, investimentos e financiamentos | Soma os três blocos | View consolidada de caixa |
| `Receita Operacional` | Receita do fluxo operacional | Grupo operacional | View de fluxo operacional |

## Regras que precisam sair do DAX

### Regras de fatos derivados

As tabelas `fFluxoPrevisto`, `fFluxoRealizado`, `fFluxoInvestimentos`, `fFluxoFinanciamento` e `fMovimentacaoDRE` usam `UNION` de entradas e saídas.

Regras confirmadas:

- excluir registros cancelados;
- classificar entradas como positivas;
- classificar saídas como negativas;
- usar data de recebimento/pagamento quando realizado;
- usar data prevista quando ainda não realizado;
- manter `Conta_DRE`, `Categoria`, `Status` e `Tipo`;
- aplicar impostos e retenções às entradas;
- preencher campos inexistentes das saídas com `BLANK()`;
- usar `valor_rateado` para análises de competência e rateio;
- usar `valor_liquido_recebido` ou `valor_pago_liquido` para caixa realizado;
- derivar ano e mês das datas no ETL.

### Regras do ETL legado

`transform_entradas.py` e `transform_saidas.py` já fazem parte da regra de negócio, não apenas da integração:

- normalização de datas;
- criação de ano e mês para cada data relevante;
- cálculo de rateio por categoria e departamento;
- cálculo de `valor_rateado`;
- cálculo de valor líquido recebido ou pago;
- identificação de conciliação;
- associação de categoria à conta DRE;
- enriquecimento com cliente, conta corrente, departamento e contrato;
- cálculo de IR, ISS, PIS, COFINS, CSLL e INSS;
- suporte a CBS, IBS estadual e IBS municipal nas entradas;
- tratamento de pagamentos ou recebimentos diretos por movimento bancário.

Essas regras devem ser portadas para transformadores Python testáveis antes de qualquer view analítica.

## Mapeamento para a nova stack

### Camada de extração e bruto

Adicionar recursos ao catálogo do pipeline, preservando o padrão atual de `ResourceSpec`, armazenamento bruto, manifesto, replay e checkpoint.

### Camada normalizada sugerida

| Recurso | Tabela sugerida | Papel |
|---|---|---|
| Contas a receber | `omie_receivables` | Base de entradas previstas e recebidas |
| Contas a pagar | `omie_payables` | Base de saídas previstas e pagas |
| Movimentos financeiros | `omie_financial_movements` | Liquidação, conciliação e caixa realizado |
| Contas correntes | `omie_bank_accounts` | Identificação das contas bancárias |
| Extrato | `omie_bank_statement` | Auditoria e conciliação bancária |
| Categorias | `omie_categories` | Classificação financeira |
| Cadastro DRE | `omie_dre_accounts` | Hierarquia e classificação da DRE |
| Departamentos | `omie_departments` | Rateios e análise por área |
| Projetos | `omie_projects` | Rateios e análise por projeto |
| Contratos | `omie_contracts` | Receita recorrente e status contratual |

Os nomes são propostas de destino e devem ser ajustados ao padrão final do projeto antes da implementação.

### Camada analítica no Supabase

Recomendação inicial:

- tabelas normalizadas para dados de origem;
- fatos analíticos materializados quando o volume justificar;
- views para DRE, KPIs e fluxos;
- funções SQL apenas para regras que precisem de parâmetros ou reutilização transacional;
- regras de rateio, impostos e normalização no Python;
- agregações, comparativos e consolidações no PostgreSQL;
- schema analítico separado, por exemplo `analytics`, com controle de acesso adequado.

Views prioritárias:

- `analytics.vw_dre_monthly`;
- `analytics.vw_financial_kpis`;
- `analytics.vw_cash_flow_projected`;
- `analytics.vw_cash_flow_realized`;
- `analytics.vw_investment_flow`;
- `analytics.vw_financing_flow`;
- `analytics.vw_financial_result`.

As views expostas pelo Data API devem permanecer protegidas por RLS e usar configuração compatível com o modelo de acesso da aplicação. A chave `service_role` nunca deve chegar ao Lovable ou ao navegador.

## Endpoints necessários

### Prioridade alta

| Endpoint | Método | Uso |
|---|---|---|
| `/api/v1/financas/contareceber/` | `ListarContasReceber` | Receita bruta, receita prevista e fluxo previsto |
| `/api/v1/financas/contapagar/` | `ListarContasPagar` | Custos, despesas e fluxo previsto |
| `/api/v1/financas/mf/` | `ListarMovimentos` | Recebimentos, pagamentos e movimentos financeiros |
| `/api/v1/financas/contacorrentelancamentos/` | `ListarLancCC` | Conciliação e fluxo realizado |
| `/api/v1/geral/categorias/` | `ListarCategorias` | Classificação financeira |
| `/api/v1/geral/dre/` | `ListarCadastroDRE` | Estrutura da DRE |
| `/api/v1/geral/departamentos/` | `ListarDepatartamentos` | Rateio e análise por área |
| `/api/v1/geral/contacorrente/` | `ListarContasCorrentes` | Contas bancárias e dependência do extrato |

### Prioridade média

| Endpoint | Método | Uso |
|---|---|---|
| `/api/v1/financas/extrato/` | `ListarExtrato` | Auditoria e conciliação bancária |
| `/api/v1/geral/projetos/` | `ListarProjetos` | Rateios e análises por projeto |
| `/api/v1/servicos/contrato/` | `ListarContratos` | Status contratual e projeções de receita |
| `/api/v1/servicos/os/` | `ListarOS` | Receita operacional e indicadores comerciais |
| `/api/v1/servicos/servico/` | `ListarCadastroServico` | Detalhamento de receitas por serviço |

O projeto atual já possui clientes e serviços, mas ainda não possui os recursos financeiros acima. A inclusão deve seguir o padrão existente, sem conectar o dashboard diretamente à Omie.

## Periodicidade e execução

O processo legado é executado aproximadamente 7 vezes por dia por cron/workers. Na nova stack, a periodicidade deve ser registrada como configuração operacional e cada execução deve gerar:

- `run_id`;
- horário de início e fim;
- recursos executados;
- quantidade de páginas e registros;
- status da execução;
- rejeições;
- checkpoint atualizado somente após carga bem-sucedida.

## Plano de implementação

1. Adicionar os recursos financeiros ao catálogo de extração.
2. Criar transformadores Python para recebíveis, pagáveis e movimentos.
3. Reproduzir rateios, impostos, status e datas do ETL legado.
4. Criar tabelas normalizadas no Supabase.
5. Validar totais de entradas, saídas, valores rateados e valores líquidos.
6. Criar o fato DRE e os fatos de fluxo.
7. Criar views analíticas para DRE, KPIs e caixa.
8. Validar os resultados contra períodos selecionados do PBI, sem transportar dados sensíveis para a documentação.
9. Disponibilizar somente views necessárias para o Lovable.
10. Descontinuar medidas DAX apenas depois da validação funcional.

## Critérios de validação

- Receita bruta deve ser equivalente entre PBI e view analítica.
- Deduções devem respeitar retenções e impostos.
- Receita líquida deve reconciliar com receita bruta menos deduções.
- Resultado bruto deve reconciliar com receita líquida menos custos.
- Resultado líquido deve reconciliar com o resultado antes de IR menos IR/CSLL.
- Fluxo previsto deve separar registros não realizados dos realizados.
- Fluxo realizado deve considerar somente recebimentos e pagamentos efetivos.
- Saídas devem manter sinal negativo nas visões de fluxo.
- Rateios devem preservar o valor original após a soma das partes.
- A mesma execução deve ser reprocessável sem duplicidade.

## Pendências

- Confirmar o nome final das tabelas e views no Supabase.
- Confirmar quais medidas auxiliares e de teste ainda são usadas.
- Mapear cada medida aos visuais do PBI.
- Definir a estratégia de atualização incremental por endpoint.
- Validar a semântica de status cancelado, pago, recebido e previsto.
- Confirmar se investimentos e financiamentos serão classificados por categoria, conta DRE ou tabela de regras própria.
- Definir o contrato de consumo do Lovable.
