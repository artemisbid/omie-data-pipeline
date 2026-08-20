# Roadmap

Estados usados:

- `planned`
- `in progress`
- `done`

## Marcos

1. Documentação — `done`
2. Fundação Python — `done`
3. Extract de Clientes — `done`
4. Extract de Serviços — `done`
5. Transformações — `done`
6. Load no Supabase — `done`
7. Orquestração e replay — `done`
8. Testes end-to-end — `done`
9. Automação futura — `planned`
10. Fundação financeira — `in progress`

## Observações

- O roadmap reflete a intenção atual do MVP.
- Clientes e Serviços já foram extraídos em execução controlada, transformados,
  carregados no Supabase e reprocessados por replay.
- A validação end-to-end foi concluída com múltiplas páginas, falhas simuladas,
  replay, idempotência e carga completa dos recursos.
- Mudanças de escopo devem atualizar este documento e, se necessário, os ADRs.
- O primeiro lote financeiro aprovado é `Contas a Receber` e `Categorias`.
- A migration financeira aguarda a confirmação dos payloads reais da Omie.
