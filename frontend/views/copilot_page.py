"""
================================================================================
View: Full-Screen AI HR Assistant & Tool-Calling Copilot
Dedicated Conversational Intelligence Suite Grounded in MySQL and ML Services.
================================================================================
"""

import streamlit as st
from frontend.services.hr_api_client import call_ai_copilot, clean_for_json
from frontend.styles.theme import (
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_PRIMARY_BORDER,
    COLOR_PRIMARY_DARK
)


def render_copilot_page():
    """
    Renders the dedicated full-screen AI Assistant interface.
    """
    st.markdown('<div class="page-title">AI HR Assistant & Tool-Calling Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-caption">Ask natural-language workforce queries grounded directly in verified MySQL database records and Machine Learning models.</div>', unsafe_allow_html=True)

    # 4 Quick Suggestion Chips
    st.markdown("<p style='font-size: 0.74rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;'>Suggested Inquiries</p>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    if col_p1.button("Highest Attrition Dept", key="cp_p1", use_container_width=True):
        st.session_state["pending_copilot_prompt"] = "Which department has highest attrition?"

    if col_p2.button("High Flight-Risk Staff", key="cp_p2", use_container_width=True):
        st.session_state["pending_copilot_prompt"] = "Who are the high flight-risk employees?"

    if col_p3.button("Next Quarter Forecast", key="cp_p3", use_container_width=True):
        st.session_state["pending_copilot_prompt"] = "What is the exit forecast for next quarter?"

    if col_p4.button("Attendance Anomalies", key="cp_p4", use_container_width=True):
        st.session_state["pending_copilot_prompt"] = "Show attendance anomalies."

    st.markdown("<div style='margin-bottom: 0.85rem;'></div>", unsafe_allow_html=True)

    # Ensure conversation state exists
    if "copilot_messages" not in st.session_state:
        st.session_state["copilot_messages"] = [
            {
                "role": "assistant",
                "content": "Hello. I am your HR Workforce AI Copilot. How can I assist you with workforce analytics, flight risks, or attendance patterns today?",
                "tool_used": None,
                "intent": None,
                "raw_data": None,
                "action": "Select a prompt above or ask a specific workforce question in the input bar below."
            }
        ]

    # Process pending prompt if triggered
    if "pending_copilot_prompt" in st.session_state and st.session_state["pending_copilot_prompt"]:
        prompt_text = st.session_state.pop("pending_copilot_prompt")
        st.session_state["copilot_messages"].append({"role": "user", "content": prompt_text})
        with st.spinner("Analyzing verified workforce database and ML models..."):
            response = call_ai_copilot(prompt_text)
            st.session_state["copilot_messages"].append({
                "role": "assistant",
                "content": response.get("natural_language_answer", "No response generated."),
                "action": response.get("recommended_action", ""),
                "tool_used": response.get("tool_used", "N/A"),
                "intent": response.get("intent", "N/A"),
                "raw_data": clean_for_json(response.get("raw_data", {}))
            })

    # Render Conversation Messages
    for msg in st.session_state["copilot_messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
                <div style="background-color: {COLOR_PRIMARY_LIGHT}; border: 1.5px solid {COLOR_PRIMARY_BORDER}; border-radius: 12px 12px 2px 12px; padding: 0.75rem 1.05rem; max-width: 78%; font-size: 0.88rem; color: {COLOR_PRIMARY_DARK}; font-weight: 500; line-height: 1.45; box-shadow: 0 2px 6px rgba(194, 65, 12, 0.08);">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            answer = msg.get("content", "")
            action = msg.get("action", "")
            tool = msg.get("tool_used", None)
            raw = msg.get("raw_data", None)

            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 0.85rem;">
                <div style="background-color: #FFFFFF; border: 1.5px solid #E2E8F0; border-left: 4.5px solid {COLOR_PRIMARY}; border-radius: 2px 12px 12px 12px; padding: 0.95rem 1.15rem; max-width: 90%; font-size: 0.88rem; color: #1E293B; line-height: 1.5; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                    <div style="font-size: 0.72rem; font-weight: 700; color: {COLOR_PRIMARY}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">Verified Workforce Intelligence</div>
                    <div>{answer}</div>
                    {f'<div style="background-color: #FFFBF7; border: 1px solid #FED7AA; border-left: 3px solid {COLOR_PRIMARY}; border-radius: 6px; padding: 0.55rem 0.85rem; margin-top: 0.65rem; font-size: 0.82rem; color: #9A3412;"><b>Strategic HR Recommendation:</b> {action}</div>' if action else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if tool and raw:
                with st.expander(f"Tool Execution Inspection: {tool}", expanded=False):
                    st.caption("Backend payload returned by database/ML engines:")
                    st.json(raw)

    # Chat Input
    query_input = st.chat_input("Ask a question about headcount, flight risk, staff attrition, or attendance...")
    if query_input:
        st.session_state["copilot_messages"].append({"role": "user", "content": query_input})
        with st.spinner("Executing controlled tools & synthesizing insights..."):
            response = call_ai_copilot(query_input)
            st.session_state["copilot_messages"].append({
                "role": "assistant",
                "content": response.get("natural_language_answer", "No response generated."),
                "action": response.get("recommended_action", ""),
                "tool_used": response.get("tool_used", "N/A"),
                "intent": response.get("intent", "N/A"),
                "raw_data": clean_for_json(response.get("raw_data", {}))
            })
        st.rerun()

