"""
Backend package for AI-Powered HR Workforce Insights Dashboard.
Contains Centralized KPI Analytics (kpi_engine) and Machine Learning (ml_engine).
"""

from .kpi_engine import (
    get_executive_kpis,
    get_department_breakdown,
    get_attrition_insights,
    get_attendance_kpis,
    get_leave_analytics,
    get_onboarding_and_mobility_kpis,
)

from .ml_engine import (
    get_employee_flight_risk,
    detect_attendance_anomalies,
    forecast_upcoming_exits,
    train_flight_risk_model,
)

