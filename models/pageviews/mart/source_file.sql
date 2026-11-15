{# 取得した元のファイルの一覧。1 行が 1 ファイル。今回取得したファイルのうち、まだ無いものを追記する #}
{{ config(materialized='incremental', incremental_strategy='append') }}

select
    url,
    page_url,
    sha256,
    bytes,
    media_type,
    retrieved_at,
    etag,
    last_modified
from {{ ref('stg_source_file') }}
{% if is_incremental() %}
where sha256 not in (select sha256 from {{ this }})
{% endif %}
order by retrieved_at, url
