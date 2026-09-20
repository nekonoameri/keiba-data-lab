PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS races (
  race_id TEXT PRIMARY KEY,
  race_date TEXT NOT NULL,
  track TEXT NOT NULL,
  race_no INTEGER NOT NULL,
  race_name TEXT,
  surface TEXT,
  distance INTEGER,
  going TEXT,
  starters INTEGER,
  trifecta_payout INTEGER,
  source_url TEXT
);
CREATE TABLE IF NOT EXISTS runners (
  race_id TEXT NOT NULL,
  finish INTEGER,
  frame_no INTEGER,
  horse_no INTEGER,
  horse_name TEXT,
  jockey TEXT,
  popularity INTEGER,
  odds REAL,
  finish_time TEXT,
  last3f REAL,
  PRIMARY KEY(race_id, horse_no),
  FOREIGN KEY(race_id) REFERENCES races(race_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_races_course ON races(track,surface,distance,race_date);
CREATE INDEX IF NOT EXISTS idx_runners_jockey ON runners(jockey,race_id);
CREATE INDEX IF NOT EXISTS idx_runners_pop ON runners(popularity,finish);
