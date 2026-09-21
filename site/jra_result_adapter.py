#!/usr/bin/env python3
"""Enrich SQLite runner rows from official JRA race-result HTML pages.

Input: a text/CSV file containing official JRA result URLs (one URL per line, or a
column named source_url). The parser writes ONLY fields visibly present on the
official result page: official popularity, jockey, horse name, frame/horse no,
finish, time and race metadata. Existing PDF-derived rows are updated by
race-date/track/race-no + horse number.

This deliberately does not guess JRA URL check-suffixes or crawl arbitrary pages.
"""
from __future__ import annotations
import argparse,csv,re,sqlite3,time
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
UA='KEIBA-DATA-LAB/0.13 (+local research prototype; sequential official-page fetch)'
TRACKS='札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉'

def urls_from(path:Path):
    txt=path.read_text(encoding='utf-8-sig')
    if path.suffix.lower()=='.csv':
        rows=list(csv.DictReader(txt.splitlines())); return [r.get('source_url','').strip() for r in rows if r.get('source_url','').strip()]
    return [x.strip() for x in txt.splitlines() if x.strip() and not x.lstrip().startswith('#')]

def parse(url,html):
    soup=BeautifulSoup(html,'html.parser'); text=' '.join(soup.stripped_strings)
    m=re.search(r'(20\d{2})年(\d{1,2})月(\d{1,2})日.*?(?:\d+回)?('+TRACKS+r')\d+日.*?(\d+)レース',text)
    if not m: raise ValueError('race header not found')
    date=f'{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'; track=m.group(4); rn=int(m.group(5)); rid=f'{date.replace("-","")}-{track}-{rn:02d}'
    surface='芝' if re.search(r'メートル（芝',text) else ('ダート' if re.search(r'メートル（ダート',text) else '')
    dm=re.search(r'コース：([\d,]+)メートル',text); distance=int(dm.group(1).replace(',','')) if dm else None
    gm=re.search(r'(?:芝|ダート)(良|稍重|重|不良)',text); going=gm.group(1) if gm else ''
    # JRA result tables have stable semantic headers. Parse each tr by cell text.
    runners=[]
    for tr in soup.find_all('tr'):
        cells=[' '.join(td.stripped_strings) for td in tr.find_all(['th','td'])]
        if len(cells)<8 or not re.fullmatch(r'\d+|中止|除外|取消',cells[0] or ''): continue
        # Typical columns: finish, frame(img may blank), horse no, horse, sexage, weight, jockey, time,..., popularity
        nums=[i for i,c in enumerate(cells[:5]) if re.fullmatch(r'1[0-8]|[1-9]',c)]
        if not nums: continue
        horse_idx=nums[-1]; horse_no=int(cells[horse_idx])
        finish=int(cells[0]) if cells[0].isdigit() else None
        horse_name=cells[horse_idx+1] if horse_idx+1<len(cells) else ''
        # jockey usually after sex/age + assigned weight
        jockey=''; finish_time=''; popularity=None
        for c in cells[horse_idx+2:]:
            if not finish_time and re.fullmatch(r'\d:\d{2}\.\d',c): finish_time=c
        if cells and re.fullmatch(r'\d{1,2}',cells[-1]): popularity=int(cells[-1])
        # Use link target patterns when available to identify jockey name.
        for a in tr.find_all('a'):
            href=a.get('href',''); label=' '.join(a.stripped_strings)
            if ('jockey' in href.lower() or 'pw01k' in href.lower()) and label: jockey=label; break
        if not jockey:
            # fallback: cell between assigned weight and time
            for i,c in enumerate(cells):
                if re.fullmatch(r'\d{2}(?:\.\d)?',c) and i+1<len(cells) and not re.fullmatch(r'\d:\d{2}\.\d',cells[i+1]): jockey=cells[i+1]; break
        frame=None
        img=tr.find('img',alt=re.compile('枠'))
        if img:
            fm=re.search(r'枠(\d)',img.get('alt','')); frame=int(fm.group(1)) if fm else None
        runners.append(dict(horse_no=horse_no,finish=finish,horse_name=horse_name,jockey=jockey,popularity=popularity,finish_time=finish_time,frame_no=frame))
    # Official payout: store the first 3連単 payout when present.
    trifecta=None
    pm=re.search(r'3連単\s+[^\n]*?([\d,]+)円',text)
    if pm:
        try: trifecta=int(pm.group(1).replace(',',''))
        except: pass
    return dict(race_id=rid,race_date=date,track=track,race_no=rn,surface=surface,distance=distance,going=going,trifecta_payout=trifecta,source_url=url),runners

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('--db',default='keiba.db'); ap.add_argument('--delay',type=float,default=1.0); a=ap.parse_args()
    con=sqlite3.connect(ROOT/a.db); con.execute('PRAGMA foreign_keys=ON')
    urls=urls_from(Path(a.input)); updated=0
    for n,url in enumerate(urls,1):
        if urlparse(url).netloc not in {'www.jra.go.jp','jra.go.jp'}: raise SystemExit(f'non-JRA URL rejected: {url}')
        r=requests.get(url,headers={'User-Agent':UA},timeout=30); r.raise_for_status(); race, runners=parse(url,r.text)
        con.execute('''INSERT INTO races(race_id,race_date,track,race_no,surface,distance,going,trifecta_payout,source_url) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(race_id) DO UPDATE SET surface=COALESCE(excluded.surface,races.surface),distance=COALESCE(excluded.distance,races.distance),going=CASE WHEN excluded.going<>'' THEN excluded.going ELSE races.going END,trifecta_payout=COALESCE(excluded.trifecta_payout,races.trifecta_payout),source_url=excluded.source_url''',(race['race_id'],race['race_date'],race['track'],race['race_no'],race['surface'],race['distance'],race['going'],race['trifecta_payout'],url))
        for u in runners:
            con.execute('''INSERT INTO runners(race_id,horse_no,finish,frame_no,horse_name,jockey,popularity,finish_time) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(race_id,horse_no) DO UPDATE SET finish=COALESCE(excluded.finish,runners.finish),frame_no=COALESCE(excluded.frame_no,runners.frame_no),horse_name=CASE WHEN excluded.horse_name<>'' THEN excluded.horse_name ELSE runners.horse_name END,jockey=CASE WHEN excluded.jockey<>'' THEN excluded.jockey ELSE runners.jockey END,popularity=COALESCE(excluded.popularity,runners.popularity),finish_time=CASE WHEN excluded.finish_time<>'' THEN excluded.finish_time ELSE runners.finish_time END''',(race['race_id'],u['horse_no'],u['finish'],u['frame_no'],u['horse_name'],u['jockey'],u['popularity'],u['finish_time']))
            updated+=1
        con.commit(); print(f'[{n}/{len(urls)}] {race["race_id"]}: {len(runners)} runners')
        if n<len(urls): time.sleep(max(0,a.delay))
    print(f'DONE: {len(urls)} official result pages, {updated} runner rows enriched')
if __name__=='__main__': main()
