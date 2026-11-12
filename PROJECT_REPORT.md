# WorkforceAI: AI-Powered HR Workforce Insights & Copilot Report

---

## 1. Problem Statement

Modern organizations struggle to manage human capital effectively because workforce data is fragmented, reporting is reactive, and predictive visibility is missing:

* **Data Silos Across HR Systems:** Employee profiles, biometric attendance logs, leave requests, onboarding checklists, internal transfers, and exit interviews reside in disconnected spreadsheets and tools, making unified reporting slow and error-prone.
* **Reactive (Lagging) Insights:** Traditional HR dashboards only surface historical numbers (e.g., past attrition counts or last month's attendance), failing to warn managers before high-risk employees decide to resign.
* **High Cost of Unplanned Attrition:** Losing experienced staff disrupts operations and increases hiring and onboarding costs. Without automated flight-risk detection or exit forecasting, HR teams cannot intervene early with stay interviews or retention plans.
* **Technical Barrier to Data Access:** Non-technical HR leaders and business managers cannot quickly query complex workforce metrics or employee behavioral trends on demand without relying on data analysts or writing SQL queries.
* **Lack of Role-Isolated Self-Service:** Employees need instant visibility into their own attendance, leave balances, and onboarding progress without exposing confidential company-wide metrics or peer data.

---

## 2. Proposed Solution

We built **WorkforceAI**, an end-to-end, self-contained **HR Workforce Intelligence Dashboard & Generative AI Copilot** that unifies descriptive SQL analytics, predictive Machine Learning, and natural-language AI assistance into a single platform:

* **Centralized Relational Data Warehouse (SQLite3):** Consolidated 6 cleaned HR datasets (`195,262` total records across 500 employees and 7 departments) into a zero-configuration, ACID-compliant local relational database (`database/hr_workforce.db`).
* **Real-Time KPI Analytics Engine (`backend/kpi_engine.py`):** Parameterized SQL aggregation engine delivering real-time executive KPIs across Headcount, Attrition, Attendance Compliance, Leave Utilization, Onboarding Progress, and Internal Mobility.
* **Predictive Machine Learning Engine (`backend/ml_engine.py`):**
  * *Attrition Flight-Risk Scoring:* Balanced `RandomForestClassifier` (`n_estimators=100`, `max_depth=5`, `class_weight='balanced'`) predicting employee departure probability and ranking the **Top 3 Explainable Contributing Factors**.
  * *Attendance Anomaly Detection:* Department-relative statistical Z-score outlier detection (`threshold=2.0`) flagging excessive absenteeism, Monday/Friday absence clustering, and frequent short workdays (`<6` hours).
  * *Exit Forecasting:* Linear trend projection over historical monthly exits to forecast upcoming quarterly attrition.
* **Dual-Tier Generative AI Copilot (`genai/hr_agent.py` & `backend/auth_service.py`):**
  * *Tier A (Google Gemini Function Calling):* Powered by `gemini-3-flash-preview` with tool calling against verified SQLite/ML functions so answers are strictly grounded in real numbers with zero hallucinations.
  * *Tier B (Deterministic Offline Fallback):* High-speed regex & entity router ensuring uninterrupted operation even without network access or API quota.
  * *Strict Guardrails & RBAC:* Blocks prompt injections and out-of-domain queries, while scoping Employee logins strictly to their personal records.
* **Interactive Dual-Portal Dashboard (`frontend/`):** Pure HTML5/CSS3/ES6 Single-Page Application featuring Chart.js visualizations, a unified `[ ⫸ Filters ▾ ]` popover (Department, Location, Date Range), sidebar-integrated user controls, and a compact/expandable AI Copilot widget.

---

## 3. Architecture

The system follows a **5-Layer Modular Architecture**, orchestrated through a single Starlette/Uvicorn ASGI server (`run.py`):

```text
+-----------------------------------------------------------------------------------+
| 1. PRESENTATION LAYER (Pure HTML5 / CSS3 / Vanilla ES6 JS + Chart.js 4.4)        |
|  - Dual Portals: HR Executive Admin Portal (4 Tabs) & Employee Self-Service View  |
|  - Unified Global Filter Popover (Dept, Location, Date Range) & Active Filter Tags|
|  - Interactive AI Copilot Popup (385x560px) with Full-Window Expand/Collapse      |
+-----------------------------------------+-----------------------------------------+
                                          | REST API (JSON over HTTP)
                                          v
+-----------------------------------------------------------------------------------+
| 2. API GATEWAY & SECURITY LAYER (Starlette ASGI + Auth Service)                   |
|  - backend/api_server.py: Async REST endpoints + static UI + NoCacheMiddleware    |
|  - backend/auth_service.py: SHA-256 credential verification & Role-Based Routing  |
+-------------------+---------------------------------------------+-----------------+
                    |                                             |
                    v                                             v
+---------------------------------------+     +-------------------------------------+
| 3. ANALYTICS & ML ENGINE              |     | 4. GENERATIVE AI LAYER              |
|  - backend/kpi_engine.py (SQL KPIs)   |<----+  - genai/hr_agent.py                |
|  - backend/ml_engine.py (Scikit-Learn)|     |  - Tier A: Gemini 3 Flash Tool Call |
|    * Random Forest Flight-Risk Model  |     |  - Tier B: Deterministic Router     |
|    * Z-Score Attendance Anomalies     |     |  - Dataset Guardrails & RBAC Scope  |
|    * Linear Exit Trend Forecasting    |     |  - RLHF Thumbs Up/Down Telemetry    |
+-------------------+-------------------+     +-------------------------------------+
                    |
                    v
+-----------------------------------------------------------------------------------+
| 5. DATA & STORAGE LAYER (SQLite3 + Cleaned CSV Pipeline)                          |
|  - database/hr_workforce.db (195,262 rows across 6 domain tables + users table)   |
|  - database/load_data.py & setup_users.py (ETL & hashed user account seeding)     |
|  - data/employee_roster.csv (502 records with firstname.lastname@workforce.ai)    |
+-----------------------------------------------------------------------------------+
```

### Key Technology Stack
* **Backend & Runtime:** Python 3.13, Starlette, Uvicorn
* **Database:** SQLite3 (built-in, zero external daemon)
* **Data & ML:** Pandas, NumPy, Scikit-Learn (`RandomForestClassifier`)
* **GenAI:** Google Gemini (`gemini-3-flash-preview` via REST API) + Deterministic Fallback Router
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6 modules), Chart.js (UMD)

