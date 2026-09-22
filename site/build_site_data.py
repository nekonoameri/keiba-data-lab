#!/usr/bin/env python3
import sqlite3,json
from pathlib import Path
root=Path(__file__).resolve().parent; con=sqlite3.connect(root/'keiba.db');con.row_factory=sqlite3.Row
# Public results must never expose future-dated rows. GitHub Actions may ingest malformed PDF dates, so cap all site aggregates at build time.
# Current jockey rankings use a rolling 12-month window so retired riders do not dominate current-facing pages.
from datetime import date,timedelta
TODAY=date.today().isoformat()
ACTIVE_SINCE=(date.today()-timedelta(days=56)).isoformat()
VALID="race_date IS NOT NULL AND race_date<=?"
MAX_TRIFECTA=58367060
wild=[dict(x) for x in con.execute('''SELECT r.race_id,r.race_date,r.track,r.race_no,r.race_name,r.surface,r.distance,r.trifecta_payout,
 (SELECT GROUP_CONCAT(popularity,' → ') FROM (SELECT popularity FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 ORDER BY finish)) popularity_top3
 FROM races r WHERE r.trifecta_payout BETWEEN 100 AND ? AND r.race_date<=? ORDER BY r.trifecta_payout DESC LIMIT 10''',(MAX_TRIFECTA,TODAY))]
jockey=[dict(x) for x in con.execute('''SELECT u.jockey AS jockey,COUNT(*) rides,SUM(u.finish=1) wins,SUM(u.finish=2) seconds,SUM(u.finish=3) thirds,ROUND(100.0*SUM(u.finish=1)/COUNT(*),1) win_rate,ROUND(100.0*SUM(u.finish<=2)/COUNT(*),1) top2_rate,ROUND(100.0*SUM(u.finish<=3)/COUNT(*),1) place_rate,ROUND(AVG(u.popularity),1) avg_popularity,ROUND(100.0*SUM(CASE WHEN u.popularity>=7 AND u.finish<=3 THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN u.popularity>=7 THEN 1 ELSE 0 END),0),1) longshot_place_rate,SUM(CASE WHEN u.popularity>=7 THEN 1 ELSE 0 END) longshot_rides,ROUND(AVG(CASE WHEN u.popularity IS NOT NULL THEN u.popularity-u.finish END),2) popularity_gain FROM runners u JOIN races r ON r.race_id=u.race_id WHERE u.jockey<>'' AND u.jockey NOT IN ('柴田 善臣','柴田善臣','藤岡 佑介','藤岡佑介','和田 竜二','和田竜二','橋木 太希','橋木太希','西村 太一','西村太一','石神 深一','石神深一','岡部 幸雄','岡部幸雄') AND r.race_date>=date(strftime('%Y',?)||'-01-01') AND r.race_date<=? AND EXISTS (SELECT 1 FROM runners ua JOIN races ra ON ra.race_id=ua.race_id WHERE ua.jockey=u.jockey AND ra.race_date BETWEEN ? AND ?) GROUP BY u.jockey HAVING COUNT(*)>=10 ORDER BY wins DESC,seconds DESC,thirds DESC LIMIT 200''',(TODAY,TODAY,ACTIVE_SINCE,TODAY))]
course=[dict(x) for x in con.execute('''SELECT r.track,r.surface,r.distance,COUNT(*) races,ROUND(AVG(r.trifecta_payout)) avg_trifecta,CASE WHEN SUM((SELECT COUNT(*) FROM runners u WHERE u.race_id=r.race_id AND u.popularity IS NOT NULL))>0 THEN ROUND(100.0*AVG(CASE WHEN EXISTS(SELECT 1 FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 AND u.popularity>=7) THEN 1 ELSE 0 END),1) ELSE NULL END longshot_place_pct FROM races r WHERE r.race_date<=? AND (r.distance IS NULL OR r.distance BETWEEN 800 AND 4000) GROUP BY r.track,r.surface,r.distance ORDER BY races DESC''',(TODAY,))]
conditions=[dict(x) for x in con.execute('''SELECT track,surface,distance,COUNT(*) races,ROUND(AVG(trifecta_payout)) avg_payout,ROUND(100.0*AVG(trifecta_payout>=100000),1) pct_100k FROM races WHERE trifecta_payout BETWEEN 100 AND ? AND race_date<=? AND (distance IS NULL OR distance BETWEEN 800 AND 4000) GROUP BY track,surface,distance HAVING COUNT(*)>=3 ORDER BY pct_100k DESC,avg_payout DESC LIMIT 20''',(MAX_TRIFECTA,TODAY))]
for x in wild:
    if not x.get('popularity_top3'): x['popularity_top3']=None
coverage=dict(con.execute("SELECT MIN(race_date),MAX(race_date),COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date<=?",(TODAY,)).fetchone())
# Rebuild coverage explicitly because sqlite Row -> dict keys are expression names.
mn,mx,rc=con.execute("SELECT MIN(race_date),MAX(race_date),COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date<=?",(TODAY,)).fetchone()
rn=con.execute("SELECT COUNT(*) FROM runners u JOIN races r ON r.race_id=u.race_id WHERE r.race_date<=?",(TODAY,)).fetchone()[0]
recent=[dict(x) for x in con.execute("""SELECT race_id,race_date,track,race_no,race_name,surface,distance,going,trifecta_payout,source_url FROM races WHERE race_date IS NOT NULL AND race_date<=? AND (distance IS NULL OR distance BETWEEN 800 AND 4000) ORDER BY race_date DESC,race_no DESC LIMIT 120""",(TODAY,))]
# Current-day data is intentionally separated from historical aggregates.
# current_jockeys is populated only from same-day race-card rows when such rows are present.
current_jockeys=[x['jockey'] for x in con.execute("""SELECT DISTINCT u.jockey AS jockey FROM runners u JOIN races r ON r.race_id=u.race_id WHERE r.race_date=? AND u.jockey<>'' ORDER BY u.jockey""",(TODAY,))]
out={'current_jockeys':current_jockeys,'meta':{'min_date':mn,'max_date':mx,'race_count':rc,'runner_count':rn},'recent_races':recent,'wild_races':wild,'jockey_rankings':jockey,'courses':course,'wild_conditions':conditions}
(root/'site-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'site-data.js').write_text('window.KEIBA_DATA='+json.dumps(out,ensure_ascii=False)+';',encoding='utf-8')
print('wrote site-data.json + site-data.js')

# rebuild-marker: corrected-current-jockeys-v2
