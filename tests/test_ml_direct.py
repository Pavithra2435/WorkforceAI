import os
import sys
import time

print(f"[{time.strftime('%H:%M:%S')}] Python starting...", flush=True)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f"[{time.strftime('%H:%M:%S')}] Importing ml_engine...", flush=True)
import backend.ml_engine as ml
print(f"[{time.strftime('%H:%M:%S')}] ml_engine imported.", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] Testing forecast_upcoming_exits...", flush=True)
t0 = time.time()
f = ml.forecast_upcoming_exits(3)
print(f"[{time.strftime('%H:%M:%S')}] forecast done in {time.time()-t0:.2f}s: {f['total_quarterly_projected_exits']} exits", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] Testing get_employee_flight_risk...", flush=True)
t0 = time.time()
r = ml.get_employee_flight_risk(None)
print(f"[{time.strftime('%H:%M:%S')}] flight risk done in {time.time()-t0:.2f}s: {len(r)} high risk employees", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] Testing detect_attendance_anomalies...", flush=True)
t0 = time.time()
a = ml.detect_attendance_anomalies(2.0)
print(f"[{time.strftime('%H:%M:%S')}] anomalies done in {time.time()-t0:.2f}s: {len(a)} anomalies", flush=True)

print("\nAll ML tests completed successfully!", flush=True)

