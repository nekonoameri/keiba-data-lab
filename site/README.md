# KEIBA DATA LAB v7 — 実データ接続版

確定した「濃紺＋青い発光」UIと、JRA成績PDF→SQLite→集計→画面表示を一つにした開発版です。

## 入っている画面
- トップ（本日の開催 / 注目レース / 競馬場 / 騎手 / コース / 穴データ / 荒れランキング / 荒れ条件 / 今週の穴 / 騎手ランキング / お知らせ）
- JRA LIVE導線
- 過去の荒れレース
- 荒れレース詳細
- コースデータ
- 騎手データ

## 一括処理
1. JRA年度別全成績PDFを `data/jra_pdf/` に置く
2. `pip install -r requirements.txt`
3. `python run_pipeline.py`
4. `index.html` を開く

処理内容: PDF解析 → races.csv/runners.csv → keiba.db → site-data.js/json → HTMLへ実データ表示。

## DBから自動生成するもの
- 3連単高配当「過去の荒れレースランキング」
- 1〜3着人気構成
- 競馬場×芝/ダート×距離の荒れ条件
- 騎手の騎乗数/勝率/複勝率/平均人気
- コース別平均3連単・人気薄馬券内率

## 注意
取得元の利用条件・掲載条件は運用前に確認してください。取得アダプターは交換可能な構造にしてあります。

## v10 expansion
- Top design/content preserved.
- 10 track pages.
- 130 track × course detail pages.
- 12 jockey detail pages + 120 jockey × track pages.
- 2022–2026 archive hubs.
- Internal links corrected from placeholder query URLs to generated static pages.
- Current generated HTML count is printed by expand_v10.py.

Real numeric values remain intentionally blank until the data import pipeline has verified source data; no fabricated racing results are shipped.

## v11 — 実開催レースページ自動生成
- `generate_race_pages.py` を追加。
- `data/verified_races.csv` の実開催レースだけを `/races/` に個別HTML化。
- 開催日ハブ `date-YYYY-MM-DD.html` も自動生成。
- 個別ページに着順上位3頭、騎手、単勝オッズ、3連単、人気構成、試作荒れ度、関連導線を表示。
- サンプルはJRA公式 2026-09-13 中山成績表から確認できた1R〜3Rのみ収録。未確認値は入れていません。
- 本番ではPDFアダプター→SQLite→CSV/JSON→このジェネレーターへ接続し、実開催分だけ増える設計です。

実行: `python generate_race_pages.py`

## v12 — PDF→DB→全レースページ直結
- `fetch_jra_pdfs.py`: JRA公式の年度別全成績ページから、公開されている成績PDFリンクを発見して順番に保存（既存PDFはスキップ）。
- `jra_pdf_adapter.py`: 年を2026固定にせず20xx年を解析。PDFだけでは全馬の「公式人気」を安全に復元できないため、人気は推測せず空欄にする方針へ修正。
- `generate_db_race_pages.py`: `keiba.db` に実在するレースだけを個別HTML化し、開催日ハブも生成。
- `update_site.py`: 取得→PDF解析→SQLite→集計JSON→レースページ生成を一括実行。

### 一括更新
```bash
pip install -r requirements.txt
python update_site.py --fetch --year 2026
```
テスト時は `--limit 2` のように取得PDF数を制限できます。

### データ品質
JRA公式PDFで確実に読める値と、推測値を混ぜない設計です。単勝人気はPDF抽出だけでは全出走馬について確実に復元できないため、現段階では未確認値を `—` と表示します。次段階でJRAの個別結果ページ用アダプターを追加し、公式人気を補完する設計です。
