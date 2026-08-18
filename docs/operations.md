# Operação

Este documento descreve o comportamento operacional planejado do pipeline.

## Fluxos planejados

Fluxos de CLI previstos:

- `run`: executa extract, transform e load.
- `extract`: executa apenas a extração e grava payload bruto.
- `replay`: reprocessa dados brutos já persistidos.

Esses fluxos ainda não estão implementados.

## Escopo de execução

O operador deverá poder executar:

- apenas Clientes
- apenas Produtos
- todos os recursos registrados

## Quando usar cada modo

- Carga total: bootstrap inicial, reconstrução ou conferência ampla.
- Carga incremental: rotina normal após existir checkpoint válido.
- Replay: reprocessamento sem nova chamada à Omie.

## Identificação de `run_id`

Cada execução deverá gerar um `run_id` único. Esse identificador será usado para:

- localizar payloads brutos;
- relacionar logs e manifesto;
- reprocessar execuções específicas;
- auditar sucesso, falha ou parcialidade.

## Reprocessamento

O replay deverá ler o armazenamento bruto associado a um `run_id` e reexecutar as etapas posteriores à extração, respeitando as mesmas regras de transformação e carga.

## Tratamento de falhas

### Timeout

- registrar a falha;
- aplicar retries dentro do limite configurado;
- encerrar como `failed` quando a condição persistir.

### HTTP 429

- respeitar backoff;
- tentar novamente;
- evitar avanço de checkpoint em caso de falha final.

### Erro redundante da Omie

- tratar como falha transitória com nova tentativa;
- registrar a ocorrência para análise operacional.

### Validação inválida

- separar o registro rejeitado;
- seguir com registros válidos quando a estratégia permitir;
- refletir parcialidade no status se necessário.

### Falha do Supabase

- interromper a confirmação final da execução;
- não avançar checkpoint;
- manter os artefatos locais para replay.

## Estados planejados de execução

- `running`: execução em andamento.
- `success`: execução concluída sem falhas relevantes.
- `partial`: execução concluída com rejeições ou falhas parciais tratadas.
- `failed`: execução não concluída com segurança.

## Logs e retenção local

Política inicial planejada:

- logs estruturados por execução;
- correlação por `run_id`;
- retenção local de payload bruto;
- retenção exata ainda será definida antes da implementação operacional.
