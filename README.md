# omie-data-pipeline

Pipeline ETL planejado para extrair dados da Omie, preservar payloads brutos, transformar os dados em estruturas úteis para análise e carregar o resultado no Supabase com upsert idempotente.

Status atual: fundação, extração, transformação, carga controlada no Supabase e replay já validados localmente. A validação end-to-end ampliada e a operação contínua ainda estão em preparação.

Classificação usada nesta documentação:

- Atual: já existe no repositório.
- Planejada: decisão aprovada, ainda não implementada.
- Futura: fora do MVP atual.

Diagrama resumido:

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

Recursos iniciais do MVP:

- Clientes
- Serviços

Escopo atual do MVP:

- Uma conta Omie inicialmente, com desenho extensível para múltiplas contas.
- Execução local por CLI.
- Armazenamento de JSON bruto para replay.
- Carga inicial completa e, depois, carga incremental com checkpoint.
- Supabase como destino final com colunas tipadas e payload bruto complementar.
- Python 3.14 como versão atual de desenvolvimento local.

Fora do MVP inicial:

- Agendamento automático
- Hospedagem gerenciada
- Supabase Cron

Estrutura conceitual planejada:

- `core`: regras centrais, contratos, entidades e casos de uso.
- `extract`: integração com a Omie, paginação, retries e persistência bruta.
- `transform`: normalização e validação dos dados.
- `load`: upsert no Supabase e controle de persistência final.
- `pipeline`: orquestração da execução sem subprocessos.

Documentação:

- [Índice da documentação](docs/index.md)
- [Visão geral](docs/overview.md)
- [Arquitetura](docs/architecture.md)
- [Fluxo de dados](docs/data-flow.md)
- [Configuração](docs/configuration.md)
- [Operação](docs/operations.md)
- [Desenvolvimento](docs/development.md)
- [Segurança](docs/security.md)
- [Roadmap](docs/roadmap.md)

ADRs:

- [ADR 0001 - Clean Architecture](docs/adr/0001-clean-architecture.md)
- [ADR 0002 - Retenção de payload bruto](docs/adr/0002-raw-data-retention.md)
- [ADR 0003 - Upsert idempotente e checkpoint](docs/adr/0003-idempotent-loading.md)

Roadmap em alto nível:

1. Documentação — concluída
2. Fundação Python — concluída
3. Extract de Clientes — concluído
4. Extract de Serviços — concluído
5. Transformações — concluídas
6. Load no Supabase — concluído
7. Orquestração e replay — concluídos
8. Testes end-to-end — em andamento
9. Automação futura

Avisos importantes:

- Credenciais não devem ser versionadas.
- O arquivo `.env` deve permanecer fora do Git.
- A CLI inicial existe, mas os fluxos reais devem ser validados localmente antes do uso em produção.
