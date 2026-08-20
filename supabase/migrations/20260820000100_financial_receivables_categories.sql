-- Financial foundation: Receivables and Categories.

alter table public.pipeline_runs drop constraint if exists pipeline_runs_resource_check;
alter table public.pipeline_runs add constraint pipeline_runs_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories'));

alter table public.pipeline_rejections drop constraint if exists pipeline_rejections_resource_check;
alter table public.pipeline_rejections add constraint pipeline_rejections_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories'));

create table if not exists public.omie_receivables (
    external_id text primary key,
    receivable_id bigint,
    integration_code text,
    customer_id bigint,
    service_order_id bigint,
    contract_number text,
    category_code text,
    project_id bigint,
    issued_at date,
    forecast_at date,
    registered_at date,
    due_at date,
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
    withholds_ir text,
    withholds_iss text,
    withholds_pis text,
    withholds_cofins text,
    withholds_csll text,
    withholds_inss text,
    source_payload jsonb not null,
    loaded_at timestamptz not null default now()
);

create index if not exists omie_receivables_customer_idx
    on public.omie_receivables (customer_id);
create index if not exists omie_receivables_due_at_idx
    on public.omie_receivables (due_at);
create index if not exists omie_receivables_status_idx
    on public.omie_receivables (status);

create table if not exists public.omie_categories (
    external_id text primary key,
    category_id text,
    category_code text not null,
    parent_category_code text,
    category_level smallint,
    name text,
    standard_name text,
    parent_category text,
    dre_code text,
    nature text,
    category_type text,
    inactive boolean not null default false,
    source_payload jsonb not null,
    loaded_at timestamptz not null default now()
);

create index if not exists omie_categories_dre_code_idx
    on public.omie_categories (dre_code);

alter table public.omie_receivables enable row level security;
alter table public.omie_categories enable row level security;
revoke all on table public.omie_receivables from anon, authenticated;
revoke all on table public.omie_categories from anon, authenticated;
