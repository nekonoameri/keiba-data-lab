#!/usr/bin/env python3
"""Generate real race/date pages from SQLite. No placeholder races are created."""
from pathlib import Path
import sqlite3, html, json
ROOT=Path(__file__).resolve().parent; OUT=ROOT/'races'; OUT.mkdir(exist_ok=True)
TRACK_SLUG={'札幌':'sapporo','函館':'hakodate','福島':'fukushima','新潟':'niigata','東京':'tokyo','中山':'nakayama','中京':'chukyo','京都':'kyoto','阪神':'hanshin','小倉':'kokura'}
def e(x): return html.escape(str(x if x is not None else ''))
def yen(x): return f'{int(x):,}円' if x is not None else '—'
def shell(title,body): return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | KEIBA DATA LAB</title><style>*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 50% 0,#07327a 0,#031126 32%,#010714 75%);color:#eaf6ff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif}}a{{color:#58d8ff;text-decoration:none}}.wrap{{max-width:1120px;margin:auto;padding:28px 18px 70px}}header{{background:#020a18e8;border-bottom:1px solid #1164a8}}header .wrap{{padding:14px 18px}}.logo{{font-weight:900;letter-spacing:.12em;color:#fff;text-shadow:0 0 18px #18a9ff}}.hero,.card{{background:linear-gradient(145deg,#061a37dd,#020b1bdd);border:1px solid #1269aa;border-radius:18px;box-shadow:0 0 26px #008cff1d,inset 0 0 20px #008cff0c}}.hero{{padding:28px;margin:22px 0}}.card{{padding:20px;margin:0 0 18px}}.eyebrow,th{{color:#58d8ff}}h1{{font-size:clamp(27px,5vw,46px);margin:8px 0}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px 7px;border-bottom:1px solid #123454;text-align:left}}.pay{{font-size:34px;font-weight:900;text-shadow:0 0 18px #11b7ff}}.grid{{display:grid;grid-template-columns:1.45fr .55fr;gap:18px}}.pill{{display:inline-block;border:1px solid #1989cf;background:#06254b;padding:6px 10px;border-radius:999px;margin:4px}}.muted{{color:#8aa7bd}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><header><div class="wrap"><a class="logo" href="../index.html">KEIBA DATA LAB</a></div></header><main class="wrap">{body}</main></body></html>'''
def main():
    db=ROOT/'keiba.db'
    if not db.exists(): raise SystemExit('keiba.db not found; run import_csv.py first')
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row
    races=list(con.execute('SELECT * FROM races ORDER BY race_date,track,race_no'))
    generated=[]; bydate={}
    for r in races:
        runners=list(con.execute('SELECT * FROM runners WHERE race_id=? ORDER BY CASE WHEN finish IS NULL THEN 999 ELSE finish END,horse_no',(r['race_id'],)))
        slug=TRACK_SLUG.get(r['track'],'track'); fn=f"{r['race_date']}-{slug}-{int(r['race_no']):02d}.html"
        rows=''.join(f"<tr><td>{e(u['finish'])}</td><td>{e(u['frame_no'])}</td><td>{e(u['horse_no'])}</td><td>{e(u['horse_name'])}</td><td>{e(u['jockey'])}</td><td>{e(u['odds'])}</td><td>{e(u['popularity']) if u['popularity'] is not None else '—'}</td></tr>" for u in runners)
        body=f'''<div class="hero"><div class="eyebrow">OFFICIAL RESULT DATA / ANALYSIS</div><h1>{e(r['track'])} {r['race_no']}R　{e(r['race_name'])}</h1><span class="pill">{e(r['race_date'])}</span><span class="pill">{e(r['surface'])} {e(r['distance'])}m</span><span class="pill">{e(r['going'])}</span></div><div class="grid"><section><div class="card"><h2>全着順</h2><table><tr><th>着</th><th>枠</th><th>馬番</th><th>馬名</th><th>騎手</th><th>単勝</th><th>人気</th></tr>{rows}</table><p class="muted">人気は公式値を確認できた場合のみ表示します。未確認値は「—」です。</p></div><div class="card"><a href="../courses.html">コースデータ →</a>　<a href="../jockeys.html">騎手データ →</a>　<a href="../wild.html">荒れレース →</a></div></section><aside><div class="card"><div class="eyebrow">3連単</div><div class="pay">{yen(r['trifecta_payout'])}</div></div><div class="card"><b>出走頭数</b><p>{e(r['starters'])}頭</p></div></aside></div>'''
        (OUT/fn).write_text(shell(f"{r['race_date']} {r['track']}{r['race_no']}R",body),encoding='utf-8')
        generated.append(fn); bydate.setdefault(r['race_date'],[]).append((r,fn))
    for date,items in bydate.items():
        cards=''.join(f'<div class="card"><a href="races/{fn}"><b>{e(r["track"])} {r["race_no"]}R</b> {e(r["race_name"])} →</a><br><span class="muted">{e(r["surface"])} {e(r["distance"])}m / 3連単 {yen(r["trifecta_payout"])}</span></div>' for r,fn in items)
        (ROOT/f'date-{date}.html').write_text(shell(f'{date} レース結果',f'<div class="hero"><div class="eyebrow">DAILY RESULTS</div><h1>{date} レース結果</h1><p>DBに存在する実開催レースのみ掲載。</p></div>{cards}').replace('../index.html','index.html'),encoding='utf-8')
    archive=[]
    for date in sorted(bydate, reverse=True):
        archive.append(f'<a class="card" href="date-{date}.html"><b>{date}</b><span class="muted"> {len(bydate[date])}レース →</span></a>')
    archive_body='<div class="hero"><div class="eyebrow">VERIFIED RACE ARCHIVE</div><h1>実レース結果アーカイブ</h1><p>DBに取り込んだ検証済み開催日のみ掲載。</p></div><div>'+''.join(archive)+'</div>'
    (ROOT/'race-archive.html').write_text(shell('実レース結果アーカイブ',archive_body).replace('../index.html','index.html'),encoding='utf-8')
    manifest={'races':len(generated),'dates':len(bydate),'pages':generated}
    (ROOT/'data'/'db-race-page-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__': main()
