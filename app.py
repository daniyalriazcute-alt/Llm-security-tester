import os
import streamlit as st

# --- Load Groq key from Streamlit secrets (cloud) or env (local) ---
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

from database import init_db
from ui.styles import GLOBAL_CSS
from ui.login_screen import render_login_screen
from ui.initial_screen import render_initial_screen
from ui.live_chat_screen import render_live_screen

st.set_page_config(page_title="LLM Security Tester", page_icon="🛡️", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

init_db()

# --- Session state defaults ---
st.session_state.setdefault("page", "login")
st.session_state.setdefault("user", None)

# --- Top bar (only when logged in) ---
if st.session_state.get("user"):
    user = st.session_state.user
    col_l, col_user, col_logout = st.columns([8, 1.2, 1])

    with col_user:
        st.markdown(
            f'<div style="text-align:right;font-size:12px;color:#B4B2A9;padding-top:8px;white-space:nowrap;">'
            f'👤 {user.get("name", "User")}</div>',
            unsafe_allow_html=True,
        )

    with col_logout:
        if st.button("Logout", key="top_logout", use_container_width=True):
            for k in ["user", "page", "test_config", "graph_done",
                      "final_state", "round_display"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown("---")

# --- Routing ---
if st.session_state.user is None:
    render_login_screen()
elif st.session_state.page == "app":
    render_initial_screen()
elif st.session_state.page == "live":
    render_live_screen()
