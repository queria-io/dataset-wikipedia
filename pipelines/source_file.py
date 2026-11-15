"""取得した元のファイルの記録（source_file の行）。

元のファイルはいったん data/wikipedia/download/ に取得して sha256 を計算し、読み終えたら消す。
ファイル本体は URL から取得し直せるので保存しない。

出力: data/wikipedia/source_file/<名前>.json（1 行 = 1 ファイル）
"""

import json
from pathlib import Path

from shared.fetch import fetch_file, write_atomic

USER_AGENT = "dataset-wikipedia (+https://github.com/queria-io/dataset-wikipedia)"
DOWNLOAD = Path("data/wikipedia/download")
RECORDS = Path("data/wikipedia/source_file")


def fetch(url: str, page_url: str) -> tuple[Path, dict]:
    """url を DOWNLOAD に取得し、その場所と source_file の行を返す。"""
    path = DOWNLOAD / url.rsplit("/", 1)[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    row = fetch_file(url, path, user_agent=USER_AGENT, timeout=300)
    return path, {**row, "page_url": page_url}


def record(name: str, row: dict) -> None:
    RECORDS.mkdir(parents=True, exist_ok=True)
    write_atomic(RECORDS / f"{name}.json", json.dumps(row, ensure_ascii=False) + "\n")


def forget(prefix: str, keep: set[str]) -> None:
    """名前が prefix で始まる記録のうち、keep に無いものを消す（前回の取得分）。"""
    for path in RECORDS.glob(f"{prefix}*.json"):
        if path.stem not in keep:
            path.unlink()
