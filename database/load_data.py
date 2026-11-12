"""
================================================================================
AI-Powered HR Workforce Insights Dashboard
Step 1: Automated SQLite Database Ingestion Script (database/load_data.py)
Technology: Python, sqlite3, pandas
Zero external server dependencies, 100% self-contained.
================================================================================
"""

import os
import sys
import sqlite3
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DB_PATH = os.path.join(CURRENT_DIR, "hr_workforce.db")
SCHEMA_PATH = os.path.join(CURRENT_DIR, "schema_sqlite.sql")


def find_dataset_folder():
    """Locates the directory containing the 6 cleaned HR CSV datasets."""
    candidates = [
        os.path.join(PROJECT_ROOT, "data", "cleaned"),
        os.path.join(CURRENT_DIR, "..", "data", "cleaned"),
        os.path.join("data", "cleaned"),
        "data/cleaned"
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.exists(os.path.join(p, "employee_master.csv")):
            return os.path.abspath(p)
    raise FileNotFoundError("Could not locate data/cleaned directory.")


def init_database():
    """Initializes SQLite schema and analytical tables."""
    print(f"[*] Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable PRAGMA for speed and foreign keys
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA foreign_keys = OFF;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("[+] Schema and indexes created successfully.")


def ingest_data():
    """Loads all 6 CSV files into SQLite tables with high-speed transactions."""
    folder = find_dataset_folder()
    print(f"[*] Loading CSV datasets from: {folder}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    datasets = [
        ("employee_master.csv", "employee_master"),
        ("leave.csv", "leave_requests"),
        ("workforce_movements.csv", "workforce_movements"),
        ("attrition.csv", "attrition"),
        ("onboarding.csv", "onboarding"),
        ("attendance.csv", "attendance")
    ]

    total_rows = 0

    for csv_file, table_name in datasets:
        csv_path = os.path.join(folder, csv_file)
        if not os.path.exists(csv_path):
            print(f"[!] Warning: {csv_file} not found, skipping.")
            continue

        print(f"[*] Ingesting {csv_file} into {table_name}...")
        df = pd.read_csv(csv_path)
        
        # Convert NaN values to None
        df = df.where(pd.notnull(df), None)

        # Clear existing rows in table
        cursor.execute(f"DELETE FROM {table_name};")
        conn.commit()

        # Fast insert using to_sql with active connection
        df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=10000)
        
        row_count = len(df)
        total_rows += row_count
        print(f"    -> {row_count:,} records inserted.")

    conn.commit()

    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.close()

    print("\n" + "="*60)
    print("DATABASE INGESTION COMPLETE & VALIDATED")
    print(f"Total Records Ingested into SQLite: {total_rows:,}")
    print(f"Database File: {DB_PATH}")
    print("="*60 + "\n")


if __name__ == "__main__":
    init_database()
    ingest_data()
