# Configuração

Este documento lista apenas nomes e finalidade das variáveis de ambiente planejadas para o projeto.

## Princípios

- Não registrar valores reais em documentação, código, exemplos ou commits.
- O arquivo `.env` nunca deve ser versionado.
- Defaults planejados devem ser documentados separadamente da lista de variáveis obrigatórias.
- Os comandos abaixo existem na CLI inicial; o fluxo completo continua em evolução.

## Variáveis planejadas

### Obrigatórias

- `OMIE_APP_KEY`: chave de aplicação usada para autenticar chamadas à API da Omie.
- `OMIE_APP_SECRET`: segredo da aplicação usado junto da chave da Omie.
- `SUPABASE_URL`: URL do projeto Supabase de destino.
- `SUPABASE_SERVICE_ROLE_KEY`: chave de backend para carga no Supabase.

### Opcionais

- `RAW_DATA_DIR`: diretório base para persistência de payloads brutos e artefatos locais.
- `LOG_LEVEL`: nível de detalhamento dos logs.
- `HTTP_TIMEOUT`: tempo limite das requisições HTTP.
- `HTTP_MAX_RETRIES`: número máximo de retries para falhas transitórias.
- `LOAD_BATCH_SIZE`: tamanho do lote de escrita no destino.
- `OMIE_COMPANY_ID`: identificador lógico opcional para organizar execuções e arquivos brutos quando houver mais de uma conta.

## Defaults planejados

Os valores default ainda não estão fixados no código, mas a documentação de implementação deverá registrar defaults explícitos para:

- `RAW_DATA_DIR`
- `LOG_LEVEL`
- `HTTP_TIMEOUT`
- `HTTP_MAX_RETRIES`
- `LOAD_BATCH_SIZE`

## Comandos da CLI inicial

Exemplos conceituais de comandos futuros:

```text
python main.py run --resource customers --mode full
python main.py extract --resource services
python main.py replay --resource customers --run-id <uuid>
```

`extract` grava somente o bruto local. `run` e `replay` exigem as variáveis do Supabase e usam o adaptador REST configurado.
