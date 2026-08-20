-- Expose Omie's hierarchical category code explicitly.
alter table public.omie_categories
    add column if not exists category_code text,
    add column if not exists parent_category_code text,
    add column if not exists category_level smallint;

update public.omie_categories
set
    category_code = external_id,
    parent_category_code = case
        when position('.' in external_id) > 0
        then regexp_replace(external_id, '\\.[^.]+$', '')
        else null
    end,
    category_level = array_length(string_to_array(external_id, '.'), 1)
where category_code is null;

alter table public.omie_categories
    alter column category_code set not null;

create index if not exists omie_categories_parent_code_idx
    on public.omie_categories (parent_category_code);
