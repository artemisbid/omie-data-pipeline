-- Omie category codes are hierarchical strings such as 0.01.01 and 1.01.
alter table public.omie_categories
    alter column category_id type text
    using category_id::text;

alter table public.pipeline_checkpoints drop constraint if exists pipeline_checkpoints_resource_check;
alter table public.pipeline_checkpoints add constraint pipeline_checkpoints_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories'));
