{# 1 日ごとの閲覧数（人のアクセス）の上位 1,000 記事。標準名前空間の記事だけで、メインページは除く。
   記事名は page（ページの一覧）のもの。ダンプより後に作られたページは、その日いちばん多くリクエストされた記事名にする。
   新しい日だけを追記する。 #}
{{ config(materialized='incremental', incremental_strategy='append') }}

with views as (
    select
        date,
        page_id,
        arg_max(title, daily_total) as requested_title,
        sum(daily_total)::integer as views
    from {{ ref('stg_pageviews') }}
    where page_id is not null and agent_type = 'user'
    {% if is_incremental() %}
        and date > (select max(date) from {{ this }})
    {% endif %}
    group by date, page_id
),

articles as (
    select
        v.date,
        v.page_id,
        coalesce(p.title, v.requested_title) as title,
        v.views
    from views as v
    left join {{ ref('page') }} as p using (page_id)
    where coalesce(p.namespace, 0) = 0
      -- ダンプに無いページは名前空間が判定できない。名前空間の接頭辞が付いた記事名は除く
      and (p.page_id is not null or not {{ namespaced('v.requested_title') }})
      and coalesce(p.title, v.requested_title) <> 'メインページ'
)

select
    date,
    row_number() over (partition by date order by views desc, page_id) as rank,
    page_id,
    title,
    views
from articles
qualify rank <= 1000
order by date, rank
