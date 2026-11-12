"""
================================================================================
View: Onboarding & Internal Workforce Mobility
New-hire onboarding velocity and internal career transitions across departments.
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.services.hr_api_client import fetch_onboarding_mobility
from frontend.styles.theme import (
    apply_clean_layout,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT
)


def render_mobility_view():
    """
    Renders the Onboarding & Career Mobility screen.
    """
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div class="page-title">Onboarding & Internal Workforce Mobility</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-caption">New-hire onboarding velocity and internal career transitions across departments.</div>', unsafe_allow_html=True)
    with col_t2:
        if not st.session_state.get("show_sidechat", False):
            if st.button("💬 AI Copilot Drawer", key="mob_open_copilot", use_container_width=True):
                st.session_state["show_sidechat"] = True
                st.rerun()

    onb_kpis = fetch_onboarding_mobility()
    completion_pct = onb_kpis.get("onboarding_completion_pct", 0.0)
    total_mov = onb_kpis.get("total_movements", 0)

    # 1. Metric Cards
    html_onb = f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-title">Onboarding Task Completion</div>
            <div class="metric-value">{completion_pct:.1f}%</div>
            <div class="metric-sub">{onb_kpis.get('total_onboarding_tasks', 0):,} tasks tracked</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Internal Career Transitions</div>
            <div class="metric-value">{total_mov}</div>
            <div class="metric-sub">Promotions, transfers & role updates</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Mobility Health Index</div>
            <div class="metric-value" style="color: #059669;">Optimal</div>
            <div class="metric-sub">Healthy internal promotion velocity</div>
        </div>
    </div>
    """
    st.markdown(html_onb, unsafe_allow_html=True)
    st.progress(min(max(completion_pct / 100.0, 0.0), 1.0))

    st.markdown("<div style='margin-bottom: 0.85rem;'></div>", unsafe_allow_html=True)

    # 2. Charts Section
    col_o1, col_o2 = st.columns([1, 1])

    with col_o1:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Onboarding Task Status</span>
                <span class="exec-card-badge">Completion Health</span>
            </div>
        """, unsafe_allow_html=True)

        onb_breakdown = onb_kpis.get("onboarding_status_breakdown", [])
        if onb_breakdown:
            df_onb = pd.DataFrame(onb_breakdown)
            fig_onb = px.pie(
                df_onb,
                names="task_status",
                values="task_count",
                hole=0.55,
                color="task_status",
                color_discrete_map={"Completed": "#475569", "Pending": COLOR_PRIMARY}
            )
            fig_onb.update_traces(textposition='inside', textinfo='percent+label')
            fig_onb = apply_clean_layout(fig_onb, height=270)
            fig_onb.update_layout(showlegend=False)
            st.plotly_chart(fig_onb, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_o2:
        st.markdown("""
        <div class="exec-card">
            <div class="exec-card-header">
                <span class="exec-card-title">Internal Movement Types</span>
                <span class="exec-card-badge">Career Mobility</span>
            </div>
        """, unsafe_allow_html=True)

        mob_list = onb_kpis.get("movements_breakdown", [])
        if mob_list:
            df_mob = pd.DataFrame(mob_list).sort_values("movement_count", ascending=True)
            fig_mob = px.bar(
                df_mob,
                x="movement_count",
                y="movement_type",
                orientation="h",
                text="movement_count",
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig_mob.update_traces(textposition='outside')
            fig_mob = apply_clean_layout(fig_mob, height=270)
            fig_mob.update_layout(xaxis_title="", yaxis_title="", showlegend=False)
            st.plotly_chart(fig_mob, use_container_width=True, config={"responsive": True, "displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Strategic Mobility Summary
    st.markdown(f"""
    <div class="rust-banner">
        <span style="font-weight: 800; color: {COLOR_PRIMARY};">ONBOARDING READINESS:</span>
        New-hire onboarding task completion stands at <b>{completion_pct:.1f}%</b>.
        A total of <b>{total_mov} internal transitions</b> have been processed, promoting internal talent retention.
    </div>
    """, unsafe_allow_html=True)

