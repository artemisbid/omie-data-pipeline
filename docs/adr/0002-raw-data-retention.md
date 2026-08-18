# ADR 0002: Payloads brutos versionados por run_id

## Contexto

O pipeline precisará de rastreabilidade, auditoria e capacidade de replay sem depender de nova chamada à Omie.

## Decisão

Persistir payloads brutos por recurso e por `run_id`, incluindo manifesto de execução.

## Consequências

- Permite replay e depuração offline.
- Melhora auditabilidade.
- Exige política de retenção local e cuidado com dados sensíveis.

## Alternativas rejeitadas

- Descartar payload bruto após transformação.
- Consolidar todas as páginas em um único artefato opaco.
- Reexecutar sempre a Omie em vez de reaproveitar extrações anteriores.
