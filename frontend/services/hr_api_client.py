"""
================================================================================
Client-Side Service & API Layer for WorkforceAI Dashboard
Decouples UI Presentation Views from Raw Database and ML Engines.
Provides Caching, Type Sanitization, and Error Fault-Tolerance.
================================================================================
"""

import os
import sys
import json
from decimal import Decimal
import pandas as pd
import numpy as np
import streamlit as st

# Ensure repository root is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.kpi_engine import (
    get_db_connection,
    get_executive_kpis,
    get_department_breakdown,
    get_attrition_insights,
    get_attendance_kpis,
    get_leave_analytics,
    get_onboarding_and_mobility_kpis,
    DB_HOST,
    DB_PORT,
    DB_NAME
)
from backend.ml_engine import (
    get_employee_flight_risk,
    detect_attendance_anomalies,
    forecast_upcoming_exits
)
from genai.hr_agent import ask_hr_copilot


def clean_for_json(obj):
    """
    Recursively converts MySQL Decimals, NumPy types, and sets into JSON-serializable types.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [clean_for_json(item) for item in obj]
    return obj


@st.cache_data(ttl=600, show_spinner=False)
def fetch_filter_options():
    """
    Retrieves unique list of active departments and locations for sidebar filtering.
    """
    conn = get_db_connection()
    if not conn:
        return ["HR", "Engineering", "Sales", "Marketing", "Finance"], ["New York", "San Francisco", "London"]
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT department FROM employee_master WHERE department IS NOT NULL ORDER BY department;")
        depts = [row["department"] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT location FROM employee_master WHERE location IS NOT NULL ORDER BY location;")
        locs = [row["location"] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return depts, locs
    except Exception as e:
        print(f"[fetch_filter_options] Warning: {e}")
        return ["HR", "Engineering", "Sales", "Marketing", "Finance"], ["New York", "San Francisco", "London"]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_executive_kpis(dept_list=None, loc_list=None):
    """
    Fetches high-level executive workforce KPIs filtered by departments and locations.
    """
    conn = get_db_connection()
    if not conn:
        return {
            "total_headcount": 500,
            "active_headcount": 430,
            "exited_count": 70,
            "attrition_rate_pct": 14.0,
            "avg_active_tenure_years": 3.2
        }
    try:
        where_clauses = []
        params = []
        if dept_list:
            placeholders = ", ".join(["%s"] * len(dept_list))
            where_clauses.append(f"department IN ({placeholders})")
            params.extend(dept_list)
        if loc_list:
            placeholders = ", ".join(["%s"] * len(loc_list))
            where_clauses.append(f"location IN ({placeholders})")
            params.extend(loc_list)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        cursor = conn.cursor(dictionary=True)
        query = f"""
            SELECT 
                COUNT(*) AS total_headcount,
                SUM(CASE WHEN employment_status = 'Active' THEN 1 ELSE 0 END) AS active_headcount,
                SUM(CASE WHEN employment_status = 'Exited' THEN 1 ELSE 0 END) AS exited_count,
                ROUND((SUM(CASE WHEN employment_status = 'Exited' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS attrition_rate_pct,
                ROUND(AVG(CASE WHEN employment_status = 'Active' THEN DATEDIFF(CURDATE(), joining_date) / 365.25 END), 2) AS avg_active_tenure_years
            FROM employee_master
            {where_sql};
        """
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        total = result["total_headcount"] or 0
        active = result["active_headcount"] or 0
        exited = result["exited_count"] or 0
        att_rate = float(result["attrition_rate_pct"]) if result["attrition_rate_pct"] is not None else 0.0
        tenure = float(result["avg_active_tenure_years"]) if result["avg_active_tenure_years"] is not None else 0.0

        return {
            "total_headcount": int(total),
            "active_headcount": int(active),
            "exited_count": int(exited),
            "attrition_rate_pct": att_rate,
            "avg_active_tenure_years": tenure
        }
    except Exception as e:
        print(f"[fetch_executive_kpis] Fallback: {e}")
        return get_executive_kpis()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_department_breakdown():
    return get_department_breakdown()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_attrition_insights():
    return get_attrition_insights()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_attendance_kpis():
    return get_attendance_kpis()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_leave_analytics():
    return get_leave_analytics()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_onboarding_mobility():
    return get_onboarding_and_mobility_kpis()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_flight_risk_roster():
    """
    Retrieves all high-risk employees (risk_score >= 0.60).
    """
    res = get_employee_flight_risk(None)
    if isinstance(res, list):
        return res
    elif isinstance(res, dict) and "error" not in res:
        return res.get("high_risk_employees", [])
    return []


def fetch_single_employee_risk(emp_id: str):
    """
    Evaluates individual employee flight risk.
    """
    return get_employee_flight_risk(emp_id)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_attendance_anomalies(threshold: float = 2.0):
    return detect_attendance_anomalies(threshold)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_exit_forecast(months: int = 3):
    return forecast_upcoming_exits(months)


def call_ai_copilot(query_text: str):
    """
    Direct interface to the Generative AI Copilot.
    """
    return ask_hr_copilot(query_text)
