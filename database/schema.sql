-- ============================================================================
-- AI-Powered HR Workforce Insights Dashboard
-- Database Schema Definition (SQLite3)
-- Target RDBMS: SQLite 3.35+ (Self-Contained, Zero Configuration)
-- ============================================================================

-- Table 1: employee_master
CREATE TABLE IF NOT EXISTS employee_master (
    employee_id         TEXT PRIMARY KEY,
    department          TEXT NOT NULL,
    designation         TEXT NOT NULL,
    joining_date        TEXT NOT NULL,
    employment_status   TEXT NOT NULL,
    location            TEXT NOT NULL,
    employment_type     TEXT NOT NULL,
    manager_id          TEXT,
    gender              TEXT NOT NULL,
    date_of_birth       TEXT NOT NULL
);

-- Table 2: attendance
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id           TEXT PRIMARY KEY,
    employee_id             TEXT NOT NULL,
    attendance_date         TEXT NOT NULL,
    attendance_status       TEXT NOT NULL,
    check_in_time           TEXT,
    check_out_time          TEXT,
    scheduled_working_day   INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
);

-- Table 3: leave_requests (maps to leave.csv)
CREATE TABLE IF NOT EXISTS leave_requests (
    leave_id        TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL,
    leave_type      TEXT NOT NULL,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    leave_days      INTEGER NOT NULL,
    approval_status TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
);

-- Table 4: workforce_movements
CREATE TABLE IF NOT EXISTS workforce_movements (
    movement_id          TEXT PRIMARY KEY,
    employee_id          TEXT NOT NULL,
    movement_type        TEXT NOT NULL,
    previous_department  TEXT NOT NULL,
    new_department       TEXT NOT NULL,
    previous_designation TEXT NOT NULL,
    new_designation      TEXT NOT NULL,
    movement_date        TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
);

-- Table 5: attrition
CREATE TABLE IF NOT EXISTS attrition (
    employee_id     TEXT PRIMARY KEY,
    exit_date       TEXT NOT NULL,
    exit_type       TEXT NOT NULL,
    exit_reason     TEXT NOT NULL,
    department      TEXT NOT NULL,
    rehire_eligible TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
);

-- Table 6: onboarding
CREATE TABLE IF NOT EXISTS onboarding (
    onboarding_id   TEXT PRIMARY KEY,
    employee_id     TEXT NOT NULL,
    task_name       TEXT NOT NULL,
    assigned_date   TEXT NOT NULL,
    completion_date TEXT,
    task_status     TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_master(employee_id)
);

-- Compatibility view for 'leave'
DROP VIEW IF EXISTS `leave`;
CREATE VIEW `leave` AS SELECT * FROM leave_requests;

-- High-performance analytical indexes
CREATE INDEX IF NOT EXISTS idx_emp_dept ON employee_master(department);
CREATE INDEX IF NOT EXISTS idx_emp_loc ON employee_master(location);
CREATE INDEX IF NOT EXISTS idx_emp_status ON employee_master(employment_status);
CREATE INDEX IF NOT EXISTS idx_att_emp_date ON attendance(employee_id, attendance_date);
CREATE INDEX IF NOT EXISTS idx_att_status ON attendance(attendance_status);
CREATE INDEX IF NOT EXISTS idx_leave_emp ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_attr_emp ON attrition(employee_id);
CREATE INDEX IF NOT EXISTS idx_onb_emp ON onboarding(employee_id);
