{# ページの一覧。日本語版 Wikipedia のデータベースダンプの page テーブルの、転送でないページ。
   pipelines/page.py が data/wikipedia/page/<ダンプの日付>.tsv.gz に書いたものをそのまま読む。 #}

select *
from read_csv(
    'data/wikipedia/page/*.tsv.gz',
    delim = '\t',
    header = false,
    quote = '',
    escape = '',
    filename = true,
    columns = {'page_id': 'BIGINT', 'namespace': 'INTEGER', 'title': 'VARCHAR'}
)
