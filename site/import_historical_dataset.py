#!/usr/bin/env python3
"""Normalize the public historical JRA race-result CSV into KEIBA DATA LAB runners.csv.
Expected source: takamotoki/JRA horse racing dataset (1986-2021).
"""
import argparse,csv,re
from pathlib import Path

def g(r,*names):
    for n in names:
        v=r.get(n)
        if v not in (None,'', 'nan'): return str(v).strip()
    return ''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('--out',default='runners.csv'); ap.add_argument('--races-out',default='races.csv'); a=ap.parse_args()
    src=Path(a.input); root=Path(__file__).resolve().parent; out=root/a.out; races_out=root/a.races_out
    fields=['race_id','finish','frame_no','horse_no','horse_name','jockey','popularity','odds','finish_time','last3f']
    n=0; races={}
    with src.open(encoding='utf-8-sig',newline='') as f, out.open('w',encoding='utf-8',newline='') as o:
        rd=csv.DictReader(f); wr=csv.DictWriter(o,fieldnames=fields); wr.writeheader()
        for r in rd:
            rid=g(r,'レースID','race_id','Race ID')
            course=g(r,'コース','course','Course')
            surf='芝' if '芝' in course else ('ダート' if 'ダ' in course else '')
            dist=g(r,'距離','距離（m）','distance','Distance')
            if not dist:
                m=re.search(r'(\d{3,4})',course); dist=m.group(1) if m else ''
            row={'race_id':rid,'finish':g(r,'着順','finish_position'),'frame_no':g(r,'枠番','frame'),'horse_no':g(r,'馬番','horse_number'),'horse_name':g(r,'馬名','horse_name'),'jockey':g(r,'騎手名','騎手','jockey'),'popularity':g(r,'人気','popularity'),'odds':g(r,'オッズ（単勝）','単勝','odds'),'finish_time':g(r,'タイム','finish_time'),'last3f':g(r,'上り','上がり','last_3f')}
            try:
                hn=int(float(row['horse_no']))
            except: hn=0
            try:
                pop=int(float(row['popularity'])) if row['popularity'] else None
            except: pop=None
            if rid and 1 <= hn <= 18 and (pop is None or 1 <= pop <= 18):
                row['horse_no']=str(hn); row['popularity']='' if pop is None else str(pop)
                wr.writerow(row); n+=1
                if rid not in races:
                    races[rid]={'race_id':rid,'race_date':g(r,'レース日付','日付','date','Race Day'),'track':g(r,'競馬場名','開催場所','track','Racecourse Name'),'race_no':g(r,'レース番号','何レース目','race_no'),'race_name':g(r,'レース名','race_name','Race Name'),'surface':surf,'distance':dist,'going':g(r,'馬場状態','going'),'starters':'','trifecta_payout':'','source_url':''}
    if n==0: raise SystemExit('No runner rows normalized; source schema did not match')
    rf=['race_id','race_date','track','race_no','race_name','surface','distance','going','starters','trifecta_payout','source_url']
    with races_out.open('w',encoding='utf-8',newline='') as o:
        wr=csv.DictWriter(o,fieldnames=rf); wr.writeheader()
        for row in races.values(): wr.writerow(row)
    print(f'normalized {len(races)} races -> {races_out}')
    print(f'normalized {n} runner rows -> {out}')
if __name__=='__main__': main()
