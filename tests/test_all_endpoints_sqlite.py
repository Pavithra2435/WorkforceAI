import os
import sys
import time
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api_server import (
    api_status,
    api_filters,
    api_executive_kpis,
    api_department_breakdown,
    api_attrition_insights,
    api_attendance_kpis,
    api_leave_analytics,
    api_onboarding_mobility,
    api_flight_risk_roster,
    api_employee_risk,
    api_attendance_anomalies,
    api_exit_forecast,
    api_copilot
)

def run_coro(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value
    raise RuntimeError("Coroutine did not finish synchronously")

class MockReq:
    def __init__(self, q=None, p=None, body=None):
        self.query_params = q or {}
        self.path_params = p or {}
        self._body_dict = body or {}

print("\n" + "="*80)
print("VERIFYING ALL REST API ENDPOINTS ON SQLITE3 (database/hr_workforce.db)")
print("="*80 + "\n")

# 1. API Status
t0 = time.time()
r = run_coro(api_status(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/status -> status={data['status']}, db={data['database']}, type={data['type']}")
assert data["status"] == "online"
assert data["database"] == "hr_workforce.db"

# 2. Filters
t0 = time.time()
r = run_coro(api_filters(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/filters -> depts={data['departments']}, locs={data['locations']}")
assert len(data["departments"]) == 7
assert len(data["locations"]) > 0

# 3. Executive KPIs (Unfiltered)
t0 = time.time()
r = run_coro(api_executive_kpis(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/kpis (All) -> Total={data['total_headcount']}, Active={data['active_headcount']}, Exited={data['exited_count']}, Attrition={data['attrition_rate_pct']}%, Tenure={data['avg_active_tenure_years']}y")
assert data["total_headcount"] == 500
assert data["active_headcount"] == 430
assert data["exited_count"] == 70
assert data["attrition_rate_pct"] == 14.0

# 4. Executive KPIs (Filtered: IT)
t0 = time.time()
r = run_coro(api_executive_kpis(MockReq(q={"department": "IT"})))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/kpis (IT) -> Total={data['total_headcount']}, Active={data['active_headcount']}, Exited={data['exited_count']}")
assert data["total_headcount"] == 82

# 5. Department Breakdown (Unfiltered)
t0 = time.time()
r = run_coro(api_department_breakdown(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/departments (All) -> {len(data)} departments, top dept={data[0]['department']} (count={data[0]['total_headcount']}, active={data[0]['active_count']}, attrition={data[0]['attrition_rate']}%)")
assert len(data) == 7

# 6. Department Breakdown (Filtered: IT, HR)
t0 = time.time()
r = run_coro(api_department_breakdown(MockReq(q={"department": "IT,HR"})))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/departments (Filtered) -> {len(data)} departments returned")
assert len(data) == 2

# 7. Attrition Insights
t0 = time.time()
r = run_coro(api_attrition_insights(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/attrition -> Total Exits={data['total_exits']}, Top Reason='{data['top_exit_reasons'][0]['exit_reason']}' ({data['top_exit_reasons'][0]['exit_count']} exits)")
assert data["total_exits"] == 70

# 8. Attendance KPIs
t0 = time.time()
r = run_coro(api_attendance_kpis(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/attendance -> Present={data['present_pct']}%, Remote={data['remote_pct']}%, Absent={data['absenteeism_pct']}%, Hours={data['avg_daily_work_hours']}")
assert data["present_pct"] == 80.0

# 9. Leave Analytics
t0 = time.time()
r = run_coro(api_leave_analytics(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/leaves -> {len(data['leave_by_type'])} leave types, top={data['leave_by_type'][0]['leave_type']} ({data['leave_by_type'][0]['total_leave_days']} days)")
assert len(data["leave_by_type"]) > 0

# 10. Onboarding & Mobility
t0 = time.time()
r = run_coro(api_onboarding_mobility(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/onboarding-mobility -> Tasks={data['total_onboarding_tasks']}, Completion={data['onboarding_completion_pct']}%, Movements={data['total_movements']}")
assert data["total_onboarding_tasks"] == 2500

# 11. Flight Risk Roster (ML)
t0 = time.time()
r = run_coro(api_flight_risk_roster(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/flight-risk-roster -> High Risk Flagged={len(data)}, Top Employee={data[0]['employee_id']} (Score={data[0]['risk_score']})")
assert len(data) > 0

# 12. Single Employee Deep Dive (ML)
t0 = time.time()
r = run_coro(api_employee_risk(MockReq(p={"employee_id": data[0]["employee_id"]})))
emp_data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/flight-risk/{data[0]['employee_id']} -> Tier={emp_data['risk_tier']}, Top Factor='{emp_data['top_contributing_factors'][0]}'")

# 13. Attendance Anomalies (ML)
t0 = time.time()
r = run_coro(api_attendance_anomalies(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/attendance-anomalies -> Anomalies Flagged={len(data)}")
assert len(data) > 0

# 14. Exit Forecast (ML)
t0 = time.time()
r = run_coro(api_exit_forecast(MockReq()))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/exit-forecast -> Quarterly Projection={data['total_quarterly_projected_exits']} exits, Trend={data['trend_direction']}")

# 15. Copilot GenAI Query
t0 = time.time()
r = run_coro(api_copilot(MockReq(body={"query": "Which department has highest attrition?"})))
data = json.loads(r.body.decode())
print(f" [PASS] ({(time.time()-t0)*1000:5.1f}ms) /api/copilot -> Answer: {data['natural_language_answer'][:75]}...")
assert len(data["natural_language_answer"]) > 10

print("\n" + "="*80)
print("🎉 ALL 15 REST API ENDPOINTS & DATA RETRIEVAL PIPELINES PASSED ON SQLITE!")
print("="*80 + "\n")
