# WorkforceAI — End-to-End Project Summary & Architecture Report

> **Project Name:** WorkforceAI — AI-Powered HR Workforce Insights & Copilot Dashboard  
> **Repository:** `hr/`  
> **Status:** Production-Ready & Actively Running on `http://127.0.0.1:8000`  
> **Technology Stack:** Python 3.13, Starlette ASGI, SQLite3, Scikit-Learn, Chart.js, HTML5/CSS3/Vanilla JS

---

## 1. Executive Summary

**WorkforceAI** is an enterprise-grade, end-to-end Human Resources Intelligence Platform and Generative AI Assistant. It transforms raw corporate workforce logs into actionable executive intelligence, predictive flight-risk alerts, attrition forecasts, and an interactive conversational copilot. 

The application is completely self-contained—requiring **zero external database servers** (MySQL/PostgreSQL) and **zero frontend heavy build toolchains** (npm/webpack)—operating entirely on an optimized **SQLite3** database, a blazing-fast **Starlette** ASGI backend, and a high-performance **HTML5/CSS3/ES6** Single-Page Application (SPA).

---

## 2. End-to-End Project Journey & Milestones

### Phase 1: Data Architecture & Preprocessing
- **Source Datasets (`data/cleaned/`):**
  - `employee_master.csv` (500 records): Demographics, departments, titles, salary bands, hire dates, tenure, locations.
  - `attendance.csv` (190,259 records): Daily check-ins, check-outs, work hours, office presence flags across 14 months.
  - `leave.csv` (1,874 records): Leave types (Sick, Vacation, Casual), date spans, quota consumption, manager approval states.
  - `workforce_movements.csv` (59 records): Internal transfers, promotions, demotions, salary adjustments.
  - `attrition.csv` (70 exit records): Departure dates, primary exit reasons (Career Change, Compensation, Relocation, etc.).
  - `onboarding.csv` (2,500 task records): 5 milestone checkpoints for each new hire (IT Setup, HR Docs, Manager 1:1, etc.).
  - `final_ml_workforce_dataset.csv`: Engineered feature matrix for machine learning model training.
- **Corporate Email Standardisation:**
  - Standardized all 502 records in `data/employee_roster.csv` from generic IDs (`e0001@workforce.ai`) to clean, real-world corporate email addresses (`firstname.lastname@workforce.ai`) with collision-resistant numbering for duplicate names (e.g. `priya.joshi2@workforce.ai`).

---

### Phase 2: Relational Database Design (`database/`)
- **Engine:** SQLite3 (`database/hr_workforce.db`) holding **195,262 total rows**.
- **DDL & Schema (`database/schema.sql`):**
  - Normalised tables: `departments`, `employees`, `attendance`, `leaves`, `workforce_movements`, `attrition`, `onboarding_milestones`, and `users`.
  - Enforced primary keys, foreign key constraints with `ON DELETE CASCADE`, composite indexes on `(employee_id, date)`, and check constraints.
- **Automated Ingestion (`database/load_data.py`):**
  - Automated Python ETL pipeline that validates CSV schema integrity, handles nulls and date formatting, and bulk-inserts records in ACID transactions.
- **Authentication & RBAC Store (`database/setup_users.py`):**
  - Generated credential store for 502 individual accounts:
    - **HR Administrators:** Full access (`admin@workforce.ai`, `sarah.jenkins@workforce.ai`).
    - **Employees:** 500 individual self-service accounts with scoped permissions.
    - Security: Secure password hashing with salt and SHA-256.

---

### Phase 3: Analytics & Machine Learning Engines (`backend/`)
- **Structured KPI Analytics Engine (`backend/kpi_engine.py`):**
  - High-performance, single-pass parameterized SQL aggregation queries calculating:
    - Headcount (Total: 500, Active: 430, Exits: 70, Onboarded: 169).
    - Attrition Rate (18.4% company-wide, broken down by department and tenure).
    - Office Presence Compliance (80.0% benchmarked against company policy).
    - Leave Quota Utilization (78.9% of 5,160 annual company quota).
    - Departmental breakdown (Customer Support 17.2%, IT 16.4%, HR 15.6%, Sales 14.4%, etc.).
    - Monthly workforce movements (Promotions, lateral transfers, department shifts).
- **Machine Learning Services (`backend/ml_engine.py`):**
  - **Flight-Risk Classification:** Trained Scikit-Learn classification model predicting attrition probability based on overtime hours, tenure, recent leaves, and role stagnation.
  - **Attendance Anomaly Detection:** Isolation Forest algorithm detecting anomalous absence spikes and sudden attendance irregularities.
  - **Time-Series Attrition Forecasting:** Moving-average and linear trend forecasting for next 3, 6, and 12-month staffing needs.

---

### Phase 4: Generative AI Assistant & Copilot (`genai/`)
- **HR Copilot Agent (`genai/hr_agent.py`):**
  - Self-grounded reasoning agent connected directly to the SQLite workforce dataset.
  - **Safety Guardrails:** Strict prompt boundaries ensuring the copilot queries verified SQLite tables, preventing hallucinations or unauthorized data leaks.
  - **Transparent Thought Process:** Dynamic step-by-step reasoning traces rendered in the UI with a collapsible "Thought Process" container.
  - **Interactive Features:**
    - **Bulb Icon Prompt Suggestions:** Popover tray providing context-relevant follow-up prompts.
    - **RLHF Feedback Bar:** Thumbs-Up and Thumbs-Down rating buttons with telemetry logging.

