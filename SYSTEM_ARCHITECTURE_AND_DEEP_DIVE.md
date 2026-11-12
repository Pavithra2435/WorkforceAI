# WorkforceAI — Comprehensive System Architecture, Algorithms & Deep Dive

> **Document Type:** Production Engineering Whitepaper & Technical Deep Dive  
> **Target Audience:** Engineering Leads, HR Technology Executives, System Architects  
> **Status:** Fully Implemented, Verified, and Active on `http://127.0.0.1:8000`

---

## 1. Problem Statement

Modern enterprise human resource departments face significant systemic challenges in workforce management:

1. **Disconnected Data Silos:** Workforce data is fractured across disparate systems—biometric access turnstiles, leave request trackers, HRIS employee databases, payroll records, and exit surveys. Consolidating this into actionable intelligence is typically manual, slow, and prone to error.
2. **Lagging / Reactive Analytics:** Standard HR dashboards are purely retrospective—they report who has *already* resigned, what the absence rate was last quarter, or how many exit interviews were conducted. They fail to offer **predictive foresight**.
3. **High Cost of Unplanned Attrition:** Replacing an experienced employee costs 50% to 200% of their annual salary in lost productivity, recruiting fees, and ramp-up time. HR managers lack early warning alerts for disengaged or high-flight-risk staff before resignation notices arrive.
4. **Information Accessibility Barrier:** Business leaders and frontline people managers cannot query workforce systems on demand without requesting specialized reports from Data/BI teams or writing complex SQL queries.

---

## 2. Desired Solution We Built

**WorkforceAI** is an end-to-end, self-contained **Human Capital Intelligence Platform** and **Conversational Copilot** that unifies operational HR data into an integrated analytical and predictive ecosystem:

- **Unified Relational Store:** 195,262 workforce transactions modeled into a clean, normalized SQLite database with enforced ACID constraints.
- **Real-Time Structured Analytics:** Single-pass parameterized SQL aggregation queries delivering sub-15ms calculations for Headcount, Attrition, Attendance, and Leave KPIs.
- **Proactive Machine Learning:**
  - *Attrition Flight-Risk Scoring* predicting flight probability with top-3 explainable risk factors.
  - *Attendance Anomaly Detection* flagging irregular absenteeism and productivity drop-offs.
  - *Quarterly Exit Forecasting* projecting staffing gaps 3 to 12 months ahead.
- **Grounded GenAI HR Copilot:** Autonomous tool-calling reasoning agent with SQLite database citations, thinking transparency, RLHF feedback, and conversational memory.
- **Modern Interactive Dashboard (SPA):** Pure HTML5/CSS3/Vanilla JS single-page application with dual-portal role routing (HR Admin vs Employee Self-Service), Chart.js visualizations, unified global filter popover, and expandable copilot popup window.

---

## 3. Technology Stack & Technical Justifications

| Technology | Layer | Primary Role | Why Selected Over Alternatives |
| :--- | :--- | :--- | :--- |
| **Python 3.13** | Core Runtime | Backend engine, ML pipeline, AI orchestration | Richest data science ecosystem; native SQLite bindings; rapid prototyping. |
| **SQLite 3.x** | Database | Relational storage & SQL analytics | **Zero external server dependency.** Eliminates MySQL/Postgres daemon setup, network latency, and driver incompatibilities. Provides full ACID compliance and instant portability. |
| **Starlette / Uvicorn** | ASGI Web Server | REST APIs & static asset serving | Significantly faster and more lightweight than Django or Flask; native async support; built-in static file mounting; zero-cache middleware integration. |
| **Scikit-Learn** | Machine Learning | Classification, anomaly detection, forecasting | Robust, deterministic, production-grade algorithms with minimal overhead; native support for class balancing, feature importance, and model evaluation metrics. |
| **Pandas & NumPy** | Data Engineering | Feature engineering, vectorized transformations | Fast in-memory array operations, datetime handling, and statistical grouping across 190k+ rows. |
| **Vanilla HTML5 / CSS3 / ES6** | Frontend SPA | User interface & interaction | **No build step required** (no Node.js, Webpack, or Vite build pipeline). Zero bundle churn, instant page load, universal browser compatibility, and clean maintainability. |
| **Chart.js 4.4 (UMD)** | Data Visualization | Canvas-rendered responsive graphs | Lightweight, declarative charting with smooth transitions, tooltip support, and responsive resizing. |

