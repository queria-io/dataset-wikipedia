{# ページの一覧。日本語版 Wikipedia のデータベースダンプの page テーブルの、転送でないページ。
   pipelines/page.py が data/wikipedia/page/<ダンプの日付>-<sha256>.tsv.gz に書いたものをそのまま読む。
   ファイル名から元のファイルの sha256（source_sha256）を付ける。 #}

select
    *,
    regexp_extract(filename, '-([0-9a-f]{64})\.tsv\.gz$', 1) as source_sha256
from read_csv(
    'data/wikipedia/page/*.tsv.gz',
    delim = '\t',
    header = false,
    quote = '',
    escape = '',
    filename = true,
    columns = {'page_id': 'BIGINT', 'namespace': 'INTEGER', 'title': 'VARCHAR'}
)
