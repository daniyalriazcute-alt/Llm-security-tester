"""Glowing auth screen: Sign in / Create account."""
import streamlit as st
from auth import register_user, login_user


def render_login_screen():
    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        st.markdown(
            """
            <div style="margin-bottom:8px;">
              <span style="font-size:15px;font-weight:600;color:#B5D4F4;letter-spacing:1px;">
                🛡️ AI OFFENSIVE SECURITY
              </span>
            </div>
            <div class="hero-title">Break your AI before<br>attackers do.</div>
            <div class="hero-sub">
              Four agents attack, judge, and harden your chatbot's system prompt.
              You get a written report of what leaked and how it was fixed.
            </div>
            <div style="font-size:14px;color:#85B7EB;font-style:italic;
                        border-left:3px solid #378ADD;padding:8px 14px;margin-bottom:20px;
                        background:rgba(55,138,221,0.06);border-radius:0 8px 8px 0;">
              “Every system prompt is one clever conversation away from becoming public.”
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- AI Offensive Security hero image ---
        st.markdown(
            """
            <div style="background:#0b0e13;border-radius:20px;border:1px solid #2a3440;
                        padding:12px;box-shadow:0 20px 40px -15px rgba(0,0,0,0.8),
                        0 0 30px rgba(55,138,221,0.1);margin-bottom:16px;">
              <img src="https://i.imgur.com/your-uploaded-image.png"
                   alt="AI Offensive Security — Attacker, Judge, Defender"
                   style="width:100%;border-radius:12px;display:block;">
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Badges ---
        st.markdown(
            """
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
              <span class="badge">OWASP LLM Top 10 2025</span>
              <span class="badge">Attacker, Judge, Defender</span>
              <span class="badge">Free to use</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)

        if "auth_tab" not in st.session_state:
            st.session_state.auth_tab = "signin"

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign in", use_container_width=True, key="tab_signin"):
                st.session_state.auth_tab = "signin"
                st.rerun()
        with c2:
            if st.button("Create account", use_container_width=True, key="tab_signup"):
                st.session_state.auth_tab = "signup"
                st.rerun()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        if st.session_state.auth_tab == "signin":
            st.markdown("### Welcome back")
            st.caption("Sign in to run your next security test.")
            email = st.text_input("Email", placeholder="name@company.com", key="si_email")
            password = st.text_input("Password", type="password",
                                     placeholder="Your password", key="si_pw")
            if st.button("Sign in →", use_container_width=True,
                         key="do_signin", type="primary"):
                user, err = login_user(email, password)
                if err:
                    st.error(err)
                else:
                    st.session_state.user = user
                    st.session_state.page = "app"
                    st.rerun()
            st.caption("New here? Click **Create account** above.")
        else:
            st.markdown("### Create your account")
            st.caption("Free forever. No credit card.")
            name = st.text_input("Name", placeholder="Ada Lovelace", key="su_name")
            email = st.text_input("Email", placeholder="name@company.com", key="su_email")
            password = st.text_input("Password", type="password",
                                     placeholder="Min. 8 characters", key="su_pw")
            if st.button("Create account →", use_container_width=True,
                         key="do_signup", type="primary"):
                ok, msg = register_user(name, email, password)
                if ok:
                    st.success(msg)
                    st.session_state.auth_tab = "signin"
                else:
                    st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)