---

## 4. Algorithms Used, Mathematical Logic & Why Chosen

### 4.1. Task 1: Attrition Classification (Flight-Risk Scoring)
- **Algorithm:** `RandomForestClassifier` (Ensemble of Decision Trees)
- **Hyperparameters:**
  - `n_estimators = 100`: High variance reduction across 100 bootstrap trees.
  - `max_depth = 5`: Prunes deep branches to prevent memorization and guarantee explainability.
  - `class_weight = 'balanced'`: Automatically adjusts weights inversely proportional to class frequencies:
    $$W_j = \frac{N}{K \cdot N_j}$$
    *(where $N$ is total samples, $K$ is number of classes, and $N_j$ is samples in class $j$)*.
  - `random_state = 42`: Ensures deterministic reproducibility.
- **Engineered Features:**
  1. `tenure_months`: Active company tenure in months.
  2. `absence_rate`: $\frac{\text{Absent Days}}{\text{Total Scheduled Workdays}}$.
  3. `remote_rate`: $\frac{\text{Remote Work Days}}{\text{Total Scheduled Workdays}}$.
  4. `unpaid_leave_days`: Total volume of approved unpaid leaves.
  5. `sick_leave_days`: Total volume of medical/sick leaves taken.
  6. `onboarding_completion_rate`: Proportion of completed onboarding checkpoints.
  7. `department_*`: One-hot encoded categorical department vectors.
- **Why Random Forest over Logistic Regression / Deep Learning:**
  - Tabular HR data exhibits non-linear relationships (e.g., both short tenure $<12$ months and extended tenure $>48$ months elevate risk for different reasons).
  - Robust against multicollinearity between absence rates and leave days.
  - Resilient to outliers without requiring sensitive numerical normalization.
- **Explainable AI (XAI) Scoring:**
  To make predictions actionable for HR managers, each individual employee's risk score is mapped to their **Top 3 Contributing Factors** using a normalized deviation-importance function:
  $$\text{Impact}_i = \frac{x_i - \mu_{\text{org}}}{\sigma_{\text{org}}} \cdot \text{FeatureImportance}_i$$
  Generates clear human-readable explanations (e.g., *"High Absenteeism Rate (14.2% vs org avg 8.1%)"*, *"Short Company Tenure (7.4 months)"*).

---

### 4.2. Task 2: Attendance Anomaly Detection
- **Algorithm:** Statistical $Z$-Score Multi-Factor Outlier Detection
- **Formula:**
  $$Z = \frac{X - \mu_{\text{dept}}}{\sigma_{\text{dept}}}$$
- **Evaluated Signals:**
  1. **Excessive Absence Deviation:** $Z_{\text{absence}} \ge 2.0$ (top 2.5% tail of department absence).
  2. **Weekend-Adjacent Clustering:** Disproportionate Friday and Monday absences indicating intentional absenteeism patterns.
  3. **Short Workday Drift:** Frequent logged days with $<6.0$ logged hours.
- **Why Statistical $Z$-Score over Isolation Forest:**
  - Department-specific baselines prevent false positives (e.g., Sales has different mobility patterns than Customer Support).
  - Deterministic and immediately justifiable in audit or employee review scenarios.

---

### 4.3. Task 3: Time-Series Attrition Forecasting
- **Algorithm:** Ordinary Least Squares (OLS) Trend Regression over rolling historical monthly exits.
- **Projection Horizon:** 3, 6, and 12 months ahead.
- **Why Chosen:** Workforce exit datasets with 14 months of history do not possess sufficient seasonal cycles for heavy ARIMA or LSTM models. Linear projection paired with quarterly moving averages delivers reliable, transparent forecasts for headcount capacity planning.

---

### 4.4. Task 4: Autonomous Controlled Tool Calling & Reasoning Agent
- **Architecture:** Dual-Tier Intent & Entity Routing
  - **Tier A (LLM Function Calling):** When configured with Gemini / OpenAI API keys, prompts are parsed into structured function calls (`tool_executive_kpis`, `tool_employee_flight_risk`, etc.).
  - **Tier B (Deterministic Entity & Pattern Router):** Offline, zero-latency deterministic parser that regex-matches intents, extracts entities (departments, employee IDs, time horizons), queries the SQLite database directly, and returns formatted responses with full thinking traces.
