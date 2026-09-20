#!/usr/bin/env python3
import csv,sqlite3,argparse
from pathlib import Path
root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--races',default='races.csv');ap.add_argument('--runners',default='runners.csv');a=ap.parse_args()
con=sqlite3.connect(root/'keiba.db'); con.executescript((root/'schema.sql').read_text())
def val(x,t=str):
    if x in ('',None): return None
    try:return t(x)
    except:return None
with open(root/a.races,encoding='utf-8-sig') as f:
    for x in csv.DictReader(f): con.execute('INSERT OR REPLACE INTO races VALUES (?,?,?,?,?,?,?,?,?,?,?)',(x['race_id'],x['race_date'],x['track'],val(x['race_no'],int),x['race_name'],x['surface'],val(x['distance'],int),x['going'],val(x['starters'],int),val(x['trifecta_payout'],int),x['source_url']))
with open(root/a.runners,encoding='utf-8-sig') as f:
    for x in csv.DictReader(f): con.execute('INSERT OR REPLACE INTO runners VALUES (?,?,?,?,?,?,?,?,?,?)',(x['race_id'],val(x['finish'],int),val(x['frame_no'],int),val(x['horse_no'],int),x['horse_name'],x['jockey'],val(x['popularity'],int),val(x['odds'],float),x['finish_time'],val(x['last3f'],float)))
con.commit();print('DB',con.execute('select count(*) from races').fetchone()[0],'races /',con.execute('select count(*) from runners').fetchone()[0],'runners')
