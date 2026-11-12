# WorkforceAI Frontend Web Application (`frontend/`)

A modern, responsive, and high-performance Single Page Application (SPA) built purely with **HTML5**, **CSS3**, and **Vanilla Modern JavaScript (ES6 Modules)**, completely replacing Streamlit.

---

## 🏛️ Client-Server Architecture

```text
hr/
├── backend/
│   ├── kpi_engine.py          # Structured SQL metrics & KPIs
│   ├── ml_engine.py           # ML flight risk, Z-score anomalies, exit forecast
│   └── api_server.py          # Starlette ASGI REST API server
│
├── genai/
│   ├── hr_agent.py            # AI Copilot engine (controlled tool-calling)
│   └── test_agent.py
│
├── frontend/
│   ├── index.html             # Clean Semantic HTML5 Single Page Application
│   ├── css/
│   │   └── style.css          # Executive Light Theme (60-30-10), Responsive CSS Grid & Drawer Animations
│   └── js/
│       ├── app.js             # Core App Controller, View Routing, Filter Management, Side-Chat Drawer
│       ├── api.js             # Client-side API fetch client communicating with backend
│       └── charts.js          # Responsive chart rendering (Chart.js + SVG fallback)
│
└── run.py                     # One-click launcher: starts the API & Web server on http://localhost:8000
```

---

## 🚀 How to Launch the Application

From the project root directory (`hr/`):

```powershell
# Using Python directly
python run.py
```

Or using the virtual environment:
```powershell
.\.venv\Scripts\python.exe run.py
```

The application runs at:
👉 **`http://localhost:8000`**

---

## 🎨 UI/UX Features & Interactive Capabilities

1. **Collapsible Modern Sidebar:**
   - Smooth CSS transitions (`transition: margin-left 0.28s cubic-bezier(0.16, 1, 0.3, 1)`).
   - Collapse toggle button `[<]`.
   - Floating reopen button `[>]` pinned at top-left so the sidebar can never disappear or be unreachable.
   - Live MySQL connection status pill (`🟢 Connected to MySQL: hr_workforce_db`).
   - Dynamic Department and Location dropdown filters with **Reset Filters** button.

2. **Collapsible AI Copilot Side-Chat Drawer:**
   - Accessible across **all screens** via the top-bar button `[💬 AI Copilot Drawer]`.
   - Slide-in animation from the right with quick inquiry chips.
   - Natural language Q&A, strategic recommendations, and expandable tool telemetry.
   - Explicit `[✕]` close button.

3. **5 Fully Interactive Views (SPA with zero page reloads):**
   - **📊 Executive Overview:** Reactive metric strip, Department headcount stacked bar chart, Exit drivers donut, and Department attrition table with progress bars.
   - **🤖 Predictive Flight Risk:** Prioritized high-risk table ($\ge 60\%$), interactive employee inspector (e.g. `E0087`), and 3-month departure forecast chart.
   - **🗓️ Attendance & Leaves:** Presence/Remote/Absent rate metrics, Attendance status donut, Leave consumption bar chart, and Statistical Z-Score outlier alerts ($Z \ge 2.0$).
   - **🚀 Onboarding & Mobility:** Onboarding completion progress bar, task status donut, and internal movement types horizontal bar chart.
   - **💬 AI HR Assistant:** Full-screen conversational AI suite with prompt catalog and tool inspection accordion.
