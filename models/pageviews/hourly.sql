{# 1 時間ごと・ページごと・アクセス方法ごと・利用者の種類ごとの閲覧数。元データの最小の粒度。
   リクエストされた記事名（転送ページ）の違いは page_id にまとめる。page_id の無い行は入れない。
   新しい日だけを追記する。日の中は page_id の順に並べ、ページで検索するときに読む行グループを絞る。 #}
{{ config(materialized='incremental', incremental_strategy='append') }}

with cells as (
    select
        date,
        page_id,
        access_method,
        agent_type,
        unnest(regexp_extract_all(hourly, '[A-X][0-9]+')) as cell
    from {{ ref('stg_pageviews') }}
    where page_id is not null
    {% if is_incremental() %}
        and date > (select max(timezone('UTC', hour))::date from {{ this }})
    {% endif %}
),

counts as (
    select
        date,
        timezone('UTC', date + to_hours(ascii(cell[1]) - ascii('A'))) as hour,
        page_id,
        access_method,
        agent_type,
        cell[2:]::integer as views
    from cells
)

select hour, page_id, access_method, agent_type, sum(views)::integer as views
from counts
group by date, hour, page_id, access_method, agent_type
order by date, page_id, access_method, agent_type, hour
