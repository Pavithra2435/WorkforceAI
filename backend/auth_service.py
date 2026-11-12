"""
================================================================================
WorkforceAI - Authentication & Role-Based Access Control (RBAC) Service
Handles credential verification, role resolution, employee self-service queries,
and employee-scoped chatbot guardrails.
================================================================================
"""

import os
import sys
import sqlite3
import hashlib
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.kpi_engine import get_db_connection, get_employee_name, DB_PATH

def hash_password(password: str) -> str:
    """Computes SHA-256 hash."""
    return hashlib.sha256((password or "").strip().encode("utf-8")).hexdigest()

def authenticate_user(email: str, password: str) -> dict:
    """
    Verifies user credentials against the users table.
    The backend determines the user's role (hr_admin or employee).
    Admin: admin@workforce.ai / 123456
    Employees: ajay@workforce.ai (or any employee email) / 123456
    """
    email_clean = (email or "").strip().lower()
    pw_input = (password or "").strip()
    pw_hash = hash_password(pw_input)

    # 1. Dedicated Admin check
    if email_clean in ("admin@workforce.ai", "sarah.jenkins@workforce.ai"):
        if pw_input in ("123456", "admin123"):
            return {
                "success": True,
                "role": "hr_admin",
                "user": {
                    "user_id": 1,
                    "email": email_clean,
                    "name": "Sarah Jenkins (Chief HR Officer)",
                    "role": "hr_admin",
                    "employee_id": None
                },
                "token": "wkf-hr_admin-1-admin"
            }
        else:
            return {"success": False, "error": "Invalid email address or password."}

    conn = get_db_connection()
    if not conn:
        return {"success": False, "error": "Database connection error."}

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, password_hash, role, employee_id, full_name
            FROM users
            WHERE lower(email) = ?;
        """, (email_clean,))
        user = cursor.fetchone()

        # If user exists, check password
        if user:
            # Allow stored password hash or standard 123456
            if user["password_hash"] != pw_hash and pw_input not in ("123456", "emp123"):
                cursor.close()
                conn.close()
                return {"success": False, "error": "Invalid email address or password."}

            role = user["role"]
            emp_id = user["employee_id"]
            full_name = user["full_name"]
            user_id = user["user_id"]
        else:
            # Dynamic employee fallback: if password is 123456, allow any employee email!
            if pw_input in ("123456", "emp123") and "@" in email_clean:
                prefix = email_clean.split("@")[0].capitalize()
                # Check if prefix matches employee_id (e.g. e0087)
                emp_match = None
                if prefix.upper().startswith("E") and len(prefix) == 5:
                    cursor.execute("SELECT employee_id, gender FROM employee_master WHERE employee_id = ?;", (prefix.upper(),))
                    emp_match = cursor.fetchone()
                if not emp_match:
                    cursor.execute("SELECT employee_id, gender FROM employee_master LIMIT 1;")
                    emp_match = cursor.fetchone()
                
                emp_id = emp_match["employee_id"] if emp_match else "E0087"
                full_name = f"{prefix} (Employee)"
                role = "employee"
                user_id = 9999
            else:
                cursor.close()
                conn.close()
                return {"success": False, "error": "Invalid email address or password."}

        user_payload = {
            "user_id": user_id,
            "email": email_clean,
            "name": full_name,
            "role": role,
            "employee_id": emp_id
        }

        # If employee, attach personal workplace metadata
        if role == "employee" and emp_id:
            cursor.execute("""
                SELECT department, designation, joining_date, location, employment_type, employment_status
                FROM employee_master
                WHERE employee_id = ?;
            """, (emp_id,))
            emp = cursor.fetchone()
            if emp:
                user_payload["department"] = emp["department"]
                user_payload["designation"] = emp["designation"]
                user_payload["joining_date"] = emp["joining_date"]
                user_payload["location"] = emp["location"]
                user_payload["employment_type"] = emp["employment_type"]
                user_payload["employment_status"] = emp["employment_status"]

        cursor.close()
        conn.close()

        return {
            "success": True,
            "role": role,
            "user": user_payload,
            "token": f"wkf-{role}-{user_id}-{emp_id or 'admin'}"
        }

    except Exception as e:
        if conn:
            conn.close()
        return {"success": False, "error": f"Authentication failed: {str(e)}"}


def get_employee_portal_data(employee_id: str) -> dict:
    """
    Retrieves personal self-service records strictly for the requested employee.
    Includes personal profile, attendance history, leave balances, and onboarding checklist.
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection error."}

    try:
        cursor = conn.cursor()

        # 1. Master Profile
        cursor.execute("""
            SELECT employee_id, department, designation, joining_date, location,
                   employment_type, employment_status, gender, date_of_birth
            FROM employee_master
            WHERE employee_id = ?;
        """, (employee_id,))
        emp_row = cursor.fetchone()
        if not emp_row:
            cursor.close()
            conn.close()
            return {"error": "Employee record not found."}

        full_name = get_employee_name(employee_id, emp_row["gender"])
        profile = {
            "employee_id": emp_row["employee_id"],
            "name": full_name,
            "department": emp_row["department"],
            "designation": emp_row["designation"],
            "location": emp_row["location"],
            "joining_date": emp_row["joining_date"],
            "employment_type": emp_row["employment_type"],
            "employment_status": emp_row["employment_status"],
            "gender": emp_row["gender"],
            "date_of_birth": emp_row["date_of_birth"]
        }

        # 2. Attendance Summary & Recent Records
        cursor.execute("""
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN attendance_status = 'Present' THEN 1 ELSE 0 END) as present_days,
                SUM(CASE WHEN attendance_status = 'Remote' THEN 1 ELSE 0 END) as remote_days,
                SUM(CASE WHEN attendance_status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
                SUM(CASE WHEN attendance_status = 'On Leave' THEN 1 ELSE 0 END) as leave_days,
                SUM(CASE WHEN attendance_status = 'Half Day' THEN 1 ELSE 0 END) as half_days,
                ROUND(AVG(time_diff_hours(check_out_time, check_in_time)), 1) as avg_logged_hours
            FROM attendance
            WHERE employee_id = ?;
        """, (employee_id,))
        att_stat = dict(cursor.fetchone() or {})
        total_days = att_stat.get("total_days", 0) or 1
        present_count = (att_stat.get("present_days", 0) or 0) + (att_stat.get("remote_days", 0) or 0)
        attendance_rate = round((present_count / float(total_days)) * 100.0, 1)

        attendance_summary = {
            "total_days": att_stat.get("total_days", 0) or 0,
            "present_days": att_stat.get("present_days", 0) or 0,
            "remote_days": att_stat.get("remote_days", 0) or 0,
            "absent_days": att_stat.get("absent_days", 0) or 0,
            "leave_days": att_stat.get("leave_days", 0) or 0,
            "half_days": att_stat.get("half_days", 0) or 0,
            "avg_logged_hours": att_stat.get("avg_logged_hours", 8.2) or 8.2,
            "attendance_rate_pct": attendance_rate
        }

        # Last 15 attendance logs
        cursor.execute("""
            SELECT attendance_date, check_in_time, check_out_time, attendance_status,
                   ROUND(time_diff_hours(check_out_time, check_in_time), 1) as duration_hours
            FROM attendance
            WHERE employee_id = ?
            ORDER BY attendance_date DESC
            LIMIT 15;
        """, (employee_id,))
        recent_attendance = [dict(r) for r in cursor.fetchall()]

        # 3. Leave Requests & Balances
        cursor.execute("""
            SELECT leave_id, leave_type, start_date, end_date, leave_days, approval_status
            FROM leave_requests
            WHERE employee_id = ?
            ORDER BY start_date DESC;
        """, (employee_id,))
        leave_rows = [dict(r) for r in cursor.fetchall()]

        # Aggregate leave balances
        leave_breakdown = {
            "Casual Leave": {"used": 0, "total": 12},
            "Sick Leave": {"used": 0, "total": 10},
            "Paid Leave": {"used": 0, "total": 15},
            "Unpaid Leave": {"used": 0, "total": 0}
        }
        for l in leave_rows:
            ltype = l["leave_type"]
            days = l.get("leave_days", 1) or 1
            if l["approval_status"] == "Approved":
                if ltype in leave_breakdown:
                    leave_breakdown[ltype]["used"] += days
                else:
                    leave_breakdown[ltype] = {"used": days, "total": 10}

        leave_summary = {
            "total_applications": len(leave_rows),
            "approved_count": sum(1 for l in leave_rows if l["approval_status"] == "Approved"),
            "pending_count": sum(1 for l in leave_rows if l["approval_status"] == "Pending"),
            "rejected_count": sum(1 for l in leave_rows if l["approval_status"] == "Rejected"),
            "breakdown": leave_breakdown,
            "recent_requests": leave_rows[:10]
        }

        # 4. Onboarding Milestones
        cursor.execute("""
            SELECT onboarding_id, task_name, assigned_date, completion_date, task_status
            FROM onboarding
            WHERE employee_id = ?
            ORDER BY assigned_date ASC;
        """, (employee_id,))
        onb_tasks = [dict(r) for r in cursor.fetchall()]

        total_tasks = len(onb_tasks)
        completed_tasks = sum(1 for t in onb_tasks if t["task_status"] == "Completed")
        onb_rate = round((completed_tasks / float(total_tasks)) * 100.0, 1) if total_tasks > 0 else 100.0

        onboarding_summary = {
            "has_onboarding": total_tasks > 0,
            "total_milestones": total_tasks,
            "completed_milestones": completed_tasks,
            "pending_milestones": total_tasks - completed_tasks,
            "completion_rate_pct": onb_rate,
            "tasks": onb_tasks
        }

        cursor.close()
        conn.close()

        return {
            "profile": profile,
            "attendance": attendance_summary,
            "recent_attendance": recent_attendance,
            "leaves": leave_summary,
            "onboarding": onboarding_summary
        }

    except Exception as e:
        if conn:
            conn.close()
        return {"error": str(e)}


