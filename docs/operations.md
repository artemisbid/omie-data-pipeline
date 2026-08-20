# Operação

Este documento descreve o comportamento operacional do pipeline. Os fluxos
`run`, `extract` e `replay` já foram validados localmente em execução controlada.

## Fluxos planejados

Fluxos de CLI disponíveis:

- `run`: executa extract, transform e load.
- `extract`: executa apenas a extração e grava payload bruto.
- `replay`: reprocessa dados brutos já persistidos, sem chamar a Omie.

## Escopo de execução

O operador deverá poder executar:

- apenas Clientes
- apenas Serviços
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

Política inicial:

- logs estruturados por execução;
- correlação por `run_id`;
- retenção local de payload bruto;
- retenção exata ainda depende de decisão do responsável pelo projeto.

## Validação atual

- Clientes e Serviços foram executados em modo `full` com limite controlado de
  uma página.
- Os registros foram carregados no Supabase e os checkpoints foram atualizados
  após sucesso.
- A reexecução de Clientes manteve a mesma quantidade de registros, validando
  o upsert idempotente.
- O replay foi executado com sucesso a partir dos JSONs locais.
- A carga completa de Clientes e Serviços foi executada sem limite de páginas.
- A tabela `omie_services` foi conferida com 136 registros após a carga completa.

## Limitações conhecidas

- A estratégia incremental ainda não está habilitada para produção; o
  checkpoint temporal precisa de contrato validado com a Omie.
- A operação incremental ainda depende de um contrato temporal validado com a
  Omie; a carga atual permanece no modo `full`.
- Periodicidade e retenção dos arquivos brutos ainda não foram definidas.
