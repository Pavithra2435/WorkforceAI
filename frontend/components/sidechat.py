"""
================================================================================
Collapsible AI Copilot Side-Chat Drawer Component
Provides Real-Time Conversational AI Assistance Alongside Any Analytical Screen.
================================================================================
"""

import streamlit as st
from frontend.services.hr_api_client import call_ai_copilot, clean_for_json


def render_sidechat_drawer():
    """
    Renders the responsive side-chat drawer on the right side of the dashboard.
    """
    st.markdown("""
    <div class="sidechat-container">
        <div class="sidechat-header">
            <div class="sidechat-title">
                <span>AI Copilot</span>
                <span class="sidechat-badge">Online</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Close Drawer Button
    col_c1, col_c2 = st.columns([1, 1])
    with col_c2:
        if st.button("✕ Close Drawer", key="btn_close_sidechat", use_container_width=True):
            st.session_state["show_sidechat"] = False
            st.rerun()

    # Fast 1-Click Query Pills
    st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 0.25rem; margin-bottom: 0.35rem;'>Quick Inquiries</div>", unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    if q1.button("Attrition Rate", key="sq_attr", use_container_width=True):
        st.session_state["pending_sidechat_prompt"] = "Which department has highest attrition?"
    if q2.button("High Flight Risk", key="sq_risk", use_container_width=True):
        st.session_state["pending_sidechat_prompt"] = "Who are the high flight-risk employees?"

    # Ensure message thread exists
    if "sidechat_messages" not in st.session_state:
        st.session_state["sidechat_messages"] = [
            {
                "role": "assistant",
                "answer": "Hello. I am your HR AI Copilot. Ask me any workforce metric, flight-risk projection, or attrition insight.",
                "action": "Select a quick inquiry above or type a natural-language question below."
            }
        ]

    # Process pending quick prompt if triggered
    if "pending_sidechat_prompt" in st.session_state and st.session_state["pending_sidechat_prompt"]:
        prompt_text = st.session_state.pop("pending_sidechat_prompt")
        st.session_state["sidechat_messages"].append({"role": "user", "text": prompt_text})
        with st.spinner("Analyzing workforce database..."):
            response = call_ai_copilot(prompt_text)
            st.session_state["sidechat_messages"].append({
                "role": "assistant",
                "answer": response.get("natural_language_answer", "No response generated."),
                "action": response.get("recommended_action", ""),
                "tool_used": response.get("tool_used", "N/A"),
                "intent": response.get("intent", "N/A"),
                "raw_data": clean_for_json(response.get("raw_data", {}))
            })

    # Display conversation history (capped at last 5 for drawer responsiveness)
    chat_box = st.container(height=360)
    with chat_box:
        for msg in st.session_state["sidechat_messages"][-6:]:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{msg["text"]}</div>', unsafe_allow_html=True)
            else:
                answer = msg.get("answer", "")
                action = msg.get("action", "")
                tool = msg.get("tool_used", None)
                raw = msg.get("raw_data", None)

                content_html = f"""
                <div class="chat-bubble-bot">
                    <div>{answer}</div>
                """
                if action:
                    content_html += f"""
                    <div class="bot-action-box">
                        <b>Strategic Recommendation:</b> {action}
                    </div>
                    """
                content_html += "</div>"
                st.markdown(content_html, unsafe_allow_html=True)

                if tool and raw:
                    with st.expander(f"Tool: {tool}", expanded=False):
                        st.json(raw)

    # Input Box
    user_input = st.chat_input("Ask HR Copilot...", key="sidechat_input_field")
    if user_input:
        st.session_state["sidechat_messages"].append({"role": "user", "text": user_input})
        with st.spinner("Analyzing..."):
            response = call_ai_copilot(user_input)
            st.session_state["sidechat_messages"].append({
                "role": "assistant",
                "answer": response.get("natural_language_answer", "No response generated."),
                "action": response.get("recommended_action", ""),
                "tool_used": response.get("tool_used", "N/A"),
                "intent": response.get("intent", "N/A"),
                "raw_data": clean_for_json(response.get("raw_data", {}))
            })
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

