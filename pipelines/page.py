"""日本語版 Wikipedia のデータベースダンプの page テーブルから、ページの一覧を取り出す。

ページビューの行は「リクエストされた記事名」と「転送先を解決したページの page_id」を持つ。
page_id ごとの正式な記事名と名前空間はダンプの page テーブルにしかないので、ここから取る。
ダンプは月 2 回（1 日と 20 日）作られる。前回と同じダンプなら取り直さない。

INSERT 文の値は (page_id, page_namespace, 'page_title', page_is_redirect, ...) で、今のダンプは 1 行に 1 つ。
転送ページ（page_is_redirect = 1）は入れない。

出力: data/wikipedia/page/<YYYYMMDD>.tsv.gz（page_id, namespace, title）

データソース: Wikimedia Foundation, jawiki database dumps
https://dumps.wikimedia.org/jawiki/latest/
"""

import gzip
import logging
import re
from collections.abc import Iterable, Iterator
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request

from shared.fetch import fetch, replacing, request

logger = logging.getLogger("pipelines")

RSS_URL = "https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-page.sql.gz-rss.xml"
USER_AGENT = "dataset-wikipedia (+https://github.com/queria-io/dataset-wikipedia)"
OUT = Path("data/wikipedia/page")
DUMP_DATE = re.compile(rb"/jawiki/(\d{8})")
# (page_id, page_namespace, 'page_title', page_is_redirect, ...
ROW = re.compile(rb"\((\d+),(-?\d+),'((?:[^'\\]|\\.)*)',([01]),")
ESCAPE = re.compile(rb"\\(.)")
UNESCAPED = {b"0": b"\0", b"n": b"\n", b"r": b"\r", b"t": b"\t", b"Z": b"\x1a"}


def latest_dump() -> date:
    rss = fetch(RSS_URL, user_agent=USER_AGENT)
    found = DUMP_DATE.search(rss)
    if not found:
        raise RuntimeError("page.sql.gz の RSS にダンプの日付が無い")
    return datetime.strptime(found.group(1).decode(), "%Y%m%d").date()


def dump_url(day: date) -> str:
    return f"https://dumps.wikimedia.org/jawiki/{day:%Y%m%d}/jawiki-{day:%Y%m%d}-page.sql.gz"


def unescape(title: bytes) -> bytes:
    return ESCAPE.sub(lambda m: UNESCAPED.get(m.group(1), m.group(1)), title)


def pages(lines: Iterable[bytes]) -> Iterator[bytes]:
    """INSERT 文の値から、転送でないページを TSV の行にして返す。1 行に複数の値があっても読む。"""
    return (
        b"\t".join((page_id, namespace, unescape(title))) + b"\n"
        for line in lines
        for page_id, namespace, title, redirect in ROW.findall(line)
        if redirect == b"0"
    )


def extract(response, out: Path) -> int:
    with gzip.open(response) as lines, gzip.open(out, "wb", compresslevel=1) as dest:
        return sum(1 for _ in map(dest.write, pages(lines)))


def download_page(current: date | None) -> date | None:
    """current より新しいダンプがあれば取る。取ったダンプの日付を返す。"""
    day = latest_dump()
    if current and day <= current:
        return None
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.tsv.gz"):
        path.unlink()
    req = Request(dump_url(day), headers={"User-Agent": USER_AGENT})
    with replacing(OUT / f"{day:%Y%m%d}.tsv.gz") as tmp:
        rows = request(req, lambda response: extract(response, tmp), timeout=300)
        if rows < 1_000_000:
            raise RuntimeError(f"{req.full_url} のページが {rows} 件しかない")
    logger.info("page %s: %d 行", day, rows)
    return day
