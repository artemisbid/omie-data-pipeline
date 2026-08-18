# ADR 0003: Upsert idempotente com checkpoint após sucesso

## Contexto

O pipeline precisa suportar reprocessamentos e falhas transitórias sem duplicar dados nem avançar a marca incremental de forma incorreta.

## Decisão

Usar upsert idempotente com chaves estáveis por recurso e atualizar checkpoint somente após conclusão bem-sucedida da carga.

## Consequências

- Reprocessamentos se tornam seguros.
- Falhas no destino não comprometem a consistência do incremental.
- Exige definição cuidadosa das chaves estáveis dos recursos.

## Alternativas rejeitadas

- Inserção cega sem upsert.
- Avanço de checkpoint antes da persistência final.
- Estratégia baseada em deleção e recarga completa em toda execução.
