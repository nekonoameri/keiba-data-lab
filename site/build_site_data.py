#!/usr/bin/env python3
import sqlite3,json
from pathlib import Path
root=Path(__file__).resolve().parent; con=sqlite3.connect(root/'keiba.db');con.row_factory=sqlite3.Row
wild=[dict(x) for x in con.execute('''SELECT r.race_id,r.race_date,r.track,r.race_no,r.race_name,r.surface,r.distance,r.trifecta_payout,
 (SELECT GROUP_CONCAT(popularity,' → ') FROM (SELECT popularity FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 ORDER BY finish)) popularity_top3
 FROM races r WHERE r.trifecta_payout IS NOT NULL ORDER BY r.trifecta_payout DESC LIMIT 100''')]
jockey=[dict(x) for x in con.execute('''SELECT jockey,COUNT(*) rides,SUM(finish=1) wins,ROUND(100.0*SUM(finish=1)/COUNT(*),1) win_rate,ROUND(100.0*SUM(finish<=3)/COUNT(*),1) place_rate,ROUND(AVG(popularity),1) avg_popularity FROM runners WHERE jockey<>'' GROUP BY jockey HAVING COUNT(*)>=3 ORDER BY place_rate DESC,rides DESC LIMIT 100''')]
course=[dict(x) for x in con.execute('''SELECT r.track,r.surface,r.distance,COUNT(*) races,ROUND(AVG(r.trifecta_payout)) avg_trifecta,CASE WHEN SUM((SELECT COUNT(*) FROM runners u WHERE u.race_id=r.race_id AND u.popularity IS NOT NULL))>0 THEN ROUND(100.0*AVG(CASE WHEN EXISTS(SELECT 1 FROM runners u WHERE u.race_id=r.race_id AND u.finish<=3 AND u.popularity>=7) THEN 1 ELSE 0 END),1) ELSE NULL END longshot_place_pct FROM races r GROUP BY r.track,r.surface,r.distance ORDER BY races DESC''')]
conditions=[dict(x) for x in con.execute('''SELECT track,surface,distance,COUNT(*) races,ROUND(AVG(trifecta_payout)) avg_payout,ROUND(100.0*AVG(trifecta_payout>=100000),1) pct_100k FROM races WHERE trifecta_payout IS NOT NULL GROUP BY track,surface,distance HAVING COUNT(*)>=3 ORDER BY pct_100k DESC,avg_payout DESC LIMIT 20''')]
for x in wild:
    if not x.get('popularity_top3'): x['popularity_top3']=None
out={'wild_races':wild,'jockey_rankings':jockey,'courses':course,'wild_conditions':conditions}
(root/'site-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'site-data.js').write_text('window.KEIBA_DATA='+json.dumps(out,ensure_ascii=False)+';',encoding='utf-8')
print('wrote site-data.json + site-data.js')
