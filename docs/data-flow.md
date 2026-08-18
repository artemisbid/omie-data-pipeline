# Fluxo de dados

## Ciclo de uma execução

Uma execução planejada do pipeline seguirá esta sequência:

1. Início da execução com geração de `run_id`.
2. Seleção do recurso e do modo de carga.
3. Extração paginada na Omie.
4. Persistência de cada página bruta em armazenamento local.
5. Geração de manifesto da execução.
6. Transformação dos registros extraídos.
7. Separação entre registros válidos e rejeitados.
8. Upsert idempotente no Supabase.
9. Atualização do checkpoint somente após sucesso.
10. Finalização com status da execução.

## Paginação e persistência bruta

Cada página retornada pela Omie deverá ser armazenada individualmente. A estrutura planejada é semelhante a:

```text
data/raw/<account>/<resource>/<run_id>/
  manifest.json
  pages/
    page_0001.json
    page_0002.json
```

Benefícios:

- Replay sem chamar novamente a Omie
- Auditoria por execução
- Diagnóstico de falhas por página

## Manifesto da execução

O manifesto planejado deve registrar, no mínimo:

- `run_id`
- recurso executado
- conta Omie
- modo de carga
- horário de início
- horário de término
- quantidade de páginas
- quantidade de registros brutos
- status final

## Transformação e rejeições

Após a extração, os payloads brutos serão transformados para um modelo interno. Registros inválidos não devem interromper necessariamente todo o processo; eles devem ser segregados para análise, mantendo rastreabilidade do motivo da rejeição.

Estados esperados:

- Registros válidos seguem para load.
- Registros rejeitados são registrados para revisão.

## Upsert idempotente

A carga final deve usar uma chave estável por recurso para garantir reprocessamento seguro. Reexecutar o mesmo conjunto não deve gerar duplicidade nem depender de deleções compensatórias.

## Checkpoint

O checkpoint só poderá ser atualizado depois que a carga final do recurso terminar com sucesso. Isso evita avançar a marca incremental quando a persistência final falha.

## Modos de execução

### Carga total

Busca todo o conjunto disponível do recurso e é adequada para bootstrap inicial, conferência ou reconstrução.

### Carga incremental

Busca apenas dados novos ou alterados desde o último ponto válido conhecido, usando filtros temporais e checkpoint.

### Replay

Reprocessa payloads já armazenados localmente, sem nova chamada à Omie.

## Comportamento em falhas

### Falha completa

Se a execução falhar antes da carga final bem-sucedida:

- o `run_id` permanece como histórico da tentativa;
- o checkpoint não avança;
- os artefatos brutos já persistidos podem ser usados para análise.

### Falha parcial

Quando parte dos registros falha em validação ou carga:

- o status pode ser `partial`;
- os registros rejeitados precisam ser identificáveis;
- o comportamento exato de checkpoint deve continuar conservador.

## Regra de não apagar ausentes

No MVP, registros ausentes em uma nova extração não serão removidos automaticamente do destino. A estratégia inicial é apenas de upsert, sem sincronização destrutiva.

## Recursos do MVP

O fluxo inicial será aplicado a:

- Clientes
- Serviços

Produtos continuam previstos, mas como expansão posterior.
