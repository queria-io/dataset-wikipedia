{# ページビューの行に、ファイル名から日付と利用者の種類（user・automated）を付ける。
   記事名はリクエストされたもの（転送ページの名前を含む）、page_id は転送先を解決したページ。
   ページを解決できなかった行は page_id が null。 #}

select
    strptime(regexp_extract(filename, '(\d{8})-', 1), '%Y%m%d')::date as date,
    regexp_extract(filename, '-(user|automated)-', 1) as agent_type,
    title,
    try_cast(page_id as bigint) as page_id,
    access_method,
    daily_total,
    hourly,
    source_sha256
from {{ ref('raw_pageviews') }}