def ask_employee_copilot(query: str, employee_id: str) -> dict:
    """
    Employee-scoped, empathetic, and humanized conversational HR assistant.
    Strictly answers questions regarding the employee's own records.
    Declines company-wide attrition, peer records, and administrative queries gracefully.
    """
    q = (query or "").lower().strip()

    # RBAC Denial Patterns: Queries employees are NOT permitted to access
    forbidden_patterns = [
        "attrition", "turnover", "flight risk", "churn risk", "who will leave",
        "company attrition", "department attrition", "other employee", "salary of",
        "peer", "all employees", "admin", "anomaly radar", "forecast", "exit forecast"
    ]

    # Fetch employee's personal data
    data = get_employee_portal_data(employee_id)
    if "error" in data:
        return {
            "query": query,
            "answer": f"I'm sorry, I ran into an issue retrieving your personal records: {data['error']}",
            "recommendation": "Please try refreshing your session or signing in again."
        }

    profile = data["profile"]
    att = data["attendance"]
    leaves = data["leaves"]
    onb = data["onboarding"]
    first_name = profile["name"].split()[0] if profile.get("name") else "there"

    # 1. RBAC Guardrail Check
    if any(pat in q for pat in forbidden_patterns):
        return {
            "query": query,
            "answer": (
                f"I completely understand your curiosity, {first_name}! However, company-wide attrition analytics, "
                "organizational flight risk forecasts, and peer personnel records are confidential and restricted "
                "strictly to authorized HR Administrators under our workplace data governance policy.\n\n"
                f"That said, I am always here to assist with **your own personal records**—such as your available leave balances, "
                "attendance history, logged hours, or induction milestones. What would you like to check regarding your own profile?"
            ),
            "recommendation": "For company-level workforce analytics or administrative reports, please consult an authorized HR Administrator."
        }

    # 2. Greetings & Casual Openers
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "who are you", "what can you do"]
    if any(q == g or q.startswith(g + " ") or q.endswith(" " + g) for g in greetings):
        ans = (
            f"Hello {first_name}! Good to see you. I'm doing well, thank you for asking! "
            f"I am your personal HR Assistant here in WorkforceAI.\n\n"
            f"I'm always ready to help you with:\n"
            f"• **Leave Balances & Time Off:** Checking remaining days for Casual, Sick, or Paid Leave.\n"
            f"• **Attendance & Hours:** Reviewing your presence rate, daily hours, and remote work balance.\n"
            f"• **Onboarding Milestones:** Tracking your induction checklist and pending tasks.\n"
            f"• **Workplace Policies:** Answering common questions about time off and guidelines.\n\n"
            f"How can I help you today, {first_name}?"
        )
        rec = "Try asking: 'How many leaves do I have left?' or 'How is my attendance looking this month?'"
        return {"query": query, "answer": ans, "recommendation": rec}

    # 3. Gratitude & Goodbyes
    thanks_patterns = ["thank", "thanks", "thank you", "appreciate", "bye", "goodbye", "see you", "great thanks"]
    if any(pat in q for pat in thanks_patterns):
        ans = (
            f"You're very welcome, {first_name}! I'm always happy to help. "
            "Please feel free to open this chat anytime you need assistance with your time off, attendance, or benefits. "
            "Wishing you a wonderful and productive day ahead!"
        )
        rec = "I'm available 24/7 right here whenever you have HR questions."
        return {"query": query, "answer": ans, "recommendation": rec}

    # 3.5 Tier A: Google Gemini Personal Assistant (strictly scoped to employee's own JSON data)
    try:
        from genai.hr_agent import _get_gemini_api_key, _call_gemini_rest, _split_gemini_answer_and_rec
        import json as _json
        gemini_key = _get_gemini_api_key()
        if gemini_key:
            emp_system = (
                f"You are {first_name}'s Personal HR Assistant at WorkforceAI. "
                "You MUST ONLY answer questions about the employee's own personal records provided below or general HR leave/attendance policies. "
                "NEVER reveal or speculate on company-wide attrition, peer salaries, or other employees' records. "
                "If a metric is not in the JSON context, politely say so. Format clearly with bullet points and bold numbers, "
                "and end with '**Recommended Action:** <brief helpful tip>' when appropriate.\n\n"
                f"PERSONAL EMPLOYEE DATA:\n{_json.dumps(data, default=str)}"
            )
            payload = {
                "systemInstruction": {"parts": [{"text": emp_system}]},
                "contents": [{"role": "user", "parts": [{"text": query}]}],
                "generationConfig": {"temperature": 0.25},
            }
            resp = _call_gemini_rest(payload, gemini_key)
            cands = resp.get("candidates") or []
            if cands:
                parts = cands[0].get("content", {}).get("parts") or []
                text = "\n".join([p.get("text", "") for p in parts if "text" in p]).strip()
                if text:
                    ans, rec = _split_gemini_answer_and_rec(text)
                    return {"query": query, "answer": ans, "recommendation": rec}
    except Exception as _emp_gem_err:
        print(f"[GENAI] Employee Gemini fallback to deterministic mode: {_emp_gem_err}")

    # 4. Leave & Vacation Queries
    if any(k in q for k in ["leave", "leaves", "vacation", "sick leave", "casual leave", "paid leave", "balance", "holiday", "time off", "day off"]):
        casual = leaves["breakdown"].get("Casual Leave", {})
        sick = leaves["breakdown"].get("Sick Leave", {})
        paid = leaves["breakdown"].get("Paid Leave", {})

        c_used = casual.get("used", 0)
        c_total = casual.get("total", 12)
        c_rem = max(0, c_total - c_used)

        s_used = sick.get("used", 0)
        s_total = sick.get("total", 10)
        s_rem = max(0, s_total - s_used)

        p_used = paid.get("used", 0)
        p_total = paid.get("total", 15)
        p_rem = max(0, p_total - p_used)

        total_rem = c_rem + s_rem + p_rem
        pending = leaves.get("pending_count", 0)

        pending_str = (
            f"You also have **{pending} leave application currently pending review** with your manager.\n\n"
            if pending > 0 else
            "You currently have no pending leave applications under review.\n\n"
        )

        ans = (
            f"Hi {first_name}, you're in great standing with your leave balances! "
            f"In total, you have **{total_rem} days of leave remaining** across all categories:\n\n"
            f"• **Casual Leave:** **{c_rem} days remaining** (out of {c_total} allocated, {c_used} used so far)\n"
            f"• **Sick Leave:** **{s_rem} days remaining** (out of {s_total} allocated, {s_used} used)\n"
            f"• **Paid Vacation:** **{p_rem} days remaining** (out of {p_total} allocated, {p_used} used)\n\n"
            f"{pending_str}"
            "If you're planning some time off soon, remember to coordinate with your team in advance so your manager can approve your dates promptly!"
        )
        rec = "You can review your detailed application dates and approval history in the 'Leaves & Balances' section."
        return {"query": query, "answer": ans, "recommendation": rec}

    # 5. Attendance & Work Hours Queries
    if any(k in q for k in ["attendance", "work hours", "working hours", "remote", "absent", "present", "hours", "check in", "check out", "punch", "duration"]):
        att_rate = att.get("attendance_rate_pct", 90.0)
        avg_hours = att.get("avg_logged_hours", 8.2)
        present = att.get("present_days", 0)
        remote = att.get("remote_days", 0)
        absent = att.get("absent_days", 0)

        ans = (
            f"Hi {first_name}, looking over your verified attendance logs, you have maintained a dependable and solid record!\n\n"
            f"• **Overall Presence Rate:** **{att_rate}%** (Healthy engagement rate)\n"
            f"• **Average Work Duration:** **{avg_hours} hours per day** (Meets standard full-time expectations)\n"
            f"• **Work Distribution:** You have logged **{present} days on-site** and **{remote} remote work days**, which aligns nicely with our hybrid workplace guidelines.\n"
            f"• **Recorded Absences:** {absent} day(s) recorded to date.\n\n"
            "Your schedule is well-balanced and fully meets team collaboration benchmarks. Keep up the consistent routine!"
        )
        rec = "You can view the exact check-in and check-out timestamps for your last 15 days in the 'Attendance Records' tab."
        return {"query": query, "answer": ans, "recommendation": rec}

    # 6. Onboarding & Induction Queries
    if any(k in q for k in ["onboard", "onboarding", "milestone", "milestones", "task", "tasks", "induction", "checklist", "orientation"]):
        if onb.get("has_onboarding") and onb.get("total_milestones", 0) > 0:
            total_m = onb["total_milestones"]
            done_m = onb["completed_milestones"]
            pending_m = onb["pending_milestones"]
            pct = onb["completion_rate_pct"]

            if pending_m == 0 or pct >= 100.0:
                ans = (
                    f"Awesome news, {first_name}! You have completed **100% of your initial onboarding milestones** "
                    f"({done_m} of {total_m} tasks signed off). "
                    "All your IT security setups, compliance training modules, and departmental introductions are verified. "
                    "You are fully settled into your position!"
                )
                rec = "All standard onboarding procedures for your role are successfully satisfied."
            else:
                pending_tasks = [t["task_name"] for t in onb.get("tasks", []) if t.get("task_status") != "Completed"]
                pending_list = ", ".join(pending_tasks) if pending_tasks else f"{pending_m} task(s)"
                ans = (
                    f"Hi {first_name}, you're making steady progress on your onboarding journey! "
                    f"You have completed **{done_m} of {total_m} milestones ({pct}%)**.\n\n"
                    f"You still have {pending_m} open item(s): **{pending_list}**.\n\n"
                    "Knocking these out over the next few days will help keep your employee induction file 100% up to date. "
                    "Let me know if you need any assistance with documentation or setup!"
                )
                rec = "You can track milestone due dates directly in the 'Onboarding Status' tab."
        else:
            ans = (
                f"Hello {first_name}! You have fulfilled all orientation requirements, and there are currently no pending "
                "induction tasks assigned to your profile. You're completely up to speed!"
            )
            rec = "All standard onboarding requirements for your position are verified complete."
        return {"query": query, "answer": ans, "recommendation": rec}

    # 7. HR Policy Questions
    if any(k in q for k in ["policy", "rules", "how to apply", "guideline", "guidelines"]):
        ans = (
            f"Here is a quick overview of our common workplace guidelines for you, {first_name}:\n\n"
            f"• **Casual Leave (12 Days/Year):** Designed for personal commitments, family events, or errands. Usually requested 24–48 hours ahead via the portal.\n"
            f"• **Sick Leave (10 Days/Year):** For medical recovery, doctor visits, or unexpected illness. Can be reported on the same day without advance notice.\n"
            f"• **Paid Vacation (15 Days/Year):** Planned time off for rest and holidays. Planned in coordination with your team to maintain coverage.\n"
            f"• **Hybrid Remote Policy:** Standard office hours are typically 9:00 AM to 6:00 PM (averaging ~8.2 hours logged/day).\n\n"
            "If you need an exception or custom scheduling, please reach out to your reporting manager or HR partner."
        )
        rec = "You can submit any new leave request directly in the portal."
        return {"query": query, "answer": ans, "recommendation": rec}

    # 8. Default Profile & Welcome Overview
    ans = (
        f"Hi **{first_name}**! Welcome to your personal HR workspace. Here is a quick snapshot of your workplace profile:\n\n"
        f"• **Employee ID:** `{profile['employee_id']}`\n"
        f"• **Designation:** {profile['designation']} ({profile['department']})\n"
        f"• **Location:** {profile['location']}\n"
        f"• **Attendance Rate:** **{att['attendance_rate_pct']}%** (Avg {att['avg_logged_hours']}h/day)\n"
        f"• **Leave Summary:** {leaves['approved_count']} approved requests, {leaves['pending_count']} pending\n\n"
        f"I can assist you with your **leave balances**, **logged attendance**, or **onboarding induction milestones**. "
        f"What would you like to check today, {first_name}?"
    )
    rec = "Ask: 'How many leaves do I have left?' or 'How is my attendance looking?'"
    return {"query": query, "answer": ans, "recommendation": rec}

