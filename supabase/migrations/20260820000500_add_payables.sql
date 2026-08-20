alter table public.pipeline_runs drop constraint if exists pipeline_runs_resource_check;
alter table public.pipeline_runs add constraint pipeline_runs_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables'));

alter table public.pipeline_rejections drop constraint if exists pipeline_rejections_resource_check;
alter table public.pipeline_rejections add constraint pipeline_rejections_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables'));

alter table public.pipeline_checkpoints drop constraint if exists pipeline_checkpoints_resource_check;
alter table public.pipeline_checkpoints add constraint pipeline_checkpoints_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables'));

create table if not exists public.omie_payables (
    external_id text primary key,
    payable_id bigint,
    integration_code text,
    supplier_id bigint,
    category_code text,
    project_id bigint,
    issued_at date,
    entry_at date,
    due_at date,
    forecast_at date,
    registered_at date,
    installment_number text,
    document_number text,
    document_fiscal_number text,
    status text,
    original_amount numeric(18, 4),
    ir_amount numeric(18, 4),
    iss_amount numeric(18, 4),
    pis_amount numeric(18, 4),
    cofins_amount numeric(18, 4),
    csll_amount numeric(18, 4),
    inss_amount numeric(18, 4),
    withholds_ir text,
    withholds_iss text,
    withholds_pis text,
    withholds_cofins text,
    withholds_csll text,
    withholds_inss text,
    source_payload jsonb not null,
    loaded_at timestamptz not null default now()
);

create index if not exists omie_payables_supplier_idx on public.omie_payables (supplier_id);
create index if not exists omie_payables_due_at_idx on public.omie_payables (due_at);
create index if not exists omie_payables_status_idx on public.omie_payables (status);

alter table public.omie_payables enable row level security;
revoke all on table public.omie_payables from anon, authenticated;
