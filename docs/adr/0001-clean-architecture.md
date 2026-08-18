# ADR 0001: Clean Architecture preservando ETL

## Contexto

O projeto precisa crescer de 1 ou 2 APIs da Omie para um catálogo maior sem acumular acoplamento entre HTTP, transformação, carga e orquestração.

## Decisão

Adotar uma estrutura baseada em Clean Architecture, preservando a separação explícita entre extract, transform e load.

## Consequências

- Facilita expansão para novos recursos Omie.
- Melhora testabilidade por camada.
- Exige contratos e limites claros entre módulos.

## Alternativas rejeitadas

- Pipeline monolítico concentrado em um único arquivo.
- Orquestração por subprocessos entre etapas.
- Mistura de regras de negócio com detalhes de integração.