---

## 4. Functional Flow

1. **Authentication & Role Resolution:**
   * Users sign in on the login screen using corporate email credentials (`admin@workforce.ai` / `sarah.jenkins@workforce.ai` for HR Admin, or `firstname.lastname@workforce.ai` for Employees).
   * `auth_service.py` validates the SHA-256 password hash against the SQLite `users` table and routes the user to either the **HR Executive Portal** or **Employee Self-Service Portal**.

2. **Dashboard Initialization & Visualization Rendering:**
   * For **HR Admins**, the SPA fetches `/api/overview`, `/api/trends`, `/api/attrition-onboarding`, `/api/attendance`, `/api/leaves`, `/api/flight-risk`, `/api/attendance-anomalies`, and `/api/onboarding-mobility`.
   * Chart.js renders interactive visualizations across 4 dedicated tabs:
     1. *Overview* (KPI cards, Workforce Trend spline chart, Department Distribution donut).
     2. *Attrition & Onboarding* (Exit Drivers bar chart, Onboarding Milestone donut, ML Flight-Risk table).
     3. *Attendance & Leave* (Attendance breakdown, Leave Quota distribution, Z-Score Anomaly table).
     4. *Workforce Movement* (Promotions/Transfers/Role Changes and searchable Employee Roster).

3. **Dynamic Global Filtering:**
   * Clicking `[ ⫸ Filters ▾ ]` in the top bar opens a unified popover containing **Department**, **Location**, and **From/To Date Range** controls.
   * Applying filters appends query parameters to backend API calls, updates active filter count badges and removable filter pills, and re-renders all visible KPIs, charts, and data tables in sync.

4. **Conversational AI Copilot Flow:**
   * Clicking the floating Copilot button opens a docked `385px × 560px` popup window (expandable to cover the full tab window via `[ ⤢ ]` and collapsible back via `[ 🗗 ]` without overlapping the page).
   * Natural-language queries pass through dataset guardrails (`check_workforce_dataset_guardrails()`), invoke Gemini tool calling (`gemini-3-flash-preview`) against live SQL/ML tools, display collapsible reasoning steps + grounded answers + recommended actions, and capture RLHF thumbs-up/thumbs-down feedback.
   * **Employee Portal Isolation:** Employee chat requests go through `/api/employee/copilot`, where RBAC guardrails reject company-wide/peer queries and ground Gemini strictly in that individual employee's attendance, leave, and onboarding records.

---

## 5. Business Overview

WorkforceAI converts raw operational HR logs into strategic decision-making value for leadership, HR business partners, and employees:

### Key Workforce Metrics Tracked (Verified Baseline)
* **Workforce Scale & Growth:** `500` total employees tracked (`430` active, `70` exited, `169` onboarded) with **+99 net headcount growth** and a **2.41x replacement ratio**.
* **Retention & Attrition:** **18.4% attrition rate** (period turnover on `380.5` average headcount) and **2.92 years** (`35.0` months) average tenure, with ML-driven flight-risk alerts identifying employees needing proactive retention check-ins.
* **Attendance & Engagement:** `190,259` scheduled workdays tracked with **80.04% on-site presence**, **9.32% remote work**, **5.29% absenteeism**, and **8.25 average daily productive work hours**.
* **Leave & Quota Management:** `1,874` leave requests (`4,656` approved days against a `5,160`-day quota = **90.2% utilization**), with a **79.03% manager approval rate** and visibility into `214` pending requests.
* **Onboarding & Internal Mobility:** **88.16% onboarding completion** (`2,204` of `2,500` tasks completed across new hires) and `59` internal career movements (`26` transfers, `19` role changes, `14` promotions).

### Measurable Business Impact
* **Proactive Retention:** Replaces guesswork with explainable ML flight-risk scores and exit forecasts so HR can retain key talent in high-turnover units (e.g., IT and Finance) before resignations happen.
* **Operational Efficiency:** Eliminates hours of manual spreadsheet consolidation by providing instant self-service executive dashboards and natural-language AI answers in ~2–3 seconds.
* **Workforce Governance & Security:** Enforces strict role-based isolation between executive HR analytics and personal employee self-service, while grounding AI outputs exclusively in verified SQLite data to prevent hallucinations.

