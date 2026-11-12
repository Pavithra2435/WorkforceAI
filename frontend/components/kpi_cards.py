"""
================================================================================
KPI Metric Cards Component
Renders High-Impact Executive Workforce Statistics with Fluid Layout.
================================================================================
"""

import streamlit as st
from frontend.services.hr_api_client import fetch_executive_kpis


def render_executive_metric_strip(selected_depts=None, selected_locs=None):
    """
    Renders the 4-5 core workforce KPI cards in a responsive CSS Grid.
    """
    kpis = fetch_executive_kpis(selected_depts, selected_locs)
    
    total = kpis.get("total_headcount", 0)
    active = kpis.get("active_headcount", 0)
    exited = kpis.get("exited_count", 0)
    att_rate = kpis.get("attrition_rate_pct", 0.0)
    tenure = kpis.get("avg_active_tenure_years", 0.0)
    
    html = f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-title">Total Headcount</div>
            <div class="metric-value">{total:,}</div>
            <div class="metric-sub"><span style="color: #059669; font-weight: 700;">{active:,}</span> active roster</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Active Employees</div>
            <div class="metric-value">{active:,}</div>
            <div class="metric-sub"><span style="color: #64748B;">{((active / total) * 100 if total > 0 else 0):.1f}%</span> retention stability</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Company Attrition Rate</div>
            <div class="metric-value" style="color: #C2410C;">{att_rate:.1f}%</div>
            <div class="metric-sub"><span style="color: #DC2626; font-weight: 700;">{exited}</span> departures recorded</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Average Active Tenure</div>
            <div class="metric-value">{tenure:.1f} <span style="font-size: 1rem; font-weight: 600; color: #64748B;">Yrs</span></div>
            <div class="metric-sub">Workforce longevity index</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

