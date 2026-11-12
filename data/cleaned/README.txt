# Synthetic HR Workforce Insights Dataset

IMPORTANT: All records in this package are synthetically generated for an internship prototype.
They do not represent real employees or a real organization.

Reporting window:
- Attendance and event records: 2025-01-01 through 2026-10-31 (subject to employee joining/exit dates)
- Employee master includes a mix of employees hired before and during the reporting window.

Files:
1. employee_master.csv
   One row per employee. employee_id is the primary identifier.
   Contains current/latest department and designation for the prototype, employment status, joining date, location, employment type, manager_id, and illustrative demographic fields.

2. attendance.csv
   One row per employee per scheduled weekday while employed in the reporting window.
   attendance_id is unique. employee_id links to employee_master.
   Status values: Present, Absent, Remote, Half Day, On Leave.
   Weekends are excluded. This synthetic calendar does not model country-specific public holidays or shift schedules.

3. leave.csv
   One row per leave request. leave_id is unique.
   approval_status values: Approved, Pending, Rejected.
   leave_days counts weekdays within the request date range.

4. attrition.csv
   One row per employee exit in the reporting window.
   employee_id links to employee_master. Exit records represent employees whose master status is Exited.

5. onboarding.csv
   Five standard onboarding tasks per employee. One row per task.
   Pending tasks have a blank completion_date.

6. workforce_movements.csv
   One row per recorded promotion, transfer, or role change.
   Previous and new department/designation are recorded.

Relationships:
- employee_master.employee_id is referenced by attendance.employee_id, leave.employee_id,
  attrition.employee_id, onboarding.employee_id, and workforce_movements.employee_id.
- employee_master has one row per employee; the other tables can have multiple rows per employee.

Important analytical notes:
- Treat this as demonstration data, not evidence about actual HR patterns.
- Confirm metric definitions before calculating KPIs. For example, attrition rate usually uses exits divided by average headcount over a defined period.
- Attendance rate should use eligible scheduled workdays and a clearly defined treatment of remote work, half days, and approved leave.
- The data is synthetic and simplified: no real holiday calendar, payroll, shift roster, or detailed leave balance ledger is included.
- For ML, use a time-aware split where appropriate and avoid using information recorded after the prediction date.
- Do not use demographic attributes for automated employment decisions. Use fairness and privacy checks for any analytical exploration.
