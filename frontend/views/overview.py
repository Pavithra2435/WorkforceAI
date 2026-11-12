"""
================================================================================
View: Executive Overview
Workforce distribution, attrition dynamics, and department benchmarking.
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.services.hr_api_client import (
    fetch_department_breakdown,
    fetch_attrition_insights
)
from frontend.components.kpi_cards import render_executive_metric_strip
from frontend.styles.theme import apply_clean_layout, COLOR_PRIMARY, COLOR_PRIMARY_LIGHT


def render_overview_view(selected_depts=None, selected_locs=None):
    """
    Renders the Executive Overview screen.
    """
    # Header Row with Page Title and Quick Copilot Drawer Button
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div class="page-title">Executive Overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-caption">Workforce distribution, attrition dynamics, and department structure.</div>', unsafe_allow_html=True)
    with col_t2:
        if not st.session_state.get("show_sidechat", False):
            if st.button("💬 AI Copilot Drawer", use_container_width=True):
                st.session_state["show_sidechat"] = True
                st.rerun()

    # 1. Top Executive Metric Strip
    render_executive_metric_strip(selected_depts, selected_locs)

    # 2. Filter Active Feedback Pill
    if selected_depts or selected_locs:
        filters_applied = []
        if selected_depts:
            filters_applied.append(f"Departments: {', '.join(selected_depts)}")
        if selected_locs:
            filters_applied.append(f"Locations: {', '.join(selected_locs)}")
        st.markdown(f"""
        <div style="display: inline-block; background-color: {COLOR_PRIMARY_LIGHT}; border: 1px solid #FED7AA; color: #9A3412; font-size: 0.8rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 6px; margin-bottom: 0.75rem;">
            <span style="color: {COLOR_PRIMARY}; font-weight: 700; margin-right: 4px;">FILTER ACTIVE:</span> {' | '.join(filters_applied)}
        </div>
        """, unsafe_allow_html=True)

    # Data Fetching
    dept_data = fetch_department_breakdown()
    df_dept = pd.DataFrame(dept_data)

    attr_data = fetch_attrition_insights()
    exit_reasons = attr_data.get("top_exit_reasons", [])

    # 3. Two Responsive Chart Cards
    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Department Headcount Structure</span>
                <span class="exec-card-badge">Active vs Exited</span>
            </div>
        """, unsafe_allow_html=True)

        if not df_dept.empty:
            df_melted = df_dept.melt(
                id_vars=["department"],
                value_vars=["active_count", "exited_count"],
                var_name="Status",
                value_name="Headcount"
            )
            df_melted["Status"] = df_melted["Status"].map({"active_count": "Active", "exited_count": "Exited"})

            fig_bar = px.bar(
                df_melted,
                x="department",
                y="Headcount",
                color="Status",
                barmode="group",
                color_discrete_map={"Active": "#475569", "Exited": COLOR_PRIMARY}
            )
            fig_bar = apply_clean_layout(fig_bar, height=270)
            fig_bar.update_layout(
                xaxis_title="",
                yaxis_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Primary Departure Drivers</span>
                <span class="exec-card-badge">Exit Reasons</span>
            </div>
        """, unsafe_allow_html=True)

        if exit_reasons:
            df_reasons = pd.DataFrame(exit_reasons)
            fig_donut = px.pie(
                df_reasons,
                names="exit_reason",
                values="exit_count",
                hole=0.55,
                color_discrete_sequence=["#C2410C", "#D97706", "#475569", "#64748B", "#94A3B8"]
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut = apply_clean_layout(fig_donut, height=270)
            fig_donut.update_layout(showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Department Performance & Attrition Table
    st.markdown("""
    <div class="exec-card">
        <div class="exec-card-header">
            <span class="exec-card-title">Department Attrition Benchmarking</span>
            <span class="exec-card-badge">Enterprise Breakdown</span>
        </div>
    """, unsafe_allow_html=True)

    if not df_dept.empty:
        df_table = df_dept.rename(columns={
            "department": "Department",
            "total_headcount": "Total Headcount",
            "active_count": "Active",
            "exited_count": "Exited",
            "attrition_rate": "Attrition Rate (%)",
            "avg_tenure_years": "Avg Tenure (Yrs)"
        })
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Attrition Rate (%)": st.column_config.ProgressColumn(
                    "Attrition Rate (%)",
                    format="%.1f%%",
                    min_value=0.0,
                    max_value=max(df_table["Attrition Rate (%)"].max(), 25.0)
                ),
                "Avg Tenure (Yrs)": st.column_config.NumberColumn(
                    "Avg Tenure (Yrs)",
                    format="%.2f"
                )
            }
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Strategic Takeaway Banner
    highest_dept = df_dept.iloc[0]["department"] if not df_dept.empty else "N/A"
    highest_rate = df_dept.iloc[0]["attrition_rate"] if not df_dept.empty else 0.0
    st.markdown(f"""
    <div class="rust-banner">
        <span style="font-weight: 800; color: {COLOR_PRIMARY};">STRATEGIC OBSERVATION:</span>
        <b>{highest_dept}</b> currently leads organizational departures with an attrition rate of <b>{highest_rate:.1f}%</b>.
        Primary voluntary drivers correlate with Career Growth and Compensation benchmarks.
    </div>
    """, unsafe_allow_html=True)