---

### Phase 5: Modern Interactive Frontend SPA (`frontend/`)
- **Architecture:** Zero-framework, pure HTML5, CSS3, and ES6 JavaScript (`frontend/index.html`, `frontend/css/style.css`, `frontend/js/app.js`).
- **Design System:** Clean Executive Navy theme (`#0B192C` sidebar, `#F8FAFC` background, `#2563EB` active accents).
- **Core Components & Features:**
  1. **Dual Role Views:**
     - **HR Admin Portal:** Full access to all 4 dashboard tabs (*Overview*, *Attrition & Onboarding*, *Attendance & Leave*, *Workforce Movement*), KPI cards, interactive Chart.js graphs, and search/sort employee tables.
     - **Employee Self-Service Portal:** Clean personal portal showing individual attendance, leave balance counters, onboarding checklists, and personal HR assistant.
  2. **Consolidated Global Filter Dropdown:**
     - Replaced cluttered multiple top-bar dropdowns with a single unified `[ ⫸ Filters ▾ ]` popover.
     - Live badge counter showing active filter count and removable filter chips.
  3. **Sidebar Redesign:**
     - Transferred user profile card and Sign Out button from the top bar into the left sidebar footer.
     - Collapsible sidebar toggle (expanding from `68px` to `250px`).
  4. **Chatbot Window Control (Compact vs Full Window):**
     - Compact popup widget (`385px × 560px`) in the bottom-right corner with a dedicated close `✕` button.
     - Expand button (`⤢`) to maximize the chatbot to cover the full window size of the tab.
     - Collapse button (`🗗`) to restore the compact popup without overlapping dashboard content.

---

### Phase 6: Orchestration & Execution (`run.py`)
- Single command execution:
  ```powershell
  python -u run.py
  ```
- Starts the Starlette ASGI server with Uvicorn on `http://127.0.0.1:8000`.
- Automated browser launch and live API endpoint verification.

---

## 3. System Architecture & Component Mapping

| Component | Files / Paths | Key Responsibilities |
| :--- | :--- | :--- |
| **Data Repository** | `data/cleaned/*.csv`, `data/employee_roster.csv` | Raw and cleaned HR logs, employee profiles, attendance, leaves, exits. |
| **Database Layer** | `database/hr_workforce.db`, `database/schema.sql`, `database/load_data.py` | SQLite3 storage engine, tables, indexes, constraints, bulk CSV loader. |
| **Auth & Security** | `backend/auth_service.py`, `database/setup_users.py` | Password hashing, session token verification, Role-Based Access Control (RBAC). |
| **KPI Engine** | `backend/kpi_engine.py` | High-performance SQL queries for headcount, attrition, attendance, and leaves. |
| **Machine Learning** | `backend/ml_engine.py` | Scikit-Learn flight-risk predictor, anomaly detection, time-series forecasting. |
| **GenAI Copilot** | `genai/hr_agent.py`, `backend/api_server.py` | SQLite grounded chatbot, tool-calling, reasoning chains, RLHF feedback. |
| **Web API Server** | `backend/api_server.py` | Starlette ASGI application, REST endpoints, static file serving, CORS & no-cache headers. |
| **Frontend UI** | `frontend/index.html`, `frontend/css/style.css`, `frontend/js/app.js` | Single-page application, Chart.js visualizations, unified filters, expandable chatbot. |
| **Startup Runner** | `run.py` | Environment validation, database check, Uvicorn server launcher. |

---

## 4. Key Login Credentials

| Role | Email Address | Password | Permissions & Scope |
| :--- | :--- | :--- | :--- |
| **HR Admin** | `admin@workforce.ai` | `admin123` | Full access to all 4 company-wide tabs, company KPIs, flight-risk tables, all 500 employees. |
| **HR Admin** | `sarah.jenkins@workforce.ai` | `admin123` | Full HR Officer administrative access. |
| **Employee** | `firstname.lastname@workforce.ai`<br>*(e.g., `ajay.sharma@workforce.ai`)* | `employee123` | Strictly scoped personal portal (My Attendance, My Leaves, Onboarding, Personal Assistant). |

---

## 5. Summary of Recent Enhancements

1. **AI Chatbot Window Expand / Collapse:**
   - Added an **Expand icon button** (`[ ⤢ ]`) in the header next to `✕`.
   - Clicking expand scales the chatbot to fill the full tab window with a centered, distraction-free conversational canvas.
   - Clicking collapse (`[ 🗗 ]`) instantly restores it to the bottom-right docked widget (`385px × 560px`) without overlapping page content.
2. **Consolidated Filter System:**
   - Unified Department, Location, and Date Range filters inside a single top-right `[ ⫸ Filters ▾ ]` dropdown.
   - Added active filter count pill and removable tag badges.
3. **Sidebar & Header Reorganization:**
   - Moved the user card and Sign Out button from the top bar into the left sidebar footer.
   - Cleaned the login screen email placeholder to display clean `"Email"` text.
4. **Name-Based Corporate Emails:**
   - Updated all 502 employee records from ID numbers to real name email addresses and synchronized the SQLite authentication database.

