"""日本語版 Wikipedia のページビューのデータパイプライン。

1. 公開中のバージョンにある最後の日と、ページの一覧のダンプの日付を読む
2. pageviews: その翌日から公開済みの日まで、Pageview complete dumps の ja.wikipedia の行を取る
3. page: 新しいデータベースダンプがあれば、ページの一覧を取る
4. dbt: 取ったものだけをビルドする（日ごとの表は追記、ページの一覧は作り直し）
"""

import logging
import os
from datetime import date

import duckdb
from dbt.cli.main import dbtRunner

from pipelines.page import download_page
from pipelines.pageviews import download_pageviews

# dbt を読み込むとルートロガーが先に設定されるので、force で上書きする
logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)
logger = logging.getLogger("pipelines")


def published_state() -> tuple[date | None, date | None]:
    """公開中のバージョンの、ページビューの最後の日とページの一覧のダンプの日付。

    FDL_WORKING（fdl checkout が作った作業場のカタログ）が無い PR のビルド確認では、どちらも None。
    """
    working = os.environ.get("FDL_WORKING")
    if not working:
        return None, None
    # data.queria.io を読むときにビルドとして名乗る（profiles.yml と同じ）
    con = duckdb.connect(config={"custom_user_agent": os.environ.get("QUERIA_USER_AGENT", "")})
    con.execute(
        f"ATTACH 'ducklake:{working}' AS wikipedia "
        f"(DATA_PATH '{os.environ['FDL_DATA_PATH']}', OVERRIDE_DATA_PATH true, META_TYPE 'sqlite', READ_ONLY)"
    )
    tables = {name for (name,) in con.execute(
        "SELECT table_name FROM duckdb_tables() WHERE database_name = 'wikipedia' AND schema_name = 'pageviews'"
    ).fetchall()}
    last_day = con.execute("SELECT max(date) FROM wikipedia.pageviews.daily").fetchone()[0] if "daily" in tables else None
    dump = con.execute("SELECT max(dump_date) FROM wikipedia.pageviews.page").fetchone()[0] if "page" in tables else None
    return last_day, dump


def dbt_build(select: list[str]) -> None:
    dbt = dbtRunner()
    for command in (["deps"], ["build", "--select", *select], ["docs", "generate"]):
        result = dbt.invoke(command)
        if not result.success:
            raise SystemExit(f"dbt {' '.join(command)} failed")


def main():
    logger.info("1/4: 公開中のバージョン")
    last_day, dump = published_state()
    logger.info("最後の日 %s、ページの一覧 %s", last_day, dump)

    logger.info("2/4: pageviews (Pageview complete dumps)")
    days = download_pageviews(last_day)

    logger.info("3/4: page (jawiki-*-page.sql.gz)")
    new_dump = download_page(dump)

    # ページの一覧が変わらないときは page を作り直さない（上位の表は公開中の page を読む）
    select = (["path:models/pageviews/page.sql"] if new_dump else []) + (
        ["path:models/pageviews/hourly.sql", "path:models/pageviews/daily.sql", "path:models/pageviews/daily_top.sql"]
        if days
        else []
    )
    if not select:
        logger.info("新しい日もダンプも無いので dbt を回さない")
        return
    logger.info("4/4: dbt build %s", select)
    dbt_build(select)


if __name__ == "__main__":
    main()
