-- Allow checkpoints for the first financial resources.
alter table public.pipeline_checkpoints drop constraint if exists pipeline_checkpoints_resource_check;
alter table public.pipeline_checkpoints add constraint pipeline_checkpoints_resource_check
    check (resource in ('customers', 'services', 'receivables', 'categories'));
