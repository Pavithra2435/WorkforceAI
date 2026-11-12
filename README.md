# AI-Powered HR Workforce Insights Dashboard

An end-to-end, enterprise-ready HR analytics solution built on a self-contained SQLite database, structured SQL analytics engine, Machine Learning predictive services, a Generative AI assistant layer, and an interactive pure HTML5/CSS3/JavaScript dashboard.

---

## 📁 Modular Project Structure

```text
hr/
│
├── .venv/                              # Isolated Python virtual environment
│
├── data/
│   └── cleaned/                        # Validated CSV datasets & engineered ML table
│       ├── employee_master.csv         # 500 rows
│       ├── attendance.csv              # 190,259 rows
│       ├── leave.csv                   # 1,874 rows
│       ├── workforce_movements.csv     # 59 rows
│       ├── attrition.csv               # 70 rows
│       ├── onboarding.csv              # 2,500 rows
│       ├── dataset_summary.csv         # Dataset summary metadata
│       └── final_ml_workforce_dataset.csv
│
├── database/
│   ├── schema.sql                      # Step 1: SQLite3 DDL tables, constraints & indexes
│   ├── schema_sqlite.sql               # SQLite3 reference DDL schema
│   ├── hr_workforce.db                 # Self-contained SQLite3 database (195,262 rows)
│   └── load_data.py                    # Step 1: Automated CSV-to-SQLite ingestion script
│
├── backend/
│   ├── __init__.py                     # Backend package initialization
│   ├── api_server.py                   # High-performance Starlette ASGI REST API server
│   ├── kpi_engine.py                   # Step 2: Centralized SQLite analytics & KPI functions
│   └── ml_engine.py                    # Step 3: Machine Learning Engine (Flight-Risk, Anomalies, Forecast)
│
├── genai/                              # Step 4: Generative AI Assistant Layer
│   ├── __init__.py                     # Exposes ask_hr_copilot and tool schemas
│   ├── hr_agent.py                     # Controlled tool-calling & reasoning agent
│   ├── test_agent.py                   # Evaluation test runner (5 benchmark queries)
│   └── README.md
│
├── frontend/                           # Step 5: Modern Interactive SPA Dashboard (Pure HTML5, CSS3 & JS)
│   ├── index.html                      # Single-page dashboard application
│   ├── css/style.css                   # Responsive layout, dark theme & animations
│   └── js/app.js                       # Chart.js graphs, sidebar toggle, filters & API bridge
│
├── .env                                # Local database configuration
├── .env.example                        # Configuration template
├── requirements.txt                    # Project dependencies
└── README.md                           # Documentation & interview talking points
```

---

## 🚀 Virtual Environment & Setup Instructions

### 1. Virtual Environment (`.venv`)
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. Dependencies
Dependencies are installed directly in `.venv`:
```bash
pip install -r requirements.txt
```
*(Dependencies: `pandas`, `numpy`, `scikit-learn`, `starlette`, `uvicorn` — `sqlite3` is built into Python)*

### 3. Database Configuration
Configured in [`.env`](.env):
```env
DB_PATH=database/hr_workforce.db
DB_NAME=hr_workforce.db
```
*(No MySQL server, background services, or MySQL Workbench needed)*

---

## 🛠️ Step-by-Step Module Execution

### Step 1: Database Setup & Data Ingestion
Creates `hr_workforce_db`, instantiates `schema.sql`, and bulk-loads all 6 CSVs:
```bash
python database/load_data.py
```

### Step 2: Centralized HR Analytics & KPI Engine
Calculates executive KPIs, department breakdowns, attrition drivers, and attendance metrics:
```bash
python backend/kpi_engine.py
```

### Step 3: Machine Learning Engine
Trains the balanced Random Forest model, scores flight risks, flags anomalies, and forecasts exits:
```bash
python backend/ml_engine.py
```

### Step 4: Generative AI Assistant & Controlled Tool-Calling Layer
Runs the natural-language query engine across 6 benchmark workforce questions:
```bash
python genai/test_agent.py
```

### Step 5: Interactive Web Dashboard UI (Pure HTML5, CSS3 & JavaScript)
Launches the full interactive enterprise dashboard in your browser:
```bash
python run.py
```
*(Runs at `http://localhost:8000`)*

---

## 🖥️ Step 5: Frontend Dashboard UI (`frontend/`)

Implements **Blocks 6A, 6B, and 7** into a modern, responsive Single Page Application (SPA) built with pure HTML5, CSS3, and modern JavaScript, served via a Starlette ASGI REST API backend:

### Key Capabilities & Layout:
1. **Dynamic Sidebar Controls**:
   - Live MySQL connection status pill (`🟢 Connected to MySQL: hr_workforce_db`).
   - Multi-select filters for **Department** and **Location** directly populated from MySQL.
   - One-click "Reset All Filters" button.
2. **Top Executive Metric Strip**:
   - 5 high-impact cards: Total Headcount, Active Headcount, Exited Count, Attrition Rate %, and Average Active Tenure.
   - All cards dynamically update based on the sidebar filters.
3. **Tab 1: 📊 Executive Overview**:
   - Grouped bar chart comparing active vs exited employees across departments.
   - Donut chart of primary exit reasons.
   - Detailed department turnover table with Streamlit native progress bars.
