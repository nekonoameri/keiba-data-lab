#!/usr/bin/env python3
import sqlite3,json
from pathlib import Path
root=Path(__file__).resolve().parent; con=sqlite3.connect(root/'keiba.db');con.row_factory=sqlite3.Row
# Public results must never expose future-dated rows. GitHub Actions may ingest malformed PDF dates, so cap all site aggregates at build time.
TODAY="2026-09-22"
VALID="race_date IS NOT NULL AND race_date<=?"
wild=[dict(x) for x in con.execute('''SELECT r.race_id,r.race_date,r.track,r.race_no,r.race_name,r.surface,r.distance,r.trifecta_payout,
 (SELECT GROUP_CONCAT(popularity,' → ') FROM (SELECT popularity FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 ORDER BY finish)) popularity_top3
 FROM races r WHERE r.trifecta_payout IS NOT NULL AND r.race_date<=? ORDER BY r.trifecta_payout DESC LIMIT 100''',(TODAY,))]
jockey=[dict(x) for x in con.execute('''SELECT jockey,COUNT(*) rides,SUM(finish=1) wins,SUM(finish=2) seconds,SUM(finish=3) thirds,ROUND(100.0*SUM(finish=1)/COUNT(*),1) win_rate,ROUND(100.0*SUM(finish<=2)/COUNT(*),1) top2_rate,ROUND(100.0*SUM(finish<=3)/COUNT(*),1) place_rate,ROUND(AVG(popularity),1) avg_popularity,ROUND(100.0*AVG(CASE WHEN popularity>=7 AND finish<=3 THEN 1 ELSE 0 END),1) longshot_place_rate,ROUND(AVG(CASE WHEN popularity IS NOT NULL THEN popularity-finish END),2) popularity_gain FROM runners u JOIN races r ON r.race_id=u.race_id WHERE u.jockey<>'' AND r.race_date<=? GROUP BY u.jockey HAVING COUNT(*)>=30 ORDER BY place_rate DESC,rides DESC LIMIT 200''',(TODAY,))]
course=[dict(x) for x in con.execute('''SELECT r.track,r.surface,r.distance,COUNT(*) races,ROUND(AVG(r.trifecta_payout)) avg_trifecta,CASE WHEN SUM((SELECT COUNT(*) FROM runners u WHERE u.race_id=r.race_id AND u.popularity IS NOT NULL))>0 THEN ROUND(100.0*AVG(CASE WHEN EXISTS(SELECT 1 FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 AND u.popularity>=7) THEN 1 ELSE 0 END),1) ELSE NULL END longshot_place_pct FROM races r WHERE r.race_date<=? AND (r.distance IS NULL OR r.distance BETWEEN 800 AND 4000) GROUP BY r.track,r.surface,r.distance ORDER BY races DESC''',(TODAY,))]
conditions=[dict(x) for x in con.execute('''SELECT track,surface,distance,COUNT(*) races,ROUND(AVG(trifecta_payout)) avg_payout,ROUND(100.0*AVG(trifecta_payout>=100000),1) pct_100k FROM races WHERE trifecta_payout IS NOT NULL AND race_date<=? AND (distance IS NULL OR distance BETWEEN 800 AND 4000) GROUP BY track,surface,distance HAVING COUNT(*)>=3 ORDER BY pct_100k DESC,avg_payout DESC LIMIT 20''',(TODAY,))]
for x in wild:
    if not x.get('popularity_top3'): x['popularity_top3']=None
coverage=dict(con.execute("SELECT MIN(race_date),MAX(race_date),COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date<=?",(TODAY,)).fetchone())
# Rebuild coverage explicitly because sqlite Row -> dict keys are expression names.
mn,mx,rc=con.execute("SELECT MIN(race_date),MAX(race_date),COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date<=?",(TODAY,)).fetchone()
rn=con.execute("SELECT COUNT(*) FROM runners u JOIN races r ON r.race_id=u.race_id WHERE r.race_date<=?",(TODAY,)).fetchone()[0]
recent=[dict(x) for x in con.execute("""SELECT race_id,race_date,track,race_no,race_name,surface,distance,going,trifecta_payout,source_url FROM races WHERE race_date IS NOT NULL AND race_date<=? AND (distance IS NULL OR distance BETWEEN 800 AND 4000) ORDER BY race_date DESC,race_no DESC LIMIT 120""",(TODAY,))]
out={'meta':{'min_date':mn,'max_date':mx,'race_count':rc,'runner_count':rn},'recent_races':recent,'wild_races':wild,'jockey_rankings':jockey,'courses':course,'wild_conditions':conditions}
(root/'site-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'site-data.js').write_text('window.KEIBA_DATA='+json.dumps(out,ensure_ascii=False)+';',encoding='utf-8')
print('wrote site-data.json + site-data.js')
