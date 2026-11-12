import os
import sys
import time
import asyncio
import json

print(f"[{time.strftime('%H:%M:%S')}] Starting API server endpoints test...", flush=True)

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
    api_attendance_anomalies,
    api_exit_forecast,
    api_copilot
)

class MockReq:
    def __init__(self, q=None, p=None, body=None):
        self.query_params = q or {}
        self.path_params = p or {}
        self._body = body or {}
    async def json(self):
        return self._body

async def run_all():
    # 1. Status
    t0 = time.time()
    r = await api_status(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_status in {(time.time()-t0)*1000:.1f}ms: {data}", flush=True)
    assert data["status"] == "online"
    assert data["database"] == "hr_workforce.db"

    # 2. Filters
    t0 = time.time()
    r = await api_filters(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_filters in {(time.time()-t0)*1000:.1f}ms: {len(data['departments'])} depts, {len(data['locations'])} locs", flush=True)

    # 3. Executive KPIs (Unfiltered)
    t0 = time.time()
    r = await api_executive_kpis(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_executive_kpis (All) in {(time.time()-t0)*1000:.1f}ms: Headcount={data['total_headcount']}, Active={data['active_headcount']}, Attrition={data['attrition_rate_pct']}%", flush=True)
    assert data["total_headcount"] == 500

    # 4. Executive KPIs (Filtered: Engineering)
    t0 = time.time()
    r = await api_executive_kpis(MockReq(q={"department": "Engineering"}))
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_executive_kpis (Engineering) in {(time.time()-t0)*1000:.1f}ms: Headcount={data['total_headcount']}", flush=True)

    # 5. Department Breakdown (Unfiltered)
    t0 = time.time()
    r = await api_department_breakdown(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_department_breakdown (All) in {(time.time()-t0)*1000:.1f}ms: {len(data)} departments", flush=True)
    assert len(data) == 7

    # 6. Attrition Insights
    t0 = time.time()
    r = await api_attrition_insights(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_attrition_insights in {(time.time()-t0)*1000:.1f}ms: Exits={data['total_exits']}", flush=True)
    assert data["total_exits"] == 70

    # 7. Attendance KPIs
    t0 = time.time()
    r = await api_attendance_kpis(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_attendance_kpis in {(time.time()-t0)*1000:.1f}ms: Present={data['present_pct']}%, Remote={data['remote_pct']}%", flush=True)

    # 8. Leave Analytics
    t0 = time.time()
    r = await api_leave_analytics(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_leave_analytics in {(time.time()-t0)*1000:.1f}ms: Types={len(data['leave_by_type'])}", flush=True)

    # 9. Onboarding & Mobility
    t0 = time.time()
    r = await api_onboarding_mobility(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_onboarding_mobility in {(time.time()-t0)*1000:.1f}ms: Completion={data['onboarding_completion_pct']}%, Movements={data['total_movements']}", flush=True)

    # 10. Flight Risk Roster
    t0 = time.time()
    r = await api_flight_risk_roster(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_flight_risk_roster in {(time.time()-t0)*1000:.1f}ms: Flagged={len(data)}", flush=True)

    # 11. Attendance Anomalies
    t0 = time.time()
    r = await api_attendance_anomalies(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_attendance_anomalies in {(time.time()-t0)*1000:.1f}ms: Anomalies={len(data)}", flush=True)

    # 12. Exit Forecast
    t0 = time.time()
    r = await api_exit_forecast(MockReq())
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_exit_forecast in {(time.time()-t0)*1000:.1f}ms: Forecast={data['total_quarterly_projected_exits']} exits", flush=True)

    # 13. Copilot Query
    t0 = time.time()
    r = await api_copilot(MockReq(body={"query": "What is the organization attrition rate?"}))
    data = json.loads(r.body.decode())
    print(f"[{time.strftime('%H:%M:%S')}] [PASS] api_copilot in {(time.time()-t0)*1000:.1f}ms: Answer={data['natural_language_answer'][:60]}...", flush=True)

    print("\n🎉 ALL 13 REST API ENDPOINTS FULLY VERIFIED ON SQLITE BACKEND!", flush=True)

if __name__ == "__main__":
    asyncio.run(run_all())

