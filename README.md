# yt-playlist

TSV で管理している YouTube プレイリストを GitHub Pages 上で一覧表示するサイトです。

**公開URL: https://weinyen.github.io/yt-playlist/**

## 構成

- `data/playlist.tsv` — `タイトル<TAB>URL` 形式の元データ
- `data/playlist.json` — サイトが読み込む JSON（`scripts/tsv_to_json.py` で生成）
- `index.html` / `assets/` — 一覧ページ本体（検索・無限スクロール対応）
- `.github/workflows/pages.yml` — `main` への push で GitHub Pages に自動デプロイ

## データの更新方法

1. `data/playlist.tsv` を編集する（タイトル不明の行は `NA` と記載）
2. `python3 scripts/tsv_to_json.py` を実行して `data/playlist.json` を再生成する
3. 変更をコミットして `main` に push する

## GitHub Pages の設定

リポジトリの Settings → Pages → Source を **GitHub Actions** に設定してください（設定済み）。
設定後は `main` への push ごとに自動でデプロイされます。
