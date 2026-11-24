# ビルドと更新

データセットの概要は [README.md](README.md) にあります。ここにはこのリポジトリでデータセットをビルド・更新する手順を書きます。

## ビルド

```bash
git clone https://github.com/queria-io/dataset-shared.git shared  # 更新は git -C shared pull
uv sync
scripts/build.sh   # fdl checkout → python main.py → fdl commit
```

`main.py` は公開中のバージョンの最後の日の翌日から、Pageview complete dumps が公開済みの日までを取ります（1 回に最大 7 日分、`PAGEVIEWS_MAX_DAYS`）。1 日分のファイルは全言語で 1.5〜2GB あり、wiki の名前の順に並んでいるので、`ja.wikipedia` の行を読み終えたところで取得をやめます。`hourly`・`daily`・`daily_top` は新しい日だけを追加します。`page` は新しいデータベースダンプが出たときだけ作り直します。

- 最初の日は `PAGEVIEWS_FROM`（既定は 2026-10-01）です
- `PAGEVIEWS_DATES`（`2026-11-01,2026-11-02` のようなカンマ区切り）を渡すと、その日だけを取ります。PR のビルド確認（`.github/workflows/build.yml`）は 1 日分だけを取ります

Sync は毎日 15:00（日本時間）と、main への push・手動の実行（workflow_dispatch）で実行されます。
