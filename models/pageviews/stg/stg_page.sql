{# ページの一覧に、ファイル名からダンプの日付を付ける #}

select
    page_id,
    namespace,
    title,
    strptime(regexp_extract(filename, '(\d{8})-', 1), '%Y%m%d')::date as dump_date,
    source_sha256
from {{ ref('raw_page') }}
