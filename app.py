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

# --- Route ---
if st.session_state.user is None:
    render_login_screen()
elif st.session_state.page == "app":
    render_initial_screen()
elif st.session_state.page == "live":
    render_live_screen()
