from pathlib import Path
import re, html, shutil
root=Path(__file__).parent
tracks=['札幌','函館','福島','新潟','東京','中山','中京','京都','阪神','小倉']
courses=['芝1200m','芝1400m','芝1600m','芝1800m','芝2000m','芝2200m','芝2400m','ダート1200m','ダート1400m','ダート1600m','ダート1700m','ダート1800m','ダート2100m']
jockeys=['騎手A','騎手B','騎手C','騎手D','騎手E','騎手F','騎手G','騎手H','騎手I','騎手J','騎手K','騎手L']
base=(root/'index.html').read_text()
css=re.search(r'<style>(.*?)</style>',base,re.S).group(1)
extra='''.breadcrumb{color:#79b9e5;font-size:13px;margin-bottom:14px}.directory{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.directory a{text-decoration:none}.list-links{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.list-links a{padding:12px;border:1px solid #0c5c99;border-radius:7px;text-decoration:none;background:#041329}.hero.small{min-height:210px;padding:35px 5%}.hero.small h1{font-size:38px}.metric{font-size:24px;font-weight:900}.empty{padding:20px;text-align:center;color:#8db0ca;border:1px dashed #18577f;border-radius:8px}@media(max-width:800px){.directory,.list-links{grid-template-columns:1fr 1fr}}'''
def page(title,body,active=''):
 nav=[('index.html','トップ'),('live.html','● JRA LIVE'),('tracks.html','競馬場データ'),('jockeys.html','騎手データ'),('courses.html','コースデータ'),('holes.html','穴データ'),('wild.html','過去の荒れレース'),('analysis.html','データ分析'),('columns.html','コラム'),('archive.html','年度別結果')]
 n=''.join(f'<a class="{"active" if l==active else ""}" href="{h}">{l}</a>' for h,l in nav)
 return f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}｜競馬データ研究所</title><style>{css}{extra}</style></head><body><header class="site-header"><div class="head"><a class="brand" href="index.html">♞ 競馬データ研究所<small>KEIBA DATA LAB</small></a><input class="search" placeholder="騎手名・競馬場・レース名・距離などで検索"></div><nav class="nav">{n}</nav></header>{body}<footer class="footer">♞ 競馬データ研究所 — “データで、競馬をもっと面白く。”</footer></body></html>'
def shell(title,lead,inner,crumb):
 return f'<section class="hero small"><div><div class="eyebrow">KEIBA DATA LAB</div><h1>{title}</h1><p>{lead}</p></div></section><main class="wrap"><div class="breadcrumb"><a href="index.html">トップ</a> › {crumb}</div>{inner}</main>'
# fix top track links to actual pages
idx=(root/'index.html').read_text()
for i,t in enumerate(tracks): idx=idx.replace(f'track.html?name={t}',f'track-{i}.html')
(root/'index.html').write_text(idx)
# track x course pages
for ti,t in enumerate(tracks):
 for ci,c in enumerate(courses):
  fn=f'course-{ti}-{ci}.html'
  inner=f'''<div class="grid"><section class="panel full"><div class="section-head"><h2>{t} {c}</h2><span class="tag">DB自動更新</span></div><div class="stat-grid"><div class="statbox"><span class="mini">対象レース</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">平均3連単</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">万馬券率</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">荒れ度</span><div class="metric">分析中</div></div></div></section><section class="panel"><h2>騎手ランキング</h2><table class="table"><tr><th>騎手</th><th>勝率</th><th>複勝率</th></tr><tr><td>実データ接続後</td><td>—</td><td>—</td></tr></table><a class="cta secondary" href="jockey-ranking.html">全騎手 →</a></section><section class="panel"><h2>枠順・人気別</h2><div class="list-links"><a href="analysis.html">枠順成績</a><a href="analysis.html">人気別成績</a><a href="holes.html">穴馬成績</a><a href="wild.html">高配当レース</a></div></section><section class="panel full"><h2>過去の荒れレース</h2><div class="empty">{t} {c} の高配当レースを配当順に自動表示します。</div></section><section class="panel"><h2>関連コース</h2><div class="list-links">{''.join(f'<a href="course-{ti}-{x}.html">{courses[x]}</a>' for x in range(max(0,ci-2),min(len(courses),ci+3)) if x!=ci)}</div></section><section class="panel"><h2>関連データ</h2><div class="list-links"><a href="track-{ti}.html">{t}競馬場</a><a href="holes.html">穴データ</a><a href="wild.html">荒れランキング</a><a href="archive-2026.html">2026結果</a></div></section></div>'''
  (root/fn).write_text(page(f'{t}{c}データ',shell(f'{t} {c}', '騎手・枠・人気・配当・荒れ傾向をまとめて分析。',inner,f'競馬場データ › {t} › {c}'),'コースデータ'))
