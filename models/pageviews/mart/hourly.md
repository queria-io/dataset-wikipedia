---
$schema: https://queria.io/schemas/table/v1.json
table: pageviews.hourly
title: 1 時間ごとの閲覧数
description: |-
  ページごとの 1 時間の閲覧数です。1 行が 1 時間・1 ページ・1 アクセス方法・人か bot か の組で、Wikimedia が公開する最も細かい粒度です。

  - hour は UTC です。日本時間にするときは hour AT TIME ZONE 'Asia/Tokyo' にします
  - 転送ページ経由の閲覧は転送先のページに含みます
  - 大きいので、hour と page_id で絞って検索します
primary_key: [hour, page_id, access_method, agent_type]
sources:
  - path: https://dumps.wikimedia.org/other/pageview_complete/
fields:
  - name: hour
    title: 時間
    description: 1 時間の始まり（UTC）
  - name: page_id
    title: ページ ID
    description: page.page_id
  - name: access_method
    title: アクセス方法
    description: desktop（PC）、mobile-web（モバイルのブラウザ）、mobile-app（公式アプリ）
    semantic: {role: dimension}
  - name: agent_type
    title: 利用者の種類
    description: user（人）、automated（bot と判定されたアクセス）
    semantic: {role: dimension}
  - name: views
    title: 閲覧数
    semantic: {role: measure, agg: sum}
  - name: source_sha256
    title: 元のファイル
    description: この行を読んだ Pageview complete dumps のファイルの sha256。source_file の sha256 で結合できる。この列を追加する前に追加した行は NULL
---
