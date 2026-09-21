#!/usr/bin/env python3
"""Import structured race/result CSV exported by an external collector into KEIBA DATA LAB.
This keeps collection replaceable: map source columns here, then use the existing SQLite pipeline.
"""
import argparse,csv
from pathlib import Path

ALIASES={
 'race_id':['race_id','レースID'],'date':['date','日付'],'track':['track','開催場所','場所'],
 'race_no':['race_no','R','何レース目'],'surface':['surface','コース'],'distance':['distance','距離'],
 'going':['going','馬場状態'],'finish_position':['finish_position','着順'],'frame':['frame','枠番'],
 'horse_number':['horse_number','馬番'],'horse_name':['horse_name','馬名'],'jockey':['jockey','騎手名','騎手'],
 'popularity':['popularity','人気'],'odds':['odds','オッズ（単勝）','単勝'],'last_3f':['last_3f','上り'],
 'finish_time':['finish_time','タイム']
}
def pick(row,key,default=''):
    for k in ALIASES[key]:
        if k in row and row[k] not in (None,''): return str(row[k]).strip()
    return default
def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--out',default='data/external_runners.csv');a=ap.parse_args()
    rows=list(csv.DictReader(open(a.input,encoding='utf-8-sig')))
    fields=['race_id','date','track','race_no','surface','distance','going','finish_position','frame','horse_number','horse_name','jockey','popularity','odds','finish_time','last_3f']
    out=Path(__file__).resolve().parent/a.out;out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:pick(r,k) for k in fields})
    print(f'normalized {len(rows)} runner rows -> {out}')
if __name__=='__main__':main()
