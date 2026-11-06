{# 1 日ごと・ページごとの閲覧数。hourly を日で合計したものに、アクセス方法ごとの内訳と bot の数を並べる。
   新しい日だけを追記する。日の中は page_id の順。 #}
{{ config(materialized='incremental', incremental_strategy='append') }}

select
    date,
    page_id,
    coalesce(sum(daily_total) filter (agent_type = 'user'), 0)::integer as views,
    coalesce(sum(daily_total) filter (agent_type = 'user' and access_method = 'desktop'), 0)::integer as desktop_views,
    coalesce(sum(daily_total) filter (agent_type = 'user' and access_method = 'mobile-web'), 0)::integer as mobile_web_views,
    coalesce(sum(daily_total) filter (agent_type = 'user' and access_method = 'mobile-app'), 0)::integer as mobile_app_views,
    coalesce(sum(daily_total) filter (agent_type = 'automated'), 0)::integer as automated_views
from {{ ref('stg_pageviews') }}
where page_id is not null
{% if is_incremental() %}
    and date > (select max(date) from {{ this }})
{% endif %}
group by date, page_id
order by date, page_id
