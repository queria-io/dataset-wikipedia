"""Wikimedia の Pageview complete dumps から日本語版 Wikipedia の行を取り出す。

1 日 1 ファイル（全言語・全プロジェクト、wiki の名前の順）を bz2 のまま流して読み、
ja.wikipedia の行だけを書く。ja.wikipedia の行が終わったら残りは読まない。
user（人のアクセス）と automated（bot と判定されたアクセス）の 2 本がある。

1 行は「wiki 記事名 page_id アクセス方法 1 日の合計 1 時間ごとの数」。
1 時間ごとの数は A1C3 のように時（A=0 時 … X=23 時、UTC）と数を並べたもの。

出力: data/wikipedia/pageviews/<YYYYMMDD>-<user|automated>.txt.gz

データソース: Wikimedia Foundation, Pageview complete dumps (CC0)
https://dumps.wikimedia.org/other/pageview_complete/readme.html
"""

import bz2
import gzip
import logging
import os
from collections.abc import Iterable, Iterator
from datetime import date, timedelta
from itertools import dropwhile, takewhile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request

from shared.fetch import content_length, replacing, request

logger = logging.getLogger("pipelines")

BASE_URL = "https://dumps.wikimedia.org/other/pageview_complete"
USER_AGENT = "dataset-wikipedia (+https://github.com/queria-io/dataset-wikipedia)"
OUT = Path("data/wikipedia/pageviews")
AGENTS = ("user", "automated")
WIKI = b"ja.wikipedia "
# 初めて作るときの最初の日。過去に延ばすときは PAGEVIEWS_FROM で渡す
DEFAULT_FROM = date(2026, 10, 1)
# 1 回のビルドで取る日数の上限。1 日分の取得は 3〜4 分かかる
DEFAULT_MAX_DAYS = 7


def dump_url(day: date, agent: str) -> str:
    return f"{BASE_URL}/{day:%Y}/{day:%Y-%m}/pageviews-{day:%Y%m%d}-{agent}.bz2"


def out_path(day: date, agent: str) -> Path:
    return OUT / f"{day:%Y%m%d}-{agent}.txt.gz"


def ja_lines(lines: Iterable[bytes]) -> Iterator[bytes]:
    """wiki の名前の順に並んだ行から ja.wikipedia の行だけを返す。"""
    return takewhile(lambda line: line.startswith(WIKI), dropwhile(lambda line: line < WIKI, lines))


def extract(response, out: Path) -> int:
    """bz2 の応答を流して読み、ja.wikipedia の行を gzip で out に書く。行数を返す。"""
    with bz2.open(response) as lines, gzip.open(out, "wb", compresslevel=1) as dest:
        return sum(1 for _ in map(dest.write, ja_lines(lines)))


def download_day(day: date, agent: str) -> None:
    out = out_path(day, agent)
    if out.exists():
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    req = Request(dump_url(day, agent), headers={"User-Agent": USER_AGENT})
    with replacing(out) as tmp:
        rows = request(req, lambda response: extract(response, tmp), timeout=300)
        if rows == 0:
            raise RuntimeError(f"{req.full_url} に ja.wikipedia の行が無い")
    logger.info("%s %s: %d 行", day, agent, rows)


def published(day: date) -> bool:
    """その日の 2 本がどちらも公開されているか。翌日の 03:00 UTC ごろに出る。"""
    try:
        return all(content_length(dump_url(day, agent), user_agent=USER_AGENT) > 0 for agent in AGENTS)
    except HTTPError as error:
        if error.code == 404:
            return False
        raise


def days_after(last: date | None) -> Iterator[date]:
    start = last + timedelta(days=1) if last else date.fromisoformat(os.environ.get("PAGEVIEWS_FROM", DEFAULT_FROM.isoformat()))
    return (start + timedelta(days=n) for n in range((date.today() - start).days))


def pending_days(last: date | None) -> list[date]:
    """取る日。PAGEVIEWS_DATES（YYYY-MM-DD のカンマ区切り）があればその日だけにする。"""
    wanted = os.environ.get("PAGEVIEWS_DATES")
    if wanted:
        return [date.fromisoformat(d) for d in wanted.split(",")]
    limit = int(os.environ.get("PAGEVIEWS_MAX_DAYS", DEFAULT_MAX_DAYS))
    return list(takewhile(published, days_after(last)))[:limit]


def download_pageviews(last: date | None) -> list[date]:
    """last の翌日から公開済みの日までを取る。取った日を返す。

    手元に残っている前回の取得分は消す（dbt は data/ にあるファイルをすべて読む）。
    """
    days = pending_days(last)
    keep = {out_path(day, agent) for day in days for agent in AGENTS}
    for path in set(OUT.glob("*.txt.gz")) - keep:
        path.unlink()
    for day in days:
        for agent in AGENTS:
            download_day(day, agent)
    return days