4. **Tab 2: 🤖 Predictive ML Intelligence**:
   - High flight-risk prioritization roster (employees $\ge 60\%$ risk).
   - Single employee deep-dive search (e.g., `E0087`) with interactive flight-risk gauge meter and explainable contributing factors.
   - Attendance anomaly detection alerts ($Z \ge 2.0$) with Department Absenteeism, Mon/Fri clustering, and short workday flags.
   - 3-Month exit forecast trend bar chart.
5. **Tab 3: 🗓️ Attendance & Leave Governance**:
   - Attendance distribution donut chart (Present 80.0%, Remote 9.3%, Absent 5.3%, On Leave 4.9%, Half Day 0.5%).
   - Department-wise average daily logged working duration bar chart.
   - Leave consumption by leave type and approval status split.
6. **Tab 4: 🚀 Onboarding & Career Mobility**:
   - Onboarding milestone completion progress gauge (88.16% completion rate).
   - Internal career transitions breakdown (Promotions, Transfers, Role Changes).
7. **Tab 5: 💬 GenAI HR Co-Pilot**:
   - Natural-language conversational interface with suggested prompt chips.
   - Grounded responses split into **📋 Factual Findings** and **💡 Strategic HR Recommendations**.
   - Expandable **🔍 Backend Tool Inspection** providing full transparency into the tool invoked and raw database/ML payload.

---

## 🎯 Interview Talking Points for Step 5

1. **Separation of Concerns**:
   - The UI layer (`frontend/app.py`) is completely decoupled from database logic. It interacts strictly through the analytical API in `kpi_engine`, predictive endpoints in `ml_engine`, and conversational interface in `hr_agent`.
2. **Dynamic Reactivity with High Performance**:
   - Uses Streamlit's `@st.cache_data` decorators with sensible TTLs to eliminate redundant database roundtrips, ensuring instantaneous filter reactivity across 195,000+ attendance records.
3. **Explainable AI in Action**:
   - Evaluators can inspect the exact tool parameters and raw data for every response generated by the AI agent via the expandable JSON inspection card.


---

## 🤖 Step 4: Generative AI Layer Deep Dive (`genai/`)

Implements **Block 7** of the system architecture:
`User Query -> Intent Recognition -> Controlled Tool Calling -> Verified Backend Results -> Natural-Language Response + Actionable Insights`

### Two-Tier Execution Strategy
1. **Tier A (LLM Tool Calling)**:
   - When `GEMINI_API_KEY` or `OPENAI_API_KEY` is present, the copilot uses function calling with standardized JSON schemas across all 9 tools.
2. **Tier B (Deterministic Entity & Intent Router)**:
   - Zero-cost, high-speed, offline fallback that extracts entities (e.g. employee IDs `E0087`, department names, months) and maps queries to the exact tool function. Ensures 100% test pass rates and demo reliability.

### Registered Tools

| Tool Function | Backend Provider | Purpose |
| :--- | :--- | :--- |
| `tool_executive_kpis` | `backend.kpi_engine` | Overall headcount, active/exited counts, attrition rate, tenure. |
| `tool_department_breakdown` | `backend.kpi_engine` | Department-wise headcount and turnover ranking. |
| `tool_attrition_insights` | `backend.kpi_engine` | Top exit reasons, voluntary split, and rehire eligibility. |
| `tool_attendance_kpis` | `backend.kpi_engine` | Present, Remote, Absent rates, and average work hours. |
| `tool_leave_analytics` | `backend.kpi_engine` | Leave distribution by type and approval rates. |
| `tool_onboarding_mobility` | `backend.kpi_engine` | Onboarding progress and internal promotion counts. |
| `tool_flight_risk` | `backend.ml_engine` | ML flight-risk score, risk tier, and explainable factors. |
| `tool_attendance_anomalies`| `backend.ml_engine` | Statistical Z-score outlier detection ($Z > 2.0$). |
| `tool_exit_forecast` | `backend.ml_engine` | Quarterly exit trend projection. |

### Standardized Response Schema
Every call to `ask_hr_copilot(query)` returns:
```json
{
  "query": "Which department has the highest attrition rate?",
  "intent": "department_attrition_ranking",
  "tool_used": "tool_department_breakdown",
  "raw_data": [...],
  "natural_language_answer": "Based on our workforce database, the HR department currently has the highest attrition rate at 16.67%...",
  "recommended_action": "Initiate targeted pulse surveys and stay interviews immediately within HR, Finance, and IT..."
}
```

---

## 🎯 Interview Talking Points for Step 4

1. **Grounded AI vs. Hallucination-Prone Chatbots**:
   - The copilot never guesses or hallucinates metrics. All statistics in the natural language answer are derived strictly from verified backend outputs returned by `kpi_engine` or `ml_engine`.
2. **Controlled Function Calling (Tool-Use Architecture)**:
   - Tools are exposed via strict schemas. The LLM or router acts solely as an orchestrator, decoupling conversational intelligence from transactional database access.
3. **Actionable Insights Over Raw Metrics**:
   - Instead of merely returning raw numbers, the agent provides a **Strategic HR Recommendation** for every query, bridging data analysis with executive decision-making.
4. **Resilient Two-Tier Fallback (Zero-Cost Local Execution)**:
   - The hybrid architecture guarantees that even in network-isolated environments or without active API credits, the application executes deterministically with zero latency.