# rewrite track pages course links
for ti,t in enumerate(tracks):
 p=root/f'track-{ti}.html'; s=p.read_text()
 for ci,c in enumerate(courses): s=re.sub(rf'href="course\.html\?track={re.escape(t)}&course={re.escape(c)}"',f'href="course-{ti}-{ci}.html"',s)
 p.write_text(s)
# jockey detail + track pages
for ji,j in enumerate(jockeys):
 links=''.join(f'<a href="jockey-{ji}-track-{ti}.html">{t}</a>' for ti,t in enumerate(tracks))
 inner=f'''<div class="grid"><section class="panel full"><h2>{j} 総合成績</h2><div class="stat-grid"><div class="statbox"><span class="mini">騎乗数</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">勝率</span><div class="metric">—</div></div><div class="statbox"><span class="mini">複勝率</span><div class="metric">—</div></div><div class="statbox"><span class="mini">平均人気</span><div class="metric">—</div></div></div></section><section class="panel"><h2>競馬場別</h2><div class="list-links">{links}</div></section><section class="panel"><h2>人気別・穴成績</h2><div class="list-links"><a href="holes.html">1〜3人気</a><a href="holes.html">4〜6人気</a><a href="holes.html">7人気以下</a><a href="hole-jockey-ranking.html">穴騎手比較</a></div></section></div>'''
 (root/f'jockey-{ji}.html').write_text(page(j,shell(j,'競馬場・コース・人気・枠別に騎乗成績を分析。',inner,f'騎手データ › {j}'),'騎手データ'))
 for ti,t in enumerate(tracks):
  cin=''.join(f'<a href="course-{ti}-{ci}.html">{c}</a>' for ci,c in enumerate(courses))
  inner2=f'<div class="grid"><section class="panel full"><h2>{j} × {t}</h2><div class="empty">勝率・連対率・複勝率・回収率をDBから集計。</div></section><section class="panel"><h2>コース別</h2><div class="list-links">{cin}</div></section><section class="panel"><h2>関連</h2><div class="list-links"><a href="jockey-{ji}.html">{j}総合</a><a href="track-{ti}.html">{t}競馬場</a><a href="wild.html">荒れレース</a><a href="holes.html">穴データ</a></div></section></div>'
  (root/f'jockey-{ji}-track-{ti}.html').write_text(page(f'{j} {t}成績',shell(f'{j} × {t}','この競馬場でのコース別・人気別成績。',inner2,f'騎手データ › {j} › {t}'),'騎手データ'))
# rewrite jockey directory links
s=(root/'jockeys.html').read_text()
for ji,j in enumerate(jockeys): s=s.replace(f'jockey.html?j={j}',f'jockey-{ji}.html')
(root/'jockeys.html').write_text(s)
# year archives
for year in [2026,2025,2024,2023,2022]:
 cards=''.join(f'<a class="card" href="track-{i}.html"><strong>{t}</strong><span class="mini">{year}年の開催結果 →</span></a>' for i,t in enumerate(tracks))
 inner=f'<section class="panel"><div class="section-head"><h2>{year}年 中央競馬</h2><a class="cta secondary" href="archive.html">年度一覧 →</a></div><div class="directory">{cards}</div></section><section class="panel"><h2>開催日別</h2><div class="empty">DB接続後、開催日 → 競馬場 → 1R〜12R のレース詳細ページを自動生成します。</div></section>'
 (root/f'archive-{year}.html').write_text(page(f'{year}年レース結果',shell(f'{year}年レース結果','開催日・競馬場・各レースへ辿れる年度アーカイブ。',inner,f'年度別結果 › {year}'),'年度別結果'))
# archive hub
cards=''.join(f'<a class="card" href="archive-{y}.html"><strong>{y}年</strong><span class="mini">中央競馬結果 →</span></a>' for y in [2026,2025,2024,2023,2022])
(root/'archive.html').write_text(page('年度別レース結果',shell('年度別レース結果','年度 → 開催日 → 競馬場 → 各レースへ。',f'<section class="panel"><div class="directory">{cards}</div></section>','年度別結果'),'年度別結果'))
print('HTML',len(list(root.glob('*.html'))))
