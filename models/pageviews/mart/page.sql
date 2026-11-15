{# ページの一覧。日本語版 Wikipedia のデータベースダンプの page テーブルの、転送でないページ。
   新しいダンプが出たときだけ作り直す（main.py）。記事名で検索するので名前空間・記事名の順に並べる。 #}

select
    page_id,
    namespace,
    title,
    dump_date
from {{ ref('stg_page') }}
order by namespace, title
