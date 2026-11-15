{# 取得した元のファイルの記録。pipelines/source_file.py が data/wikipedia/source_file/*.json に書いたものをそのまま読む #}

select *
from read_json(
    'data/wikipedia/source_file/*.json',
    format = 'newline_delimited',
    columns = {
        url: 'VARCHAR', page_url: 'VARCHAR', sha256: 'VARCHAR', bytes: 'BIGINT', media_type: 'VARCHAR',
        retrieved_at: 'VARCHAR', etag: 'VARCHAR', last_modified: 'VARCHAR'
    }
)
