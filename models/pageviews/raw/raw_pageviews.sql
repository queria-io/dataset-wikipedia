{# Pageview complete dumps の ja.wikipedia の行。pipelines/pageviews.py が日ごと・種類ごとに
   data/wikipedia/pageviews/<YYYYMMDD>-<user|automated>-<sha256>.txt.gz に書いたものをそのまま読む。
   ファイル名から元のファイルの sha256（source_sha256）を付ける。
   1 行は「wiki 記事名 page_id アクセス方法 1 日の合計 1 時間ごとの数」で、空白で区切る（記事名の空白は _）。 #}

select
    *,
    regexp_extract(filename, '-([0-9a-f]{64})\.txt\.gz$', 1) as source_sha256
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
