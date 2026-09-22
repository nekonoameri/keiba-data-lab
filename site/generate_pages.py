from pathlib import Path
import html
root=Path(__file__).parent
tracks=['札幌','函館','福島','新潟','東京','中山','中京','京都','阪神','小倉']
courses=['芝1200m','芝1400m','芝1600m','芝1800m','芝2000m','芝2200m','芝2400m','ダート1200m','ダート1400m','ダート1600m','ダート1700m','ダート1800m','ダート2100m']
css=(root/'style.css').read_text()
extra='''\n.breadcrumb{color:#79b9e5;font-size:13px;margin-bottom:14px}.directory{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.directory a{text-decoration:none}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.metric{font-size:24px;font-weight:900}.list-links{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.list-links a{padding:12px;border:1px solid #0c5c99;border-radius:7px;text-decoration:none;background:#041329}.hero.small{min-height:210px;padding:35px 5%}.hero.small h1{font-size:38px}.pill{display:inline-block;border:1px solid #1686ca;border-radius:999px;padding:5px 10px;margin:3px;color:#aee8ff}.empty{padding:20px;text-align:center;color:#8db0ca;border:1px dashed #18577f;border-radius:8px}@media(max-width:800px){.directory,.list-links{grid-template-columns:1fr 1fr}}'''

def page(title, body, active=''):
    nav=[('index.html','トップ'),('live.html','● JRA LIVE'),('tracks.html','競馬場データ'),('jockeys.html','騎手データ'),('courses.html','コースデータ'),('holes.html','穴データ'),('wild.html','過去の荒れレース'),('analysis.html','データ分析'),('columns.html','コラム')]
    n=''.join(f'<a class="{"active" if label==active else ""}" href="{href}">{label}</a>' for href,label in nav)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}｜競馬データ研究所</title><style>{css}{extra}</style></head><body><header class="site-header"><div class="head"><a class="brand" href="index.html">♞ 競馬データ研究所<small>KEIBA DATA LAB</small></a><input class="search" placeholder="騎手名・競馬場・レース名・距離などで検索"></div><nav class="nav">{n}</nav></header>{body}<footer class="footer">♞ 競馬データ研究所 — “データで、競馬をもっと面白く。”</footer><script src="script.js"></script><script src="site-data.js"></script><script src="data-ui.js"></script></body></html>'''

def shell(title, lead, inner, crumb='トップ'):
    return f'<section class="hero small"><div><div class="eyebrow">KEIBA DATA LAB</div><h1>{title}</h1><p>{lead}</p></div></section><main class="wrap"><div class="breadcrumb"><a href="index.html">トップ</a> › {crumb}</div>{inner}</main>'

# directories
track_cards=''.join(f'<a class="card" href="track-{i}.html"><strong>{t}</strong><span class="mini">コース・騎手・荒れ傾向 →</span></a>' for i,t in enumerate(tracks))
(root/'tracks.html').write_text(page('競馬場データ',shell('競馬場データ','中央競馬10場を、コース・騎手・枠・人気・荒れ傾向から横断分析。',f'<section class="panel"><div class="directory">{track_cards}</div></section>','競馬場データ'),'競馬場データ'))
for i,t in enumerate(tracks):
    links=''.join(f'<a href="course.html?track={t}&course={c}">{c}</a>' for c in courses)
    inner=f'''<div class="grid"><section class="panel full"><h2>{t}競馬場</h2><div class="stat-grid"><div class="statbox"><span class="mini">登録レース</span><div class="metric">DB連携</div></div><div class="statbox"><span class="mini">平均3連単</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">万馬券率</span><div class="metric">自動集計</div></div><div class="statbox"><span class="mini">穴馬複勝率</span><div class="metric">自動集計</div></div></div></section><section class="panel"><h2>コースから探す</h2><div class="list-links">{links}</div></section><section class="panel"><h2>この競馬場のデータ</h2><div class="list-links"><a href="jockey-ranking.html?track={t}">騎手ランキング</a><a href="wild.html?track={t}">荒れレース</a><a href="holes.html?track={t}">穴データ</a><a href="analysis.html?track={t}">条件分析</a></div></section><section class="panel full"><h2>直近レース</h2><div class="empty">DB接続後、{t}の直近レース結果を自動表示します。</div></section></div>'''
    (root/f'track-{i}.html').write_text(page(f'{t}競馬場データ',shell(f'{t}競馬場','コース別・騎手別・人気別・荒れ傾向を一画面で確認。',inner,f'競馬場データ › {t}'),'競馬場データ'))

