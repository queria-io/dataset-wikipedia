{# ページの一覧。日本語版 Wikipedia のデータベースダンプの page テーブルの、転送でないページ。
   pipelines/page.py が data/wikipedia/page/<ダンプの日付>.tsv.gz に書く。
   新しいダンプが出たときだけ作り直す（main.py）。記事名で検索するので名前空間・記事名の順に並べる。 #}

select
    page_id,
    namespace,
    title,
    strptime(regexp_extract(filename, '(\d{8})\.tsv', 1), '%Y%m%d')::date as dump_date
from read_csv(
    'data/wikipedia/page/*.tsv.gz',
    delim = '\t',
    header = false,
    quote = '',
    escape = '',
    filename = true,
    columns = {'page_id': 'BIGINT', 'namespace': 'INTEGER', 'title': 'VARCHAR'}
)
order by namespace, title
