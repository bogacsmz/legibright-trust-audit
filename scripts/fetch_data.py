#!/usr/bin/env python3
"""Fetch the PUBLIC datasets the demos use, so a fresh clone is fully reproducible.

Everything here is public and redistributable-by-download:
  * football-data.co.uk closing odds (incl. Pinnacle) → data/matches.db  (the Auditor demo)
  * UCI Bike Sharing + Kaggle Titanic                 → data/generality.db + CSVs

The author's private betting snapshot DBs (İddaa/TJK live feeds) are NOT required for any
demo — the runnable demo runs entirely on this public football data.

    python scripts/fetch_data.py

Idempotent: re-running rebuilds the DBs from cache.
"""
from __future__ import annotations

import io
import sqlite3
import sys
import urllib.request
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0"}

FD_BASE = "https://www.football-data.co.uk/mmz4281"
FD_LEAGUES = ["E0", "SP1", "D1", "I1", "F1", "T1"]          # big-5 + Turkey
FD_SEASONS = ["2021", "2122", "2223", "2324", "2425", "2526"]

TITANIC = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
BIKE_ZIP = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"

# football-data columns we keep (map to our `matches` schema)
FD_COLS = {
    "Date": "date", "Div": "league", "HomeTeam": "home", "AwayTeam": "away", "FTR": "result",
    "PSCH": "psc_h", "PSCD": "psc_d", "PSCA": "psc_a",
    "B365CH": "b365c_h", "B365CD": "b365c_d", "B365CA": "b365c_a",
    "MaxCH": "maxc_h", "MaxCD": "maxc_d", "MaxCA": "maxc_a",
    "AvgCH": "avgc_h", "AvgCD": "avgc_d", "AvgCA": "avgc_a",
}


def _get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def build_matches() -> int:
    import csv

    rows = []
    for season in FD_SEASONS:
        for lg in FD_LEAGUES:
            try:
                raw = _get(f"{FD_BASE}/{season}/{lg}.csv").decode("latin-1")
            except Exception:
                continue
            rdr = csv.DictReader(io.StringIO(raw))
            for r in rdr:
                if not (r.get("Date") and r.get("FTR") in ("H", "D", "A")):
                    continue
                rows.append({dst: _num(r.get(src)) for src, dst in FD_COLS.items()})
    db = DATA / "matches.db"
    con = sqlite3.connect(db)
    con.execute("DROP TABLE IF EXISTS matches")
    con.execute("""CREATE TABLE matches (date TEXT, league TEXT, home TEXT, away TEXT, result TEXT,
        psc_h REAL, psc_d REAL, psc_a REAL, b365c_h REAL, b365c_d REAL, b365c_a REAL,
        maxc_h REAL, maxc_d REAL, maxc_a REAL, avgc_h REAL, avgc_d REAL, avgc_a REAL)""")
    con.executemany(
        "INSERT INTO matches VALUES (:date,:league,:home,:away,:result,:psc_h,:psc_d,:psc_a,"
        ":b365c_h,:b365c_d,:b365c_a,:maxc_h,:maxc_d,:maxc_a,:avgc_h,:avgc_d,:avgc_a)", rows)
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    con.close()
    return n


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v if v else None


def build_generality() -> tuple[int, int]:
    import pandas as pd

    (DATA / "titanic.csv").write_bytes(_get(TITANIC))
    z = zipfile.ZipFile(io.BytesIO(_get(BIKE_ZIP)))
    (DATA / "bike_day.csv").write_bytes(z.read("day.csv"))
    con = sqlite3.connect(DATA / "generality.db")
    t = pd.read_csv(DATA / "titanic.csv"); t.to_sql("titanic", con, if_exists="replace", index=False)
    b = pd.read_csv(DATA / "bike_day.csv"); b.to_sql("bikeshare", con, if_exists="replace", index=False)
    con.close()
    return len(t), len(b)


def main() -> int:
    DATA.mkdir(exist_ok=True)
    print("Fetching public football odds (football-data.co.uk)...")
    n = build_matches()
    print(f"  data/matches.db: {n} matches")
    print("Fetching Titanic + UCI Bike Sharing...")
    nt, nb = build_generality()
    print(f"  data/generality.db: titanic={nt}, bikeshare={nb}")
    print("\nDone. Next:")
    print("  python scripts/verify_all.py     # 15 adversarial checks, no DataHub needed")
    print("  bash scripts/quickstart_up.sh && bash demo/run_demo.sh   # full graph demo (needs DataHub)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