# generic section pages
sections={
'jockeys.html':('騎手データ','騎手を検索し、競馬場別・コース別・人気別・枠別の成績へ。','騎手データ'),
'courses.html':('コースデータ','競馬場 × 芝/ダート × 距離から、騎手・枠・人気・荒れ度を分析。','コースデータ'),
'holes.html':('穴データ','人気薄の好走、穴騎手、穴コース、高配当条件をデータから探す。','穴データ'),
'analysis.html':('データ分析','荒れやすい条件、人気別傾向、枠順、距離、馬場状態を横断分析。','データ分析'),
'columns.html':('コラム','競馬データの見方や、コース・騎手・荒れ傾向の読み解き方。','コラム'),
'news.html':('お知らせ','データ更新・新機能・サイト更新情報。',''),
'jockey-ranking.html':('今週の騎手ランキング','直近成績・勝率・複勝率・コース適性を表示。','騎手データ'),
'hole-jockey-ranking.html':('今週の穴騎手ランキング','人気帯と着順・回収率から穴騎手を抽出。','穴データ'),
'today.html':('本日の中央競馬','開催場・全レース・発走時刻・注目データを一覧表示。',''),
'archive.html':('年度別レース結果','年度 → 開催日 → 競馬場 → 各レースへ辿れるアーカイブ。',''),
}
for fn,(title,lead,active) in sections.items():
    if fn=='jockeys.html':
        content='''<section class="panel"><div class="section-head"><h2>騎手一覧</h2><input id="jockey-search" class="search" placeholder="騎手名を検索"></div><p class="muted">実データから直近12か月の騎乗実績がある騎手を優先表示します。</p><div id="jockey-directory" class="directory"><div class="empty">騎手データを読み込み中…</div></div></section>'''
    elif fn=='courses.html':
        content='<section class="panel"><h2>主要コース</h2><div class="directory">'+''.join(f'<a class="card" href="course.html?course={c}"><strong>{c}</strong><span class="mini">全競馬場から比較 →</span></a>' for c in courses)+'</div></section>'
    elif fn=='holes.html':
        content='<div class="grid"><section class="panel"><h2>穴騎手</h2><p>4〜6番人気・7番人気以下など人気帯別に好走率を集計。</p><a class="cta" href="hole-jockey-ranking.html">ランキング →</a></section><section class="panel"><h2>穴コース</h2><p>人気薄が馬券内に入りやすい競馬場×距離を抽出。</p></section><section class="panel"><h2>高配当傾向</h2><p>3連単・3連複などの高配当発生条件を分析。</p></section><section class="panel"><h2>条件一致検索</h2><p>馬場・頭数・距離・人気など複数条件で絞り込み。</p></section></div>'
    elif fn=='columns.html':
        content='<section class="panel"><div class="cards"><a class="card" href="column.html"><strong>荒れるレースの探し方</strong><span class="mini">データの読み方</span></a><a class="card" href="column.html"><strong>騎手×コースを見る</strong><span class="mini">適性分析</span></a><a class="card" href="column.html"><strong>人気と回収率</strong><span class="mini">穴データ</span></a></div></section>'
    else:
        content='<div class="grid"><section class="panel full"><h2>'+title+'</h2><div class="empty">実データ接続後、このページはDBから自動生成・自動更新されます。</div></section><section class="panel"><h2>絞り込み</h2><div class="chips"><span class="chip active">直近1年</span><span class="chip">3年</span><span class="chip">5年</span><span class="chip">10年</span></div></section><section class="panel"><h2>関連データ</h2><div class="list-links"><a href="wild.html">荒れレース</a><a href="courses.html">コース</a><a href="jockeys.html">騎手</a><a href="holes.html">穴データ</a></div></section></div>'
    (root/fn).write_text(page(title,shell(title,lead,content,title),active))

(root/'column.html').write_text(page('コラム詳細',shell('荒れるレースの探し方','配当だけでなく、人気構成・頭数・馬場・コースを組み合わせて見る。','<section class="panel"><h2>データを見るポイント</h2><p>このページはコラム本文テンプレートです。関連記事としてコースデータ、荒れレース、穴騎手へ内部リンクします。</p><div class="list-links"><a href="wild.html">過去の荒れレース</a><a href="analysis.html">荒れ条件分析</a><a href="holes.html">穴データ</a><a href="courses.html">コースデータ</a></div></section>','コラム › 記事'),'コラム'))
(root/'archive.html').write_text((root/'archive.html').read_text())
print('generated',len(list(root.glob('*.html'))),'html files')
