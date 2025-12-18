#!/usr/bin/env python3
"""
Load processed CSV into a local SQLite DB (database/ab_test.db).
"""
import os
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_FP = ROOT / "data" / "processed" / "ab_cleaned.csv"
DB_DIR = ROOT / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_FP = DB_DIR / "ab_test.db"

if not PROCESSED_FP.exists():
    raise FileNotFoundError(f"Processed file not found: {PROCESSED_FP}. Run load_and_prepare.py first.")

df = pd.read_csv(PROCESSED_FP)

# connect and write
conn = sqlite3.connect(DB_FP)
df.to_sql("marketing_ab", conn, if_exists="replace", index=False)
conn.close()
print(f"Wrote table marketing_ab to {DB_FP}")
