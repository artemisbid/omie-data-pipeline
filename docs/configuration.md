# Configuração

Este documento lista apenas nomes e finalidade das variáveis de ambiente planejadas para o projeto.

## Princípios

- Não registrar valores reais em documentação, código, exemplos ou commits.
- O arquivo `.env` nunca deve ser versionado.
- Defaults planejados devem ser documentados separadamente da lista de variáveis obrigatórias.
- Comandos de CLI permanecem como planejados até a implementação real.

## Variáveis planejadas

### Obrigatórias

- `OMIE_APP_KEY`: chave de aplicação usada para autenticar chamadas à API da Omie.
- `OMIE_APP_SECRET`: segredo da aplicação usado junto da chave da Omie.
- `OMIE_ACCOUNT_KEY`: identificador lógico da conta Omie no pipeline.
- `SUPABASE_URL`: URL do projeto Supabase de destino.
- `SUPABASE_SERVICE_ROLE_KEY`: chave de backend para carga no Supabase.

### Opcionais

- `RAW_DATA_DIR`: diretório base para persistência de payloads brutos e artefatos locais.
- `LOG_LEVEL`: nível de detalhamento dos logs.
- `HTTP_TIMEOUT`: tempo limite das requisições HTTP.
- `HTTP_MAX_RETRIES`: número máximo de retries para falhas transitórias.
- `LOAD_BATCH_SIZE`: tamanho do lote de escrita no destino.

## Defaults planejados

Os valores default ainda não estão fixados no código, mas a documentação de implementação deverá registrar defaults explícitos para:

- `RAW_DATA_DIR`
- `LOG_LEVEL`
- `HTTP_TIMEOUT`
- `HTTP_MAX_RETRIES`
- `LOAD_BATCH_SIZE`

## Comandos planejados

Exemplos conceituais de comandos futuros:

```text
omie-pipeline run --resource customers --mode full
omie-pipeline extract --resource products
omie-pipeline replay --run-id <uuid>
```

Esses comandos ainda não existem no repositório e estão documentados apenas como referência de intenção arquitetural.
