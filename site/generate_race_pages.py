from pathlib import Path
import csv, html, json, re, sqlite3
ROOT=Path(__file__).parent
DATA=ROOT/'data'
OUT=ROOT/'races'
OUT.mkdir(exist_ok=True)

def yen(v):
    return f"{int(v):,}円" if v not in (None,'') else '—'

def esc(x): return html.escape(str(x or ''))

def shell(title, body):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | KEIBA DATA LAB</title><style>
    *{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 50% 0,#07327a 0,#031126 32%,#010714 75%);color:#eaf6ff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif}}a{{color:#58d8ff;text-decoration:none}}.wrap{{max-width:1120px;margin:auto;padding:28px 18px 70px}}header{{position:sticky;top:0;background:#020a18e8;border-bottom:1px solid #1164a8;backdrop-filter:blur(12px);z-index:3}}header .wrap{{padding:14px 18px;display:flex;gap:20px;align-items:center}}.logo{{font-weight:900;letter-spacing:.12em;color:#fff;text-shadow:0 0 18px #18a9ff}}nav{{margin-left:auto;display:flex;gap:14px;flex-wrap:wrap;font-size:13px}}.hero,.card{{background:linear-gradient(145deg,#061a37dd,#020b1bdd);border:1px solid #1269aa;border-radius:18px;box-shadow:0 0 26px #008cff1d,inset 0 0 20px #008cff0c}}.hero{{padding:30px;margin:22px 0}}.eyebrow{{color:#58d8ff;font-weight:800;letter-spacing:.12em}}h1{{font-size:clamp(28px,5vw,48px);margin:8px 0}}.meta{{display:flex;gap:10px;flex-wrap:wrap}}.pill{{border:1px solid #1989cf;background:#06254b;padding:7px 11px;border-radius:999px}}.grid{{display:grid;grid-template-columns:1.4fr .6fr;gap:18px}}.card{{padding:20px;margin-bottom:18px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:11px 8px;border-bottom:1px solid #123454;text-align:left}}th{{color:#78dfff}}.pay{{font-size:32px;font-weight:900;color:#fff;text-shadow:0 0 18px #11b7ff}}.score{{font-size:44px;font-weight:900;color:#66e6ff}}.muted{{color:#8aa7bd}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}nav{{display:none}}}}
    </style></head><body><header><div class="wrap"><a class="logo" href="../index.html">KEIBA DATA LAB</a><nav><a href="../today.html">今日の競馬</a><a href="../live.html">JRA LIVE</a><a href="../tracks.html">競馬場</a><a href="../jockeys.html">騎手</a><a href="../wild.html">荒れレース</a></nav></div></header><main class="wrap">{body}</main></body></html>'''

def build_race(r):
    score=min(100, round((int(r.get('trifecta') or 0)/100000)*35 + sum(max(0,int(r.get(k) or 0)-3) for k in ('p1','p2','p3'))*5))
    title=f"{r['date']} {r['track']}{r['race_no']}R {r['race_name']}"
    body=f'''<div class="hero"><div class="eyebrow">RACE RESULT / DATA ANALYSIS</div><h1>{esc(r['track'])} {esc(r['race_no'])}R　{esc(r['race_name'])}</h1><div class="meta"><span class="pill">{esc(r['date'])}</span><span class="pill">{esc(r['surface'])} {esc(r['distance'])}m</span><span class="pill">発走 {esc(r['start_time'])}</span><span class="pill">{esc(r.get('going',''))}</span></div></div>
    <div class="grid"><section><div class="card"><h2>レース結果</h2><table><tr><th>着順</th><th>馬名</th><th>騎手</th><th>単勝オッズ</th></tr>{''.join(f'<tr><td>{i}</td><td>{esc(r.get(f"horse{i}"))}</td><td>{esc(r.get(f"jockey{i}"))}</td><td>{esc(r.get(f"odds{i}"))}</td></tr>' for i in range(1,4))}</table></div><div class="card"><h2>同条件データへ</h2><p><a href="../courses.html">{esc(r['track'])}・{esc(r['surface'])}{esc(r['distance'])}m のコースデータを見る →</a></p><p><a href="../jockeys.html">騎手データを見る →</a></p><p><a href="../wild.html">過去の荒れレースランキングを見る →</a></p></div></section><aside><div class="card"><div class="eyebrow">3連単</div><div class="pay">{yen(r.get('trifecta'))}</div><p class="muted">公式成績表の払戻データ</p></div><div class="card"><div class="eyebrow">荒れ度</div><div class="score">{score}</div><p>100点満点の試作指標。3連単配当と上位人気構成から算出。</p></div><div class="card"><h3>人気構成</h3><p>1着 {esc(r.get('p1'))}番人気<br>2着 {esc(r.get('p2'))}番人気<br>3着 {esc(r.get('p3'))}番人気</p></div></aside></div>'''
    path=OUT/f"{r['date']}-{r['track_slug']}-{r['race_no']:02d}.html"
    path.write_text(shell(title,body),encoding='utf-8')
    return path.name

def main():
    csvp=DATA/'verified_races.csv'
    rows=[]
    if csvp.exists():
        with csvp.open(encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                r['race_no']=int(r['race_no']); rows.append(r)
    pages=[build_race(r) for r in rows]
    # date hub
    if rows:
        date=rows[0]['date']; cards=''.join(f'<div class="card"><a href="races/{p}"><b>{esc(r["track"])} {r["race_no"]}R</b>　{esc(r["race_name"])} →</a><br><span class="muted">{esc(r["surface"])} {esc(r["distance"])}m / 3連単 {yen(r.get("trifecta"))}</span></div>' for r,p in zip(rows,pages))
        (ROOT/f'date-{date}.html').write_text(shell(f'{date} レース結果',f'<div class="hero"><div class="eyebrow">DAILY RESULTS</div><h1>{date} レース結果</h1><p>DBに取り込まれた実開催レースだけを自動生成します。</p></div>{cards}'),encoding='utf-8')
    manifest={'generated_race_pages':len(pages),'source_csv':str(csvp.relative_to(ROOT)) if csvp.exists() else None,'pages':pages}
    (DATA/'race-page-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__': main()
