{# 記事名が標準以外の名前空間の接頭辞（「Category:」「ノート:」など）で始まるか。
   日本語版の名前空間名と、英語の正式名・別名を並べる。「Re:ゼロから始める…」のような記事は接頭辞に当たらない #}
{% macro namespaced(title) -%}
    regexp_matches({{ title }}, '^(特別|ノート|利用者|利用者‐会話|Wikipedia|Wikipedia‐ノート|ファイル|ファイル‐ノート|MediaWiki|MediaWiki‐ノート|Template|Template‐ノート|Help|Help‐ノート|Category|Category‐ノート|Portal|Portal‐ノート|プロジェクト|プロジェクト‐ノート|モジュール|モジュール‐ノート|Module|Special|Talk|User|User_talk|File|Image|Project|Draft|TimedText|Gadget|Topic):')
{%- endmacro %}
