"""
================================================================================
AI-Powered HR Workforce Insights Dashboard
Main Application Entrypoint & Modular Architecture Orchestrator
Technology: Streamlit, Plotly, Pandas, Scikit-Learn, MySQL
Design Architecture:
  - Model / Data Service Layer: frontend/services/hr_api_client.py
  - Presentation Views: frontend/views/ (Overview, Flight Risk, Attendance, Mobility, Copilot)
  - UI Components: frontend/components/ (Sidebar, Sidechat Drawer, KPI Cards)
  - Design System & Theme: frontend/styles/theme.py
================================================================================
"""

import os
import sys
import streamlit as st

# Ensure repository root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 1. Design System & Global Styles
from frontend.styles.theme import GLOBAL_CUSTOM_CSS

# 2. Reusable UI Components
from frontend.components.sidebar import render_sidebar
from frontend.components.sidechat import render_sidechat_drawer

# 3. Modular Presentation Views
from frontend.views.overview import render_overview_view
from frontend.views.flight_risk import render_flight_risk_view
from frontend.views.attendance import render_attendance_view
from frontend.views.mobility import render_mobility_view
from frontend.views.copilot_page import render_copilot_page


# ==============================================================================
# PAGE CONFIGURATION & ZERO-GAP THEME INJECTION
# ==============================================================================
st.set_page_config(
    page_title="WorkforceAI | HR Intelligence Platform",
    page_icon="https://img.icons8.com/ios-filled/50/C2410C/conference-call.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject zero-gap responsive CSS styling
st.markdown(GLOBAL_CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# APPLICATION ORCHESTRATION & ROUTING
# ==============================================================================
def main():
    # 1. Render Modern Sidebar & Retrieve Slicers
    nav_selection, selected_depts, selected_locs, show_sidechat = render_sidebar()

    # 2. Dynamic Layout Allocation (Collapsible Side-Chat Drawer)
    if show_sidechat and nav_selection != "AI HR Assistant":  
        main_col, sidechat_col = st.columns([2.3, 1.0])
    else:
        main_col = st.container()
        sidechat_col = None

    # 3. Render Active Analytical Screen
    with main_col:
        if nav_selection == "Executive Overview":
            render_overview_view(selected_depts, selected_locs)
        elif nav_selection == "Predictive Flight Risk":
            render_flight_risk_view()
        elif nav_selection == "Attendance & Leaves":
            render_attendance_view()
        elif nav_selection == "Onboarding & Mobility":
            render_mobility_view()
        elif nav_selection == "AI HR Assistant":
            render_copilot_page()

    # 4. Render Collapsible Side-Chat Drawer if Open
    if sidechat_col is not None:
        with sidechat_col:
            render_sidechat_drawer()


if __name__ == "__main__":
    main()
