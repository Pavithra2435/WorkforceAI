"""
================================================================================
Sidebar Navigation & Filter Component
Provides Brand Identity, Navigation, Global Slicers, and Side-Chat Drawer Toggle.
================================================================================
"""

import streamlit as st
from frontend.services.hr_api_client import fetch_filter_options, DB_NAME


def render_sidebar():
    """
    Renders the modern left sidebar and returns active filter state and page selection.
    """
    with st.sidebar:
        # 1. Brand Logo & Title
        st.markdown("""
        <div class="brand-box">
            <div class="brand-logo">W</div>
            <div>
                <div class="brand-title">WorkforceAI</div>
                <div class="brand-sub">HR Intelligence Platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Database Connection Status Pill
        st.markdown(f"""
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>Connected to MySQL: <b>{DB_NAME}</b></span>
        </div>
        """, unsafe_allow_html=True)

        # 3. Navigation Menu
        st.markdown('<div class="sidebar-section-header">Executive Views</div>', unsafe_allow_html=True)
        nav_options = [
            "Executive Overview",
            "Predictive Flight Risk",
            "Attendance & Leaves",
            "Onboarding & Mobility",
            "AI HR Assistant"
        ]

        # Sync with session state if needed
        default_index = 0
        if "current_page" in st.session_state and st.session_state["current_page"] in nav_options:
            default_index = nav_options.index(st.session_state["current_page"])

        nav_selection = st.radio(
            "Navigation Menu",
            options=nav_options,
            index=default_index,
            label_visibility="collapsed"
        )
        st.session_state["current_page"] = nav_selection

        st.markdown("<div style='margin-top: 0.85rem;'></div>", unsafe_allow_html=True)

        # 4. Collapsible Side-Chat Drawer Toggle (Available across all screens!)
        st.markdown('<div class="sidebar-section-header">Intelligent Assistant</div>', unsafe_allow_html=True)
        
        if "show_sidechat" not in st.session_state:
            st.session_state["show_sidechat"] = False

        show_sidechat = st.toggle(
            "AI Copilot Side-Chat Drawer",
            value=st.session_state["show_sidechat"],
            help="Toggle the interactive Generative AI assistant panel on the right side of any screen."
        )
        st.session_state["show_sidechat"] = show_sidechat

        st.markdown("<div style='margin-top: 0.85rem;'></div>", unsafe_allow_html=True)

        # 5. Global Department & Location Filters
        st.markdown('<div class="sidebar-section-header">Global Scope Filters</div>', unsafe_allow_html=True)
        all_depts, all_locs = fetch_filter_options()

        if "filter_depts" not in st.session_state:
            st.session_state["filter_depts"] = []
        if "filter_locs" not in st.session_state:
            st.session_state["filter_locs"] = []

        selected_depts = st.multiselect(
            "Filter Department",
            options=all_depts,
            default=st.session_state["filter_depts"],
            placeholder="All Departments"
        )
        st.session_state["filter_depts"] = selected_depts

        selected_locs = st.multiselect(
            "Filter Location",
            options=all_locs,
            default=st.session_state["filter_locs"],
            placeholder="All Locations"
        )
        st.session_state["filter_locs"] = selected_locs

        if selected_depts or selected_locs:
            if st.button("Reset All Filters", use_container_width=True):
                st.session_state["filter_depts"] = []
                st.session_state["filter_locs"] = []
                st.rerun()

        # Footer info
        st.markdown("""
        <div style="margin-top: 2rem; padding-top: 0.85rem; border-top: 1px solid #E2E8F0; font-size: 0.72rem; color: #94A3B8;">
            <b>WorkforceAI Engine v2.4</b><br>
            Multi-Tier GenAI & ML Pipeline
        </div>
        """, unsafe_allow_html=True)

    return nav_selection, selected_depts, selected_locs, show_sidechat

