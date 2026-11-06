{# Pageview complete dumps の ja.wikipedia の行。pipelines/pageviews.py が日ごと・種類ごとに
   data/wikipedia/pageviews/<YYYYMMDD>-<user|automated>.txt.gz に書く。
   1 行は「wiki 記事名 page_id アクセス方法 1 日の合計 1 時間ごとの数」で、空白で区切る（記事名の空白は _）。
   記事名はリクエストされたもの（転送ページの名前を含む）、page_id は転送先を解決したページ。
   ページを解決できなかった行は page_id が null。 #}
{{ config(materialized='ephemeral') }}

select
    strptime(regexp_extract(filename, '(\d{8})-', 1), '%Y%m%d')::date as date,
    regexp_extract(filename, '-(user|automated)\.txt', 1) as agent_type,
    title,
    try_cast(page_id as bigint) as page_id,
    access_method,
    daily_total,
    hourly
from read_csv(
    'data/wikipedia/pageviews/*.txt.gz',
    delim = ' ',
    header = false,
    quote = '',
    escape = '',
    filename = true,
    columns = {
        'wiki': 'VARCHAR',
        'title': 'VARCHAR',
        'page_id': 'VARCHAR',
        'access_method': 'VARCHAR',
        'daily_total': 'INTEGER',
        'hourly': 'VARCHAR'
    }
)
