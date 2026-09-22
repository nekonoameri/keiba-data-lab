#!/usr/bin/env python3
import sqlite3,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parent; con=sqlite3.connect(ROOT/'keiba.db')
checks=[]
TODAY=date.today().isoformat()
def q(label,sql):
    n=con.execute(sql).fetchone()[0]; checks.append((label,n)); return n
q('future-dated races', f"SELECT COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date>'{TODAY}'")
q('races with impossible date format', "SELECT COUNT(*) FROM races WHERE race_date IS NOT NULL AND race_date NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'")
q('races with invalid race_no', 'SELECT COUNT(*) FROM races WHERE race_no NOT BETWEEN 1 AND 12')
q('races with invalid distance', 'SELECT COUNT(*) FROM races WHERE distance IS NOT NULL AND distance NOT BETWEEN 800 AND 5000')
q('runners with invalid horse_no', 'SELECT COUNT(*) FROM runners WHERE horse_no NOT BETWEEN 1 AND 18')
q('runners with invalid popularity', 'SELECT COUNT(*) FROM runners WHERE popularity IS NOT NULL AND popularity NOT BETWEEN 1 AND 18')
q('duplicate date/track/race_no', 'SELECT COUNT(*) FROM (SELECT race_date,track,race_no,COUNT(*) c FROM races GROUP BY 1,2,3 HAVING c>1)')
q('orphan runners', 'SELECT COUNT(*) FROM runners u LEFT JOIN races r ON r.race_id=u.race_id WHERE r.race_id IS NULL')
for label,n in checks: print(('OK  ' if n==0 else 'FAIL'),label,n)
if any(n for _,n in checks): sys.exit(2)
print('DATA VALIDATION PASSED')
