"""
================================================================================
View: Predictive Flight Risk & Attrition Intelligence
Machine learning early-warning indicators to proactively detect flight risks.
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.services.hr_api_client import (
    fetch_flight_risk_roster,
    fetch_single_employee_risk,
    fetch_exit_forecast
)
from frontend.styles.theme import (
    apply_clean_layout,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_PRIMARY_DARK,
    COLOR_BORDER
)


def render_flight_risk_view():
    """
    Renders the Predictive Flight Risk screen.
    """
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div class="page-title">Predictive Flight Risk & Attrition Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-caption">Machine learning early-warning indicators to proactively detect flight risks and project departures.</div>', unsafe_allow_html=True)
    with col_t2:
        if not st.session_state.get("show_sidechat", False):
            if st.button("💬 AI Copilot Drawer", key="fr_open_copilot", use_container_width=True):
                st.session_state["show_sidechat"] = True
                st.rerun()

    roster = fetch_flight_risk_roster()
    num_high_risk = len(roster) if roster else 0
    forecast_res = fetch_exit_forecast(3)
    projected_q = forecast_res.get("total_quarterly_projected_exits", 0)

    # 1. Metric Cards for Flight Risk
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-title">Critical Flight Risks</div>
            <div class="metric-value" style="color: {COLOR_PRIMARY};">{num_high_risk}</div>
            <div class="metric-sub">Active staff with risk score ≥ 60%</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Model Confidence</div>
            <div class="metric-value">84.2%</div>
            <div class="metric-sub">ROC-AUC validation benchmark</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Quarterly Projected Exits</div>
            <div class="metric-value">{projected_q}</div>
            <div class="metric-sub">{forecast_res.get('trend_direction', 'Stable')} trajectory</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Strategic Retention Advisory Banner
    st.markdown(f"""
    <div class="rust-banner">
        <span style="color: {COLOR_PRIMARY}; font-weight: 800; margin-right: 6px;">RETENTION ADVISORY:</span>
        <b>{num_high_risk} key employees</b> are currently classified in the high flight-risk band.
        Targeted retention interventions and compensation reviews are advised for these staff members.
    </div>
    """, unsafe_allow_html=True)

    # 3. High-Risk Table inside Executive Card
    st.markdown("""
    <div class="exec-card">
        <div class="exec-card-header">
            <span class="exec-card-title">Prioritized Flight-Risk Roster</span>
            <span class="exec-card-badge">ML Probability ≥ 60%</span>
        </div>
    """, unsafe_allow_html=True)

    if roster:
        df_risk = pd.DataFrame(roster)
        df_risk["risk_pct"] = (df_risk["risk_score"] * 100).round(1)
        df_risk["top_driver"] = df_risk["top_contributing_factors"].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "Normal baseline"
        )
        
        st.dataframe(
            df_risk[["employee_id", "department", "designation", "risk_pct", "top_driver"]].rename(columns={
                "employee_id": "Employee ID",
                "department": "Department",
                "designation": "Role",
                "risk_pct": "Flight Risk (%)",
                "top_driver": "Primary Risk Driver"
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Flight Risk (%)": st.column_config.ProgressColumn(
                    "Flight Risk (%)",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0
                )
            }
        )
    else:
        st.info("No active employees currently exceed the 60% flight-risk threshold.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Two Columns: Single Employee Deep-Dive & Quarterly Forecast
    col_single, col_fc = st.columns([1, 1])

    with col_single:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Employee Risk Inspector</span>
                <span class="exec-card-badge">Individual Profile</span>
            </div>
        """, unsafe_allow_html=True)

        search_id = st.text_input(
            "Enter Employee ID:",
            value="E0087",
            placeholder="e.g. E0087, E0002, E0105",
            key="input_emp_search"
        ).strip()
        
        if search_id:
            emp_info = fetch_single_employee_risk(search_id)
            if "error" in emp_info:
                st.warning(emp_info["error"])
            else:
                score_pct = emp_info["risk_score"] * 100
                tier = emp_info["risk_tier"]
                tier_color = COLOR_PRIMARY if tier == "High" else ("#D97706" if tier == "Medium" else "#059669")
                factors = emp_info.get("top_contributing_factors", ["Normal baseline"])
                primary_factor = factors[0] if factors else "Normal baseline"
                
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1.5px solid {COLOR_BORDER}; border-radius: 8px; padding: 0.95rem; margin-top: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap; gap: 6px;">
                        <span style="font-size: 1rem; font-weight: 700; color: #0F172A;">{emp_info['employee_id']} — {emp_info.get('designation', '')}</span>
                        <span style="background: {COLOR_PRIMARY_LIGHT}; color: {tier_color}; font-weight: 700; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 4px; border: 1px solid #FED7AA;">
                            {tier} Risk ({score_pct:.1f}%)
                        </span>
                    </div>
                    <div style="font-size: 0.82rem; color: #334155; margin-bottom: 0.45rem;">
                        <b style="color: #0F172A;">Department:</b> {emp_info.get('department', 'N/A')} &nbsp;|&nbsp; <b style="color: #0F172A;">Status:</b> {emp_info.get('employment_status', 'Active')}
                    </div>
                    <div style="font-size: 0.82rem; color: #9A3412; background: #FFFBF7; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #FED7AA; border-left: 4px solid {COLOR_PRIMARY};">
                        <b style="color: {COLOR_PRIMARY_DARK};">Primary Retention Driver:</b> {primary_factor}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_fc:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Quarterly Exit Forecast</span>
                <span class="exec-card-badge">Next 3 Months</span>
            </div>
        """, unsafe_allow_html=True)

        mf = forecast_res.get("monthly_forecast", {})
        if mf:
            df_fc = pd.DataFrame([
                {"Month": m, "Projected Exits": float(val)} for m, val in mf.items()
            ])
            fig_fc = px.bar(
                df_fc,
                x="Month",
                y="Projected Exits",
                text="Projected Exits",
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig_fc.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_fc = apply_clean_layout(fig_fc, height=220)
            fig_fc.update_layout(yaxis_range=[0, max(df_fc["Projected Exits"]) * 1.35], showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_fc, use_container_width=True, config={"responsive": True, "displayModeBar": False})
            st.caption(f"Projected total: **{forecast_res['total_quarterly_projected_exits']} departures** next quarter ({forecast_res['trend_direction']} trend).")
        st.markdown("</div>", unsafe_allow_html=True)

