# Visão geral

## Propósito

O projeto existe para transformar dados operacionais da Omie em dados reutilizáveis no Supabase, preservando rastreabilidade desde a extração até a carga final.

## Problema que o pipeline resolve

Hoje, os dados estão na Omie e precisam ser consumidos de forma repetível, auditável e escalável por outras camadas analíticas ou operacionais. O pipeline busca evitar integrações frágeis, acopladas e difíceis de expandir quando novos recursos da Omie forem adicionados.

## Objetivo do fluxo

Fluxo planejado:

```text
Omie -> Extract -> Transform -> Load -> Supabase
```

Objetivos principais:

- Extrair dados de APIs da Omie.
- Armazenar o payload bruto de cada execução.
- Transformar os dados em modelos consistentes.
- Carregar o resultado no Supabase com upsert idempotente.

## Recursos iniciais

No MVP, os recursos iniciais serão:

- Clientes
- Serviços

Status:

- Atual: decisão documentada.
- Planejada: implementação dos extratores e transformações.

## Escopo do MVP

- Uma conta Omie inicialmente.
- Estrutura extensível para múltiplas contas no futuro.
- Execução local inicialmente por CLI.
- Carga completa no primeiro ciclo.
- Carga incremental com checkpoint após a fundação inicial.
- Retenção de JSON bruto para replay e auditoria.

## Fora do MVP

Itens explicitamente fora do MVP atual:

- Agendamento automático
- Hospedagem
- Supabase Cron
- Expansão para outras fontes além da Omie
- Produtos

Esses pontos podem entrar em ciclos futuros, mas não devem influenciar decisões que compliquem a entrega inicial.

## Glossário

- Recurso: conjunto de dados extraído de uma API da Omie, como Clientes ou Produtos.
- Payload bruto: resposta original da API armazenada sem normalização de negócio.
- Transformação: etapa que converte o payload bruto em um formato consistente para uso interno.
- Upsert: operação de inserir ou atualizar registros usando uma chave estável.
- Checkpoint: marca persistida que informa até onde uma carga incremental foi processada com sucesso.
- Carga total: execução que busca todo o conjunto disponível do recurso.
- Carga incremental: execução que busca apenas dados novos ou alterados desde um ponto conhecido.
