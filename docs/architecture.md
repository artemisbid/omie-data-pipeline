# Arquitetura

## Visão arquitetural

O projeto seguirá uma arquitetura limpa, com separação entre regras centrais, integrações externas e orquestração do pipeline.

Fluxo conceitual:

```text
Omie API
   ↓
Extract
   ↓
Raw JSON por run_id
   ↓
Transform
   ↓
Modelo normalizado
   ↓
Load
   ↓
Supabase
```

## Camadas planejadas

### `core`

Responsável por:

- Entidades e tipos centrais
- Contratos entre camadas
- Casos de uso do pipeline
- Regras que não dependem de Omie ou Supabase

### `extract`

Responsável por:

- Cliente HTTP da Omie
- Paginação
- Retry e rate limiting
- Catálogo declarativo de recursos
- Persistência do payload bruto por execução

### `transform`

Responsável por:

- Normalização de dados
- Validação
- Conversão de payload bruto em modelo interno
- Separação de registros válidos e rejeitados

### `load`

Responsável por:

- Persistência final no Supabase
- Upsert idempotente
- Escrita em lote
- Controle do resultado da carga

### `pipeline`

Responsável por:

- Orquestrar uma execução ponta a ponta
- Coordenar extract, transform e load
- Atualizar status de execução
- Atualizar checkpoint apenas após sucesso

## Regra de dependência

A direção da dependência deve apontar para dentro:

- Camadas externas dependem de contratos centrais.
- A lógica central não depende de SDKs, detalhes HTTP ou detalhes do Supabase.
- Adaptadores concretos implementam portas definidas no núcleo.

## Portas e adaptadores

Portas planejadas:

- Porta para extração de dados da Omie
- Porta para armazenamento bruto por `run_id`
- Porta para carga final no Supabase
- Porta para checkpoint e metadados de execução

Adaptadores planejados:

- Cliente HTTP da Omie
- Persistência local de JSON bruto
- Loader para Supabase

## Catálogo declarativo de recursos

Novas APIs da Omie devem ser adicionadas por configuração declarativa de recurso, não por alteração do cliente HTTP base.

Cada `ResourceSpec` planejado deverá definir:

- Nome interno do recurso
- Endpoint Omie
- Método da API
- Estratégia de paginação
- Chave estável do recurso
- Estratégia incremental, quando existir
- Transformador associado

## Orquestração sem subprocessos

O pipeline será executado dentro de um único processo orquestrador, sem depender de subprocessos para encadear etapas. Isso reduz acoplamento operacional, simplifica testes e melhora observabilidade.

## Como escalar para novas APIs

Para adicionar uma nova API da Omie, a expectativa arquitetural é:

1. Criar um novo `ResourceSpec`.
2. Implementar a transformação específica do recurso.
3. Declarar a estratégia de carga.
4. Registrar o recurso no catálogo.

O cliente HTTP e o orquestrador não devem precisar de mudanças estruturais para cada novo recurso.
