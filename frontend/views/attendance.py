"""
================================================================================
View: Attendance & Leave Governance
Working arrangements, presence compliance, leave utilization & statistical anomalies.
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.services.hr_api_client import (
    fetch_attendance_kpis,
    fetch_leave_analytics,
    fetch_attendance_anomalies
)
from frontend.styles.theme import (
    apply_clean_layout,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_TEXT_BODY
)


def render_attendance_view():
    """
    Renders the Attendance & Leave Governance screen.
    """
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div class="page-title">Attendance & Leave Governance</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-caption">Working arrangements, presence compliance, leave utilization patterns, and anomaly alerts.</div>', unsafe_allow_html=True)
    with col_t2:
        if not st.session_state.get("show_sidechat", False):
            if st.button("💬 AI Copilot Drawer", key="att_open_copilot", use_container_width=True):
                st.session_state["show_sidechat"] = True
                st.rerun()

    att_kpis = fetch_attendance_kpis()
    leave_kpis = fetch_leave_analytics()

    # 1. Metric Cards
    html_att = f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-title">Present Rate</div>
            <div class="metric-value">{att_kpis['present_pct']}%</div>
            <div class="metric-sub"><span style="color: #059669; font-weight: 700;">{att_kpis['present_count']:,}</span> days logged</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Remote Work Rate</div>
            <div class="metric-value">{att_kpis['remote_pct']}%</div>
            <div class="metric-sub">{att_kpis['remote_count']:,} remote days</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Absenteeism Rate</div>
            <div class="metric-value" style="color: {COLOR_PRIMARY};">{att_kpis['absenteeism_pct']}%</div>
            <div class="metric-sub">Avg {att_kpis['avg_daily_work_hours']} hrs/day logged</div>
        </div>
    </div>
    """
    st.markdown(html_att, unsafe_allow_html=True)

    # 2. Charts Section
    col_a1, col_a2 = st.columns([1, 1])

    with col_a1:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Presence Distribution</span>
                <span class="exec-card-badge">Daily Compliance</span>
            </div>
        """, unsafe_allow_html=True)

        att_proportions = [
            {"Status": "Present", "Pct": att_kpis["present_pct"]},
            {"Status": "Remote", "Pct": att_kpis["remote_pct"]},
            {"Status": "Absent", "Pct": att_kpis["absenteeism_pct"]},
            {"Status": "On Leave", "Pct": att_kpis["on_leave_pct"]}
        ]
        df_donut = pd.DataFrame(att_proportions)
        fig_donut = px.pie(
            df_donut,
            names="Status",
            values="Pct",
            hole=0.55,
            color="Status",
            color_discrete_map={
                "Present": "#475569",
                "Remote": "#94A3B8",
                "Absent": COLOR_PRIMARY,
                "On Leave": "#D97706"
            }
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut = apply_clean_layout(fig_donut, height=270)
        fig_donut.update_layout(showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_a2:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Leave Consumption by Type</span>
                <span class="exec-card-badge">Year-to-Date Days</span>
            </div>
        """, unsafe_allow_html=True)

        leave_types = leave_kpis.get("leave_by_type", [])
        if leave_types:
            df_lt = pd.DataFrame(leave_types)
            fig_lt = px.bar(
                df_lt,
                x="leave_type",
                y="total_leave_days",
                text="total_leave_days",
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig_lt.update_traces(textposition='outside')
            fig_lt = apply_clean_layout(fig_lt, height=270)
            fig_lt.update_layout(xaxis_title="", yaxis_title="Days", showlegend=False)
            st.plotly_chart(fig_lt, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Statistical Attendance Anomaly Detection Section
    st.markdown("""
    <div class="exec-card">
        <div class="exec-card-header">
            <span class="exec-card-title">Statistical Attendance Anomalies (Z-Score ≥ 2.0)</span>
            <span class="exec-card-badge">Outlier Detection</span>
        </div>
    """, unsafe_allow_html=True)

    anomalies_data = fetch_attendance_anomalies(2.0)
    outliers = anomalies_data if isinstance(anomalies_data, list) else anomalies_data.get("anomalous_records", [])

    if outliers:
        df_outliers = pd.DataFrame(outliers)
        df_outliers["Primary Anomaly Flag"] = df_outliers["anomaly_flags"].apply(
            lambda flags: flags[0] if isinstance(flags, list) and len(flags) > 0 else "Outlier pattern"
        )
        st.dataframe(
            df_outliers[["employee_id", "department", "absence_rate_pct", "mon_fri_absence_ratio_pct", "short_days_count", "Primary Anomaly Flag"]].rename(columns={
                "employee_id": "Employee ID",
                "department": "Department",
                "absence_rate_pct": "Absence Rate (%)",
                "mon_fri_absence_ratio_pct": "Mon/Fri Absence Ratio (%)",
                "short_days_count": "Short Workdays (<6h)"
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Absence Rate (%)": st.column_config.ProgressColumn(
                    "Absence Rate (%)",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0
                ),
                "Mon/Fri Absence Ratio (%)": st.column_config.ProgressColumn(
                    "Mon/Fri Absence Ratio (%)",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=100.0
                )
            }
        )
    else:
        st.info("No statistically significant attendance outliers detected at the Z ≥ 2.0 confidence threshold.")

    st.markdown("</div>", unsafe_allow_html=True)
