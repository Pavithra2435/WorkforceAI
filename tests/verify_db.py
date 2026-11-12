import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "hr_workforce.db"))
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

query = """
    SELECT 
        COUNT(*) AS total_headcount,
        SUM(CASE WHEN employment_status = 'Active' THEN 1 ELSE 0 END) AS active_headcount,
        SUM(CASE WHEN employment_status = 'Exited' THEN 1 ELSE 0 END) AS exited_count,
        ROUND((SUM(CASE WHEN employment_status = 'Exited' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 2) AS attrition_rate_pct,
        ROUND(AVG(CASE WHEN employment_status = 'Active' THEN (julianday('now') - julianday(joining_date)) / 365.25 END), 2) AS avg_active_tenure_years
    FROM employee_master;
"""
cursor.execute(query)
row = cursor.fetchone()
print("Executive KPIs Query Result:")
for k in row.keys():
    print(f"  {k}: {row[k]}")

# Department breakdown query
dept_query = """
    SELECT 
        department,
        COUNT(*) AS total_headcount,
        SUM(CASE WHEN employment_status = 'Active' THEN 1 ELSE 0 END) AS active_count,
        SUM(CASE WHEN employment_status = 'Exited' THEN 1 ELSE 0 END) AS exited_count,
        ROUND((SUM(CASE WHEN employment_status = 'Exited' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 1) AS attrition_rate,
        ROUND(AVG(CASE WHEN employment_status = 'Active' THEN (julianday('now') - julianday(joining_date)) / 365.25 END), 1) AS avg_tenure_years
    FROM employee_master
    GROUP BY department
    ORDER BY total_headcount DESC;
"""
cursor.execute(dept_query)
dept_rows = cursor.fetchall()
print(f"\nDepartment Breakdown ({len(dept_rows)} departments):")
for r in dept_rows:
    print(f"  {r['department']:15} Total: {r['total_headcount']:3} | Active: {r['active_count']:3} | Exited: {r['exited_count']:2} | Attrition: {r['attrition_rate']:4.1f}% | Tenure: {r['avg_tenure_years']}y")

# Attendance test
att_query = """
    SELECT 
        COUNT(*) AS total_records,
        ROUND((SUM(CASE WHEN attendance_status = 'Present' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 1) AS present_pct,
        ROUND((SUM(CASE WHEN attendance_status = 'Remote' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 1) AS remote_pct,
        ROUND((SUM(CASE WHEN attendance_status = 'Absent' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 1) AS absenteeism_pct,
        ROUND((SUM(CASE WHEN attendance_status = 'On Leave' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100.0, 1) AS on_leave_pct
    FROM attendance;
"""
cursor.execute(att_query)
att_row = cursor.fetchone()
print(f"\nAttendance Summary ({att_row['total_records']:,} rows):")
for k in att_row.keys():
    print(f"  {k}: {att_row[k]}")

conn.close()
print("\n[SUCCESS] All SQL queries executed perfectly on SQLite!")

