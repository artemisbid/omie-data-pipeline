# Segurança

## Princípios

- Credenciais nunca entram no Git.
- Credenciais nunca entram em logs.
- Credenciais nunca entram em payloads brutos versionados localmente.
- Exemplos e testes usam dados fictícios.

## Credenciais

As credenciais da Omie e do Supabase devem existir apenas em variáveis de ambiente ou mecanismos seguros equivalentes.

Regra crítica:

- `SUPABASE_SERVICE_ROLE_KEY` é exclusiva de backend e não deve ser exposta a clientes, frontends ou ambientes públicos.

## Dados pessoais

Os payloads brutos podem conter dados pessoais e precisam ser tratados como material sensível. Isso afeta:

- retenção local;
- compartilhamento para depuração;
- criação de fixtures de teste.

## Supabase

Diretrizes aplicadas no MVP:

- as tabelas possuem RLS habilitado;
- nenhum acesso foi concedido para `anon`;
- nenhum acesso foi concedido para `authenticated`;
- cargas do pipeline usarão credencial de backend;
- tabelas foram criadas por migration, não durante uma execução normal.

## Logs e observabilidade

Logs devem privilegiar contexto técnico sem reproduzir segredos ou payloads sensíveis completos.

Boas práticas planejadas:

- correlacionar por `run_id`;
- mascarar dados críticos;
- registrar só o necessário para diagnóstico.
