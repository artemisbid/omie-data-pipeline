# Desenvolvimento

## Stack planejada

- Python 3.12
- `uv` para gestão de ambiente e dependências
- Tipagem estática progressiva
- Testes automatizados desde a base do projeto

## Convenções de código

- Módulos com responsabilidade única.
- Contratos explícitos entre camadas.
- Tratamento de erro orientado a contexto operacional.
- Tipos e nomes consistentes entre recursos, payloads e modelos normalizados.
- Evitar lógica de negócio espalhada em adaptadores externos.

## Como adicionar um novo recurso Omie

Fluxo de desenvolvimento esperado:

1. Definir o `ResourceSpec` do novo recurso.
2. Mapear a resposta bruta e a paginação da API.
3. Implementar a transformação do payload para o modelo interno.
4. Definir a chave estável usada no upsert.
5. Registrar testes do recurso.
6. Registrar a documentação correspondente.

## Estratégia de testes

Camadas de teste planejadas:

- Unitários: paginação, parsing, validação, transformações e regras centrais.
- Contratos HTTP: comportamento esperado das integrações com a Omie.
- Integração: fluxo entre extract, transform e load.

## Git e versionamento

Convenções planejadas:

- branches por feature
- commits convencionais
- mudanças relevantes agrupadas por milestone

Exemplos de prefixos:

- `docs:`
- `feat:`
- `fix:`
- `refactor:`
- `test:`

## Checklist antes de commit

- documentação coerente com o estado real do projeto;
- nenhum segredo em arquivos versionados;
- nomes consistentes entre código e docs;
- testes relevantes executados quando já existirem;
- mudança pequena o suficiente para revisão clara;
- roadmap e ADR atualizados quando a decisão arquitetural mudar.
