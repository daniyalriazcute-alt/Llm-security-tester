"""Live chat screen — runs the LangGraph test loop."""
import streamlit as st
from agents import build_graph
from database import save_test_run


def _bubble(icon, color, border, who, who_color, body, mono=False, pulse=False):
    body_class = "mono" if mono else ""
    body_content = f'<span class="pulse">{body}</span>' if pulse else body
    st.markdown(
        f"""
        <div class="row">
          <div class="av" style="background:{color}22;color:{color};
               border:1.5px solid {border};font-size:18px;display:flex;align-items:center;justify-content:center;">{icon}</div>
          <div style="min-width:0;flex:1;">
            <div class="who" style="color:{who_color};font-size:12px;margin-bottom:3px;">{who}</div>
            <div class="bub {body_class}" style="border:0.5px solid {border};border-radius:12px;
                 padding:8px 12px;font-size:13px;line-height:1.5;color:#F1EFE8;background:#2C2C2A;">{body_content}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_live_screen():
    cfg = st.session_state.get("test_config") or {}
    system_prompt = cfg.get("system_prompt", "")
    categories = cfg.get("categories", [])
    total_rounds = cfg.get("rounds", 5)

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:16px;font-weight:500;color:#F1EFE8;">📡 Live test</span>
          <span style="font-size:12px;color:#B4B2A9;">Rounds: {total_rounds}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_area = st.container()
    progress = st.progress(0.0)

    if "graph_done" not in st.session_state:
        graph = build_graph()
        initial_state = {
            "system_prompt": system_prompt,
            "categories": categories,
            "total_rounds": total_rounds,
            "round": 1,
            "history": [],
            "failures": [],
            "current_probe": "",
            "current_response": "",
            "current_verdict": {},
            "finished": False,
        }

        final_state = initial_state
        for step_state in graph.stream(initial_state, stream_mode="values"):
            final_state = step_state
            history = step_state.get("history", [])
            rnd = step_state.get("round", 1)
            progress.progress(min(rnd / max(total_rounds, 1), 1.0))
            with chat_area:
                cat = categories[(rnd - 1) % len(categories)] if categories else "—"
                st.markdown(f'<div class="rd">Round {rnd} · {cat}</div>', unsafe_allow_html=True)
                if history:
                    last = history[-1]
                    _bubble("⚔️", "#F09595", "#A32D2D", "Attacker", "#F09595", last["probe"], mono=True)
                    _bubble("🤖", "#B4B2A9", "#5F5E5A", "Target bot", "#B4B2A9", last["response"])
                    # Judge verdict
                    sev_color = "#F09595" if last["verdict"] == "FAIL" else "#97C459"
                    st.markdown(
                        f"""
                        <div style="background:#412402;border:0.5px solid #854F0B;border-radius:12px;
                                    padding:10px 12px;margin:0 0 12px;">
                          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                            <span style="font-size:16px;">⚖️</span>
                            <span style="font-size:13px;font-weight:500;color:#FAC775;">Judge verdict</span>
                            <span style="margin-left:auto;font-size:11px;font-weight:500;padding:2px 8px;
                                         border-radius:6px;background:#501313;color:{sev_color};">{last["verdict"]}</span>
                            <span style="font-size:11px;font-weight:500;padding:2px 8px;border-radius:6px;
                                         background:#633806;color:#FAC775;">{last["severity"]}</span>
                          </div>
                          <div style="font-size:13px;color:#F1EFE8;line-height:1.5;">{last["reason"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if last["verdict"] == "FAIL":
                        _bubble("🛡️", "#85B7EB", "#185FA5", "Defender", "#85B7EB",
                                "Patched prompt with OWASP guardrails. Ref: " + last["category"])

        st.session_state.graph_done = True
        st.session_state.final_state = final_state

        # Save run
        user = st.session_state.get("user") or {}
        if user.get("id"):
            hist = final_state.get("history", [])
            passes = sum(1 for h in hist if h["verdict"] == "PASS")
            rate = (passes / len(hist) * 100) if hist else 0
            try:
                save_test_run(user["id"], system_prompt, categories, total_rounds, rate)
            except Exception:
                pass

    else:
        # Redraw final state on re-runs
        final_state = st
