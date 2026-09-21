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
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('--out',default='runners.csv'); a=ap.parse_args()
    src=Path(a.input); out=Path(__file__).resolve().parent/a.out
    fields=['race_id','date','track','race_no','surface','distance','going','frame','horse_number','horse_name','jockey','popularity','odds','finish_position','finish_time','last_3f']
    n=0
    with src.open(encoding='utf-8-sig',newline='') as f, out.open('w',encoding='utf-8',newline='') as o:
        rd=csv.DictReader(f); wr=csv.DictWriter(o,fieldnames=fields); wr.writeheader()
        for r in rd:
            rid=g(r,'レースID','race_id','Race ID')
            course=g(r,'コース','course','Course')
            surf='芝' if '芝' in course else ('ダート' if 'ダ' in course else '')
            dist=g(r,'距離','距離（m）','distance','Distance')
            if not dist:
                m=re.search(r'(\d{3,4})',course); dist=m.group(1) if m else ''
            row={
              'race_id':rid,'date':g(r,'レース日付','日付','date','Race Day'),
              'track':g(r,'競馬場名','開催場所','track','Racecourse Name'),
              'race_no':g(r,'レース番号','何レース目','race_no'),
              'surface':surf,'distance':dist,'going':g(r,'馬場状態','going'),
              'frame':g(r,'枠番','frame'),'horse_number':g(r,'馬番','horse_number'),
              'horse_name':g(r,'馬名','horse_name'),'jockey':g(r,'騎手名','騎手','jockey'),
              'popularity':g(r,'人気','popularity'),'odds':g(r,'オッズ（単勝）','単勝','odds'),
              'finish_position':g(r,'着順','finish_position'),'finish_time':g(r,'タイム','finish_time'),
              'last_3f':g(r,'上り','上がり','last_3f')}
            if rid and row['horse_number']:
                wr.writerow(row); n+=1
    if n==0: raise SystemExit('No runner rows normalized; source schema did not match')
    print(f'normalized {n} runner rows -> {out}')
if __name__=='__main__': main()
