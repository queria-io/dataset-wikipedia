{# 取得した元のファイル。1 行が 1 ファイル。取得日時を日時にする #}

select
    url,
    page_url,
    sha256,
    bytes,
    media_type,
    cast(retrieved_at as timestamptz) as retrieved_at,
    etag,
    last_modified
from {{ ref('raw_source_file') }}
