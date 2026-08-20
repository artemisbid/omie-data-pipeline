alter table public.pipeline_runs drop constraint if exists pipeline_runs_resource_check;
alter table public.pipeline_runs add constraint pipeline_runs_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables', 'dre_accounts', 'departments', 'projects', 'bank_accounts'));
alter table public.pipeline_rejections drop constraint if exists pipeline_rejections_resource_check;
alter table public.pipeline_rejections add constraint pipeline_rejections_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables', 'dre_accounts', 'departments', 'projects', 'bank_accounts'));
alter table public.pipeline_checkpoints drop constraint if exists pipeline_checkpoints_resource_check;
alter table public.pipeline_checkpoints add constraint pipeline_checkpoints_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories', 'payables', 'dre_accounts', 'departments', 'projects', 'bank_accounts'));

create table if not exists public.omie_dre_accounts (
    external_id text primary key, dre_code text not null, description text, hidden boolean not null default false,
    level integer, sign text, totalizer boolean not null default false, source_payload jsonb not null, loaded_at timestamptz not null default now()
);
create table if not exists public.omie_departments (
    external_id text primary key, department_code text not null, name text, structure text, inactive boolean not null default false,
    source_payload jsonb not null, loaded_at timestamptz not null default now()
);
create table if not exists public.omie_projects (
    external_id text primary key, project_id bigint, integration_code text, name text, inactive boolean not null default false,
    source_payload jsonb not null, loaded_at timestamptz not null default now()
);
create table if not exists public.omie_bank_accounts (
    external_id text primary key, bank_account_id bigint, integration_code text, name text, bank_code text, branch_code text,
    account_number text, account_type text, inactive boolean not null default false, blocked boolean not null default false,
    excluded_from_cash_flow boolean not null default false, excluded_from_summary boolean not null default false,
    source_payload jsonb not null, loaded_at timestamptz not null default now()
);

alter table public.omie_dre_accounts enable row level security;
alter table public.omie_departments enable row level security;
alter table public.omie_projects enable row level security;
alter table public.omie_bank_accounts enable row level security;
revoke all on table public.omie_dre_accounts, public.omie_departments, public.omie_projects, public.omie_bank_accounts from anon, authenticated;
