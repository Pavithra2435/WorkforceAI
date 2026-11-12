"""
================================================================================
WorkforceAI - User Authentication & Role Setup
Initializes the users table and seeds administrative and employee accounts.
================================================================================
"""

import os
import sys
import sqlite3
import hashlib

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.kpi_engine import get_employee_name, DB_PATH

def hash_password(password: str) -> str:
    """Computes SHA-256 hash."""
    return hashlib.sha256((password or "").strip().encode("utf-8")).hexdigest()

def setup_users_database():
    """Creates the users table and seeds HR Admin and Employee accounts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('hr_admin', 'employee')),
        employee_id TEXT,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
    );
    """)

    cursor.execute("DELETE FROM users;")

    # Standard password hash for 123456
    pw_123456 = hash_password("123456")

    # 1. Dedicated HR Admin account: admin@workforce.ai and sarah.jenkins@workforce.ai
    cursor.execute("""
    INSERT INTO users (email, password_hash, role, employee_id, full_name)
    VALUES (?, ?, ?, ?, ?)
    """, ("admin@workforce.ai", pw_123456, "hr_admin", None, "Sarah Jenkins (Chief HR Officer)"))

    cursor.execute("""
    INSERT INTO users (email, password_hash, role, employee_id, full_name)
    VALUES (?, ?, ?, ?, ?)
    """, ("sarah.jenkins@workforce.ai", pw_123456, "hr_admin", None, "Sarah Jenkins (Chief HR Officer)"))

    # 2. Named Employee legacy alias: ajay@workforce.ai / 123456
    cursor.execute("""
    INSERT OR REPLACE INTO users (email, password_hash, role, employee_id, full_name)
    VALUES (?, ?, ?, ?, ?)
    """, ("ajay@workforce.ai", pw_123456, "employee", "E0087", "Ajay Sharma"))

    # 3. Seed all employee accounts from data/employee_roster.csv
    import csv
    roster_path = os.path.join(PROJECT_ROOT, "data", "employee_roster.csv")
    emp_users = []
    if os.path.exists(roster_path):
        with open(roster_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                emp_id = row.get("employee_id", "").strip()
                email = row.get("email", "").strip()
                name = row.get("full_name", "").strip()
                role = row.get("role", "employee").strip()
                if email and role == "employee":
                    emp_users.append((email, pw_123456, "employee", emp_id, name))

    cursor.executemany("""
    INSERT OR REPLACE INTO users (email, password_hash, role, employee_id, full_name)
    VALUES (?, ?, ?, ?, ?)
    """, emp_users)

    conn.commit()

    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role;")
    stats = cursor.fetchall()
    print("[+] Users table re-seeded successfully:")
    for role, count in stats:
        print(f"    - {role}: {count} accounts")

    conn.close()

if __name__ == "__main__":
    setup_users_database()
