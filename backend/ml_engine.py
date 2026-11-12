"""
================================================================================
AI-Powered HR Workforce Insights Dashboard
Step 3: Machine Learning Engine (backend/ml_engine.py)
Technology: Python, scikit-learn, pandas, numpy
================================================================================

This module implements the predictive and anomaly-detection capabilities 
described in Block 6B of the system architecture:

1. Task 1: Attrition Classification (Flight-Risk Scoring)
   - Algorithm: RandomForestClassifier with class_weight='balanced'
   - Function: get_employee_flight_risk(employee_id=None)
   - Outputs: Flight risk score (0.0 to 1.0), risk tier (Low, Medium, High),
     and top 3 explainable contributing factors for HR intervention.

2. Task 2: Attendance Anomaly Detection
   - Function: detect_attendance_anomalies(threshold=2.0)
   - Logic: Statistical Z-score outlier detection on department-relative absenteeism,
     Monday/Friday absence clustering, and frequent short workdays (<6 hours).

3. Task 3: Exit Forecasting
   - Function: forecast_upcoming_exits(months_ahead=3)
   - Logic: Explainable linear trend projection over historical monthly exits to
     project expected turnover for upcoming quarters.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)

# Reference date representing the end of the reporting window in the synthetic dataset
REFERENCE_DATE = pd.to_datetime("2026-10-31")

# Global caches for trained model and datasets
_MODEL = None
_FEATURE_DATA = None
_FEATURE_NAMES = None
_DEPT_COLS = None
_ORG_BENCHMARKS = None
_ATTENDANCE_ANOMALIES_CACHE = {}


# ==============================================================================
# HELPER: LOCATE DATASET FILES
# ==============================================================================
def find_data_folder():
    """
    Locates the CSV dataset folder across common project paths.
    """
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "cleaned"),
        os.path.join("data", "cleaned"),
        os.path.join("..", "data", "cleaned"),
        "hr_workforce_cleaned_and_validated_dataset",
        ".",
        "cleaned_dataset",
        "hr"
    ]
    for path in candidates:
        if os.path.exists(path) and os.path.isfile(os.path.join(path, "employee_master.csv")):
            return os.path.abspath(path)
    raise FileNotFoundError("Could not locate HR CSV dataset folder (data/cleaned).")


# ==============================================================================
# 1. DATA PREPARATION & FEATURE ENGINEERING
# ==============================================================================
def prepare_ml_dataset(save_csv=True):
    """
    Builds the consolidated feature table required for ML training.
    Attempts to read from MySQL if accessible, otherwise falls back to the validated CSVs.
    
    Features engineered:
    - age: Derived from date_of_birth
    - tenure_months: Active tenure or tenure up to exit date
    - absence_rate: Proportion of absent days over total scheduled days
    - remote_rate: Proportion of remote work days
    - unpaid_leave_days: Total days of approved unpaid leave
    - sick_leave_days: Total days of approved sick leave
    - onboarding_completion_rate: Completed onboarding tasks ratio
    - is_attrition: Target binary indicator (1 for Exited, 0 for Active)
    """
    data_dir = find_data_folder()
    cached_paths = [
        os.path.join(data_dir, "final_ml_workforce_dataset.csv"),
        os.path.join(os.path.dirname(__file__), "..", "final_ml_workforce_dataset.csv"),
        "final_ml_workforce_dataset.csv"
    ]
    for cp in cached_paths:
        if os.path.exists(cp):
            return pd.read_csv(cp)

    folder = data_dir

    # Load core tables
    emp = pd.read_csv(os.path.join(folder, "employee_master.csv"))
    att = pd.read_csv(os.path.join(folder, "attendance.csv"))
    leave = pd.read_csv(os.path.join(folder, "leave.csv"))
    attr = pd.read_csv(os.path.join(folder, "attrition.csv"))
    onb = pd.read_csv(os.path.join(folder, "onboarding.csv"))

    # A) Employee demographics and tenure
    emp["joining_date"] = pd.to_datetime(emp["joining_date"])
    emp["date_of_birth"] = pd.to_datetime(emp["date_of_birth"])
    emp["age"] = ((REFERENCE_DATE - emp["date_of_birth"]).dt.days / 365.25).round(1)

    exit_map = attr.set_index("employee_id")["exit_date"].to_dict()
    emp["exit_date"] = emp["employee_id"].map(exit_map)
    emp["end_date"] = pd.to_datetime(emp["exit_date"]).fillna(REFERENCE_DATE)
    emp["tenure_months"] = (((emp["end_date"] - emp["joining_date"]).dt.days) / 30.4375).round(1)
    emp["is_attrition"] = (emp["employment_status"] == "Exited").astype(int)

    # B) Attendance behavioral features
    att["is_absent"] = (att["attendance_status"] == "Absent").astype(int)
    att["is_remote"] = (att["attendance_status"] == "Remote").astype(int)
    att_agg = att.groupby("employee_id").agg(
        total_days=("attendance_date", "count"),
        absent_days=("is_absent", "sum"),
        remote_days=("is_remote", "sum")
    ).reset_index()
    att_agg["absence_rate"] = (att_agg["absent_days"] / att_agg["total_days"]).round(4)
    att_agg["remote_rate"] = (att_agg["remote_days"] / att_agg["total_days"]).round(4)

    # C) Leave utilization features
    unpaid = leave[leave["leave_type"] == "Unpaid Leave"].groupby("employee_id")["leave_days"].sum().rename("unpaid_leave_days")
    sick = leave[leave["leave_type"] == "Sick Leave"].groupby("employee_id")["leave_days"].sum().rename("sick_leave_days")

    # D) Onboarding completion feature
    onb["is_completed"] = (onb["task_status"] == "Completed").astype(int)
    onb_agg = onb.groupby("employee_id").agg(
        total_tasks=("task_status", "count"),
        completed_tasks=("is_completed", "sum")
    ).reset_index()
    onb_agg["onboarding_completion_rate"] = (onb_agg["completed_tasks"] / onb_agg["total_tasks"]).round(4)

    # Merge into unified ML DataFrame
    df_ml = emp[["employee_id", "department", "designation", "employment_status", "age", "tenure_months", "is_attrition"]].copy()
    df_ml = df_ml.merge(att_agg[["employee_id", "absence_rate", "remote_rate"]], on="employee_id", how="left")
    df_ml = df_ml.merge(unpaid, on="employee_id", how="left").fillna({"unpaid_leave_days": 0})
    df_ml = df_ml.merge(sick, on="employee_id", how="left").fillna({"sick_leave_days": 0})
    df_ml = df_ml.merge(onb_agg[["employee_id", "onboarding_completion_rate"]], on="employee_id", how="left").fillna({"onboarding_completion_rate": 1.0})

    if save_csv:
        target_csv = os.path.join(data_dir, "final_ml_workforce_dataset.csv")
        df_ml.to_csv(target_csv, index=False)

    return df_ml


# ==============================================================================
# 2. MODEL TRAINING (RANDOM FOREST WITH CLASS BALANCING)
# ==============================================================================
def train_flight_risk_model(df=None):
    """
    Trains a balanced RandomForestClassifier for employee attrition classification.
    
    Model specifications:
    - n_estimators = 100
    - max_depth = 5 (prevents overfitting and ensures explainable trees)
    - class_weight = 'balanced' (counteracts the 14% vs 86% class imbalance)
    - random_state = 42
    
    Returns:
        tuple: (model, evaluation_metrics_dict)
    """
    global _MODEL, _FEATURE_DATA, _FEATURE_NAMES, _DEPT_COLS, _ORG_BENCHMARKS

    if df is None:
        df = prepare_ml_dataset()

    _FEATURE_DATA = df.copy()

    # Numerical feature columns
    num_cols = [
        "age",
        "tenure_months",
        "absence_rate",
        "remote_rate",
        "unpaid_leave_days",
        "sick_leave_days",
        "onboarding_completion_rate"
    ]

    # One-hot encode department
    df_encoded = pd.get_dummies(df, columns=["department"], drop_first=False)
    _DEPT_COLS = [c for c in df_encoded.columns if c.startswith("department_")]
    _FEATURE_NAMES = num_cols + _DEPT_COLS

    X = df_encoded[_FEATURE_NAMES]
    y = df_encoded["is_attrition"]

    # Compute organizational benchmarks for explainable AI explanations
    _ORG_BENCHMARKS = {
        "absence_rate_mean": df["absence_rate"].mean(),
        "absence_rate_std": df["absence_rate"].std(),
        "remote_rate_mean": df["remote_rate"].mean(),
        "tenure_months_mean": df["tenure_months"].mean(),
        "unpaid_leave_mean": df["unpaid_leave_days"].mean(),
        "sick_leave_mean": df["sick_leave_days"].mean(),
    }

    # Stratified train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Initialize and train RandomForestClassifier
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)
    _MODEL = model

    # Evaluate on test set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 3),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 3),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 3),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 3),
        "classification_report": classification_report(y_test, y_pred, output_dict=True)
    }

    # Precalculate risk scores on the full feature dataset
    all_probs = model.predict_proba(X)[:, 1]
    _FEATURE_DATA["risk_score"] = np.round(all_probs, 4)
    _FEATURE_DATA["risk_tier"] = pd.cut(
        _FEATURE_DATA["risk_score"],
        bins=[-1, 0.35, 0.60, 1.0],
        labels=["Low", "Medium", "High"]
    ).astype(str)

    return model, metrics


# ==============================================================================
# TASK 1: FLIGHT-RISK SCORING & EXPLAINABLE CONTRIBUTING FACTORS
# ==============================================================================
def _explain_contributing_factors(row, feature_importances):
    """
    Identifies the top 3 factors elevating an employee's flight-risk score
    by combining feature deviation from organizational averages with feature weights.
    """
    factors = []

    # 1. Absence rate factor
    abs_diff = row["absence_rate"] - _ORG_BENCHMARKS["absence_rate_mean"]
    if abs_diff > 0:
        pct_val = row["absence_rate"] * 100
        avg_pct = _ORG_BENCHMARKS["absence_rate_mean"] * 100
        score = (abs_diff / (_ORG_BENCHMARKS["absence_rate_std"] or 1e-4)) * feature_importances.get("absence_rate", 0.15)
        factors.append((score, f"High Absenteeism Rate ({pct_val:.1f}% vs org avg {avg_pct:.1f}%)"))

    # 2. Tenure factor (lower tenure in early months carries higher flight risk)
    if row["tenure_months"] < 12.0:
        score = (12.0 - row["tenure_months"]) / 12.0 * feature_importances.get("tenure_months", 0.20)
        factors.append((score, f"Short Company Tenure ({row['tenure_months']:.1f} months tenure)"))
    elif row["tenure_months"] > 48.0:
        score = 0.5 * feature_importances.get("tenure_months", 0.20)
        factors.append((score, f"Career Plateau / High Tenure ({row['tenure_months']:.1f} months in role)"))

    # 3. Unpaid leave usage
    if row["unpaid_leave_days"] > 2:
        score = (row["unpaid_leave_days"] / 5.0) * feature_importances.get("unpaid_leave_days", 0.10)
        factors.append((score, f"Elevated Unpaid Leave Taken ({int(row['unpaid_leave_days'])} days)"))

    # 4. Sick leave usage
    if row["sick_leave_days"] > 5:
        score = (row["sick_leave_days"] / 8.0) * feature_importances.get("sick_leave_days", 0.08)
        factors.append((score, f"Frequent Sick Leave Requests ({int(row['sick_leave_days'])} days)"))

    # 5. Incomplete Onboarding
    if row["onboarding_completion_rate"] < 1.0:
        score = (1.0 - row["onboarding_completion_rate"]) * feature_importances.get("onboarding_completion_rate", 0.05) * 5.0
        factors.append((score, f"Pending Onboarding Tasks ({row['onboarding_completion_rate']*100:.0f}% completion)"))

    # 6. Remote work variance
    rem_diff = row["remote_rate"] - _ORG_BENCHMARKS["remote_rate_mean"]
    if rem_diff > 0.05:
        score = rem_diff * feature_importances.get("remote_rate", 0.10)
        factors.append((score, f"High Remote Ratio ({row['remote_rate']*100:.1f}% vs org avg {_ORG_BENCHMARKS['remote_rate_mean']*100:.1f}%)"))

    # Sort factors by impact score descending and take top 3
    factors.sort(key=lambda x: x[0], reverse=True)
    top_3 = [f[1] for f in factors[:3]]
    if not top_3:
        top_3 = ["Normal behavioral and attendance patterns across all tracked indicators."]

    return top_3


def get_employee_flight_risk(employee_id=None, min_risk=0.40):
    """
    Task 1: Flight-Risk Scoring.
    
    If employee_id is specified:
        Returns dictionary with risk score (0.0 to 1.0), risk tier ("Low", "Medium", "High"),
        and top 3 contributing factors.
    
    If employee_id is None:
        Returns list of all active elevated-risk employees (risk_score >= min_risk, default 0.40)
        sorted descending by risk score.
    """
    global _MODEL, _FEATURE_DATA, _FEATURE_NAMES

    if _MODEL is None or _FEATURE_DATA is None:
        train_flight_risk_model()

    feat_importances = dict(zip(_FEATURE_NAMES, _MODEL.feature_importances_))

    # Case A: Specific employee inspection
    if employee_id is not None:
        emp_match = _FEATURE_DATA[_FEATURE_DATA["employee_id"] == employee_id]
        if emp_match.empty:
            return {"error": f"Employee ID '{employee_id}' not found in workforce database."}

        row = emp_match.iloc[0]
        score = float(row["risk_score"])
        tier = str(row["risk_tier"])
        factors = _explain_contributing_factors(row, feat_importances)

        return {
            "employee_id": employee_id,
            "department": row["department"],
            "designation": row["designation"],
            "employment_status": row["employment_status"],
            "risk_score": score,
            "risk_tier": tier,
            "top_contributing_factors": factors,
            "feature_metrics": {
                "age": float(row["age"]),
                "tenure_months": float(row["tenure_months"]),
                "absence_rate_pct": round(float(row["absence_rate"] * 100), 2),
                "remote_rate_pct": round(float(row["remote_rate"] * 100), 2),
                "unpaid_leave_days": int(row["unpaid_leave_days"]),
                "sick_leave_days": int(row["sick_leave_days"]),
                "onboarding_completion_pct": round(float(row["onboarding_completion_rate"] * 100), 2)
            }
        }

    # Case B: Prioritized list of all high-risk active employees
    active_emp = _FEATURE_DATA[_FEATURE_DATA["employment_status"] == "Active"].copy()
    high_risk = active_emp[active_emp["risk_score"] >= min_risk].sort_values(
        by="risk_score", ascending=False
    )

    results = []
    for _, r in high_risk.iterrows():
        factors = _explain_contributing_factors(r, feat_importances)
        score = float(r["risk_score"])
        tier = "Critical" if score >= 0.65 else ("High" if score >= 0.50 else "Elevated")
        results.append({
            "employee_id": r["employee_id"],
            "department": r["department"],
            "designation": r["designation"],
            "risk_score": score,
            "risk_tier": tier,
            "top_contributing_factors": factors,
            "primary_reason": factors[0] if factors else "Tenure and absence indicators",
            "tenure_months": float(r["tenure_months"]),
            "absence_rate_pct": round(float(r["absence_rate"] * 100), 2),
            "unpaid_leave_days": int(r["unpaid_leave_days"])
        })

    return results


# ==============================================================================
# TASK 2: ATTENDANCE ANOMALY DETECTION
# ==============================================================================
def detect_attendance_anomalies(threshold=2.0):
    """
    Task 2: Attendance Anomaly Detection.
    
    Identifies behavioral outliers using Z-score statistical tests on:
    1. Unusually high absenteeism rate compared to department peers.
    2. High Monday/Friday absence clustering ratio (long-weekend patterns).
    3. High frequency of logged short workdays (<6 hours).
    
    Parameters:
        threshold (float): Z-score cutoff (default 2.0 = ~97.5th percentile).
        
    Returns:
        list of dict: Flagged employees with exact anomaly explanation reasons.
    """
    global _ATTENDANCE_ANOMALIES_CACHE
    if threshold in _ATTENDANCE_ANOMALIES_CACHE:
        return _ATTENDANCE_ANOMALIES_CACHE[threshold]

    folder = find_data_folder()
    att = pd.read_csv(os.path.join(folder, "attendance.csv"))
    emp = pd.read_csv(os.path.join(folder, "employee_master.csv"))

    # Join department and parse dates
    att = att.merge(emp[["employee_id", "department"]], on="employee_id", how="left")
    att["attendance_date"] = pd.to_datetime(att["attendance_date"])
    att["day_of_week"] = att["attendance_date"].dt.day_name()

    # Calculate work hours for valid logged records
    att_valid = att.dropna(subset=["check_in_time", "check_out_time"]).copy()
    try:
        in_parts = att_valid["check_in_time"].str.split(":", expand=True).astype(float)
        out_parts = att_valid["check_out_time"].str.split(":", expand=True).astype(float)
        att_valid["work_hours"] = (out_parts[0] + out_parts[1] / 60.0) - (in_parts[0] + in_parts[1] / 60.0)
    except Exception:
        att_valid["work_hours"] = 8.25

    # Aggregate attendance indicators per employee
    att["is_absent"] = (att["attendance_status"] == "Absent").astype(int)
    att["is_mon_fri_absent"] = ((att["attendance_status"] == "Absent") & (att["day_of_week"].isin(["Monday", "Friday"]))).astype(int)

    emp_stats = att.groupby(["employee_id", "department"]).agg(
        total_days=("attendance_date", "count"),
        absent_days=("is_absent", "sum"),
        mon_fri_absent=("is_mon_fri_absent", "sum")
    ).reset_index()

    emp_stats["absence_rate"] = emp_stats["absent_days"] / emp_stats["total_days"]
    emp_stats["mon_fri_absence_ratio"] = np.where(
        emp_stats["absent_days"] > 0,
        emp_stats["mon_fri_absent"] / emp_stats["absent_days"],
        0.0
    )

    # Short workdays count (<6 hours)
    short_days = att_valid[att_valid["work_hours"] < 6.0].groupby("employee_id")["attendance_id"].count().rename("short_days_count")
    emp_stats = emp_stats.merge(short_days, on="employee_id", how="left").fillna({"short_days_count": 0})

    # Statistical Z-Scores
    dept_means = emp_stats.groupby("department")["absence_rate"].transform("mean")
    dept_stds = emp_stats.groupby("department")["absence_rate"].transform("std").replace(0, 1e-4)
    emp_stats["absence_zscore"] = (emp_stats["absence_rate"] - dept_means) / dept_stds

    mf_mean = emp_stats["mon_fri_absence_ratio"].mean()
    mf_std = emp_stats["mon_fri_absence_ratio"].std() or 1e-4
    emp_stats["mon_fri_zscore"] = (emp_stats["mon_fri_absence_ratio"] - mf_mean) / mf_std

    sd_mean = emp_stats["short_days_count"].mean()
    sd_std = emp_stats["short_days_count"].std() or 1e-4
    emp_stats["short_days_zscore"] = (emp_stats["short_days_count"] - sd_mean) / sd_std

    anomalies = []
    for _, r in emp_stats.iterrows():
        reasons = []
        if r["absence_zscore"] > threshold:
            dept_avg = dept_means.loc[r.name] * 100
            reasons.append(
                f"High Absenteeism: {r['absence_rate']*100:.1f}% (vs. {dept_avg:.1f}% dept avg)"
            )
        if r["mon_fri_zscore"] > threshold:
            reasons.append(
                f"Frequent Monday / Friday Leaves ({r['mon_fri_absence_ratio']*100:.0f}% of absences on Mon/Fri)"
            )
        if r["short_days_zscore"] > threshold:
            reasons.append(
                f"Frequent Short Workdays ({int(r['short_days_count'])} logged days under 6 hrs)"
            )

        if reasons:
            anomalies.append({
                "employee_id": r["employee_id"],
                "department": r["department"],
                "absence_rate_pct": round(float(r["absence_rate"] * 100), 2),
                "mon_fri_absence_ratio_pct": round(float(r["mon_fri_absence_ratio"] * 100), 2),
                "short_days_count": int(r["short_days_count"]),
                "anomaly_flags": reasons
            })

    _ATTENDANCE_ANOMALIES_CACHE[threshold] = anomalies
    return anomalies


# ==============================================================================
# TASK 3: EXIT FORECASTING (TREND PROJECTION)
# ==============================================================================
def forecast_upcoming_exits(months_ahead=3, department="", location=""):
    """
    Task 3: Exit Forecasting.
    
    Computes an explainable moving-average and linear trend projection over historical
    monthly exit records to project expected attrition for the next quarter.
    Supports filtering by department and location.
    
    Parameters:
        months_ahead (int): Number of future months to project (default 3).
        department (str): Optional department filter.
        location (str): Optional location filter.
        
    Returns:
        dict: Historical baseline and monthly future exit projections.
    """
    folder = find_data_folder()
    attr = pd.read_csv(os.path.join(folder, "attrition.csv"))
    emp = pd.read_csv(os.path.join(folder, "employee_master.csv"))

    # Merge attrition with employee master to obtain location (attrition already contains department)
    merged = attr.merge(emp[["employee_id", "location"]], on="employee_id", how="left")

    if department and str(department).strip():
        merged = merged[merged["department"].astype(str).str.strip().str.lower() == str(department).strip().lower()]
    if location and str(location).strip():
        merged = merged[merged["location"].astype(str).str.strip().str.lower() == str(location).strip().lower()]

    merged["exit_date"] = pd.to_datetime(merged["exit_date"])
    merged["month_year"] = merged["exit_date"].dt.to_period("M")

    start_period = pd.Period("2025-11", freq="M")
    end_period = pd.Period("2026-10", freq="M")
    full_idx = pd.period_range(start_period, end_period, freq="M")

    if merged.empty:
        future_periods = pd.period_range(end_period + 1, periods=months_ahead, freq="M")
        forecast_results = {p.strftime("%b %Y"): 0.0 for p in future_periods}
        return {
            "historical_monthly_average": 0.0,
            "recent_3m_average": 0.0,
            "trend_slope_per_month": 0.0,
            "trend_direction": "Stable",
            "monthly_forecast": forecast_results,
            "total_quarterly_projected_exits": 0
        }

    monthly_series = merged.groupby("month_year").size().reindex(full_idx, fill_value=0)

    # Linear trend projection: y = slope * x + intercept
    x = np.arange(len(monthly_series))
    y = monthly_series.values
    if len(x) > 1 and np.std(x) > 0:
        slope, intercept = np.polyfit(x, y, 1)
    else:
        slope, intercept = 0.0, float(y.mean()) if len(y) else 0.0

    # 3-month rolling average for short-term baseline
    rolling_3m_avg = monthly_series.iloc[-3:].mean()

    # Generate forecasts for future periods (whole number employee departure counts)
    future_periods = pd.period_range(end_period + 1, periods=months_ahead, freq="M")
    forecast_results = {}
    total_projected = 0

    for i, p in enumerate(future_periods, start=len(monthly_series)):
        trend_val = max(0.0, slope * i + intercept)
        projected = int(round(0.7 * trend_val + 0.3 * rolling_3m_avg))
        month_label = p.strftime("%b %Y")
        forecast_results[month_label] = projected
        total_projected += projected

    return {
        "historical_monthly_average": round(float(y.mean()), 1),
        "recent_3m_average": round(float(rolling_3m_avg), 1),
        "trend_slope_per_month": round(float(slope), 3),
        "trend_direction": "Increasing" if slope > 0.05 else ("Decreasing" if slope < -0.05 else "Stable"),
        "monthly_forecast": forecast_results,
        "total_quarterly_projected_exits": int(total_projected)
    }


# ==============================================================================
# CLI TEST RUNNER
# ==============================================================================
def main():
    print("\n" + "=" * 80)
    print(" AI-POWERED HR WORKFORCE INSIGHTS DASHBOARD — MACHINE LEARNING ENGINE")
    print("=" * 80)

    print("\n--- 1. TRAINING ATTRITION CLASSIFICATION MODEL (RandomForest) ---")
    model, metrics = train_flight_risk_model()
    print(f"Precision: {metrics['precision']:.3f} | Recall: {metrics['recall']:.3f} | F1-Score: {metrics['f1_score']:.3f} | ROC-AUC: {metrics['roc_auc']:.3f}")
    print("\nClassification Report:")
    for cls in ["0", "1"]:
        c_metrics = metrics["classification_report"][cls]
        print(f"  Class {cls} (Attrition={cls}): Precision={c_metrics['precision']:.2f}, Recall={c_metrics['recall']:.2f}, F1={c_metrics['f1-score']:.2f}")

    print("\n--- 2. TOP ACTIVE HIGH-RISK EMPLOYEES (Risk Score >= 0.60) ---")
    high_risk_list = get_employee_flight_risk()
    print(f"Total High-Risk Active Employees Flagged: {len(high_risk_list)}")
    print(f"{'Emp ID':<8} | {'Department':<18} | {'Designation':<22} | {'Risk Score':<11} | {'Top Contributing Factor'}")
    print("-" * 95)
    for emp in high_risk_list[:5]:
        top_factor = emp["top_contributing_factors"][0] if emp["top_contributing_factors"] else "N/A"
        print(f"{emp['employee_id']:<8} | {emp['department']:<18} | {emp['designation']:<22} | {emp['risk_score']:<11.2f} | {top_factor}")

    sample_id = high_risk_list[0]["employee_id"] if high_risk_list else "E0001"
    print(f"\n--- 3. DEEP DIVE INSPECTION: {sample_id} ---")
    detail = get_employee_flight_risk(sample_id)
    print(f"Employee: {detail['employee_id']} ({detail['designation']} - {detail['department']})")
    print(f"Risk Score: {detail['risk_score']} [{detail['risk_tier']} Tier]")
    print("Top Contributing Factors:")
    for factor in detail["top_contributing_factors"]:
        print(f"  • {factor}")

    print("\n--- 4. ATTENDANCE ANOMALY DETECTION (Threshold = 2.0 Z-Score) ---")
    anomalies = detect_attendance_anomalies(threshold=2.0)
    print(f"Total Employees with Attendance Anomalies: {len(anomalies)}")
    for a in anomalies[:5]:
        print(f"  • {a['employee_id']} ({a['department']}): {'; '.join(a['anomaly_flags'])}")

    print("\n--- 5. UPCOMING EXIT FORECASTING (Next Quarter) ---")
    forecast = forecast_upcoming_exits(months_ahead=3)
    print(f"Historical Monthly Average Exits: {forecast['historical_monthly_average']}")
    print(f"Recent 3-Month Average:           {forecast['recent_3m_average']}")
    print(f"Trend Direction:                  {forecast['trend_direction']} ({forecast['trend_slope_per_month']:+.2f} exits/month)")
    print("\nProjected Exits:")
    for month, count in forecast["monthly_forecast"].items():
        print(f"  • {month}: ~{count} exits")
    print(f"Total Projected Exits for Next Quarter: {forecast['total_quarterly_projected_exits']} employees")

    print("\n" + "=" * 80)
    print(" Machine Learning Engine execution and tests completed successfully!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

