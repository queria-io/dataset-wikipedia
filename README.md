# Wikipedia 日本語版のページビュー

日本語版 Wikipedia の記事ごとの閲覧数を、SQL で検索・集計できるテーブルにしたデータセットです。Wikimedia が公開する Pageview complete dumps から日本語版の行を取り出し、1 時間ごと・アクセス方法ごとに、人のアクセスと bot と判定されたアクセスを分けて収録しています。毎日、前日分を追加します。

## 出典と利用条件

| 原典 | テーブル |
| --- | --- |
| [Pageview complete dumps](https://dumps.wikimedia.org/other/pageview_complete/readme.html)（`pageviews-<日付>-user.bz2`・`pageviews-<日付>-automated.bz2`） | `pageviews.hourly`・`pageviews.daily`・`pageviews.daily_top` |
| [日本語版 Wikipedia のデータベースダンプ](https://dumps.wikimedia.org/jawiki/latest/)（`jawiki-<日付>-page.sql.gz`） | `pageviews.page`、`pageviews.daily_top` の記事名 |

- Pageview complete dumps は [CC0](https://creativecommons.org/publicdomain/zero/1.0/) で提供されています
- 記事名はデータベースダンプから取っています。Wikipedia の内容は [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja) で提供されています。記事名を含めて使うときは、出典として「Wikipedia 日本語版」と書き、Queria が加工したものであることを明記してください

## テーブル

| テーブル | 内容 |
| --- | --- |
| `pageviews.hourly` | 1 行が 1 時間・1 ページ・1 アクセス方法・人か bot か の組の閲覧数。元データの最も細かい粒度（1 日約 1,100 万行） |
| `pageviews.daily` | 1 行が 1 日・1 ページ。人のアクセスの閲覧数と、アクセス方法ごとの内訳、bot と判定されたアクセスの数（1 日約 140 万行） |
| `pageviews.daily_top` | 1 日ごとの閲覧数（人のアクセス）の上位 1,000 記事。記事名つき |
| `pageviews.page` | 1 行が 1 ページ。ページ ID・名前空間・記事名。記事名から `page_id` を引くのに使う |

収録は 2026 年 10 月 1 日からです。

## 使い方

記事の 1 日ごとの閲覧数の推移:

```sql
SELECT d.date, d.views, d.automated_views
FROM wikipedia.pageviews.daily AS d
JOIN wikipedia.pageviews.page AS p USING (page_id)
WHERE p.namespace = 0 AND p.title = '富士山'
ORDER BY d.date;
```

1 日のうち何時に読まれているか（日本時間）:

```sql
SELECT hour(h.hour AT TIME ZONE 'Asia/Tokyo') AS hour_jst, h.access_method, sum(h.views) AS views
FROM wikipedia.pageviews.hourly AS h
WHERE h.page_id = (SELECT page_id FROM wikipedia.pageviews.page WHERE namespace = 0 AND title = '富士山')
  AND h.agent_type = 'user'
GROUP BY ALL
ORDER BY hour_jst, h.access_method;
```

その日よく読まれた記事:

```sql
SELECT rank, title, views
FROM wikipedia.pageviews.daily_top
WHERE date = DATE '2026-11-05'
ORDER BY rank
LIMIT 20;
```

`hourly` と `daily` は大きいので、`page_id` と日付で絞ってから集計してください。

## 閲覧数の数え方

- 閲覧数は Wikimedia の[ページビューの定義](https://meta.wikimedia.org/wiki/Research:Page_view)に従います。同じ人が何度読んでも、読んだ回数だけ数えます
- `agent_type` の `user` は人のアクセス、`automated` は Wikimedia が bot と判定したアクセスです。自分から bot と名乗るクローラー（spider）は元データに含まれていません
- `access_method` は `desktop`（PC のブラウザ）、`mobile-web`（モバイルのブラウザ）、`mobile-app`（公式アプリ）です
- 時刻と日付は UTC です。`hour` は 1 時間の始まりの時刻（`TIMESTAMP WITH TIME ZONE`）で、日本時間にするときは `hour AT TIME ZONE 'Asia/Tokyo'` にします。`daily` の `date` は UTC の日付なので、日本時間の 9 時から翌日 9 時までの閲覧数です

## ページと記事名

- 元データの 1 行は「リクエストされた記事名」と、転送を解決した「転送先のページの `page_id`」を持ちます。このデータセットは `page_id` ごとに合計しているので、転送ページ経由の閲覧（「!」から「感嘆符」など）は転送先のページに含まれます
- `page_id` を解決できなかったリクエスト（存在しない記事名や特別ページなど、閲覧数の約 1%）は入れていません
- `page` はデータベースダンプ（月 2 回）の時点のページです。転送ページは入れていません。ダンプより後に作られたページ・削除されたページは `page` にありません。ダンプより後に改名されたページは古い記事名のままです
- 記事名の空白は `_` です（「Call of Duty」は `Call_of_Duty`）。`page.title` は名前空間の接頭辞を除いた名前で、記事は `namespace = 0` です
- `daily_top` は記事（`namespace = 0`）だけで、メインページを除きます。`page` に無いページは、その日いちばん多くリクエストされた記事名にしています

## ビルド

```bash
git submodule update --init
uv sync
scripts/build.sh   # fdl checkout → python main.py → fdl commit
```

`main.py` は公開中のバージョンの最後の日の翌日から、Pageview complete dumps が公開済みの日までを取ります（1 回に最大 7 日分、`PAGEVIEWS_MAX_DAYS`）。1 日分のファイルは全言語で 1.5〜2GB あり、wiki の名前の順に並んでいるので、`ja.wikipedia` の行を読み終えたところで取得をやめます。`hourly`・`daily`・`daily_top` は新しい日だけを追加します。`page` は新しいデータベースダンプが出たときだけ作り直します。

- 最初の日は `PAGEVIEWS_FROM`（既定は 2026-10-01）です
- `PAGEVIEWS_DATES`（`2026-11-01,2026-11-02` のようなカンマ区切り）を渡すと、その日だけを取ります。PR のビルド確認（`.github/workflows/build.yml`）は 1 日分だけを取ります

Sync は毎日 15:00（日本時間）と、main への push・手動の実行（workflow_dispatch）で実行されます。