- **Safety Guardrails:**
  - Query parameters strictly whitelist database column names to prevent SQL injection.
  - Employee scope guardrails prevent standard employee logins from viewing peer salaries, flight risks, or company-wide executive turnover figures.

---

## 5. Functional Flow of the Dashboard

### Step 1: Authentication & RBAC Gatekeeper
- User enters corporate credentials.
- `backend/auth_service.py` evaluates password against salted SHA-256 hash in SQLite `users` table.
- Determines view profile:
  - `hr_admin` -> Redirects to Executive Multi-Tab Analytics Workspace.
  - `employee` -> Redirects to Scoped Self-Service Portal.

### Step 2: Executive Dashboard Initialization
- Frontend asynchronously requests endpoints `/api/overview`, `/api/attrition-onboarding`, `/api/attendance`, `/api/leaves`, and `/api/workforce-movements`.
- Starlette calls `backend/kpi_engine.py` and `backend/ml_engine.py`.
- DOM paints KPI cards, line charts, and donut diagrams simultaneously via Chart.js.

### Step 3: Global Filter Interactions
- User opens the unified `[ ⫸ Filters ▾ ]` popover in the top navigation bar.
- Selecting Department, Location, or Date Ranges fires parameterized queries.
- Live badge counters update (e.g., `Filters (2)`) and active filter pills render on the screen.
- All 4 dashboard tabs and tables dynamically refresh to the filtered subset.

### Step 4: AI Copilot Interaction & Window Sizing
- User clicks the floating Copilot bubble in the bottom right corner.
- Copilot opens as a clean, docked `385px × 560px` popup.
- Clicking the lightbulb icon toggles interactive follow-up prompt chips.
- Clicking the **Expand button (`[ ⤢ ]`)** smoothly expands the chatbot to cover the entire browser tab window for dedicated analysis.
- Clicking the **Collapse button (`[ 🗗 ]`)** instantly shrinks it back to the bottom-right corner without overlapping dashboard charts.

---

## 6. Deep Dive into the 4 Core Dashboard Tabs

### 1. Overview Tab
- **Macro KPI Cards:** Total Employees (500), Attrition Rate (18.4%), Office Attendance Rate (80.0%), Leave Utilization (78.9% of quota).
- **Workforce Trend Spline Chart:** 14-month continuous timeline showing net workforce growth (169 onboarded vs 70 exits = +99 net headcount).
- **Department Distribution Donut:** Visual breakdown of all 7 departments with legend and percentage distributions.

### 2. Attrition & Onboarding Tab
- **Exit Factors Bar Chart:** Visual ranking of historical exit drivers (Career Change: 19, Performance: 11, Role Mismatch: 10, Personal: 9, Compensation: 8, Relocation: 7, Better Opportunity: 6).
- **Onboarding Milestone Progress:** Donut chart tracking task completion (88.2% completed across 2,500 onboarding milestones).
- **Employees at Risk of Leaving Table:** Real-time ML-scored roster displaying employee names, department, flight-risk score badge (High/Medium), and explainable contributing factors.

### 3. Attendance & Leave Tab
- **Presence Compliance Gauge:** Tracking remote vs in-office attendance compliance.
- **Leave Quota Distribution:** Annual leave consumption by leave category (Vacation, Sick, Casual, Unpaid).
- **Irregular Attendance Anomaly Alerts:** Roster of employees flagged with high z-score absenteeism patterns for management review.

### 4. Workforce Movement Tab
- **Internal Mobility Metrics:** Tracking internal promotions, lateral department transfers, and organizational role mobility.
- **Department Roster Explorer:** Searchable, paginated employee table with department filtering and export readiness.

---

## 7. Dual Portal & Role-Based Access Control (RBAC)

The system enforces strict security and presentation boundaries based on authenticated user identity:

- **HR Executive Admin Portal:**
  - Company-wide KPIs & all 4 analytical tabs
  - Full 500-employee master roster & flight-risk alerts
  - Global filter popover & company-level Copilot
- **Employee Self-Service Portal:**
  - Strictly personal attendance history & work hours
  - Personal leave balances & remaining quota
  - Onboarding milestone checklist
  - Company HR policies & scoped Personal Assistant

