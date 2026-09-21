"""Live chat screen — runs the LangGraph test loop with live agent status (sidebar)."""
import difflib
import time
import streamlit as st
from agents import build_graph
from database import save_test_run


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AGENTS = [
    ("Attacker",    "⚔️", "#F09595", "#501313", "#E24B4A"),
    ("Target bot",  "🤖", "#B4B2A9", "#2C2C2A", "#5F5E5A"),
    ("Judge",       "⚖️", "#FAC775", "#412402", "#BA7517"),
    ("Defender",    "🛡️", "#85B7EB", "#042C53", "#378ADD"),
]


# ---------------------------------------------------------------------------
# Bubbles
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Live agent status panel (for sidebar)
# ---------------------------------------------------------------------------
def _render_status_panel(status_map: dict, timings: dict):
    rows = []
    for name, icon, color, bg, border in AGENTS:
        state = status_map.get(name, "waiting")

        if state == "thinking":
            badge = (
                f'<span style="color:{color};display:inline-flex;align-items:center;gap:6px;">'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{color};'
                f'animation:p 1s ease-in-out infinite;"></span>thinking…</span>'
            )
        elif state == "done":
            t = timings.get(name)
            time_str = f" · {t:.1f}s" if t is not None else ""
            badge = f'<span style="color:#97C459;">✅ done{time_str}</span>'
        elif state == "failed":
            badge = '<span style="color:#F09595;">❌ failed</span>'
        else:
            badge = '<span style="color:#5F5E5A;">○ waiting</span>'

        bg_active = bg if state != "waiting" else "#1A1A1A"
        border_active = border if state != "waiting" else "#2C2C2A"

        rows.append(
            f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                        background:{bg_active};
                        border:0.5px solid {border_active};
                        border-radius:10px;margin-bottom:6px;transition:all 0.3s ease;">
              <div style="flex:none;width:28px;height:28px;border-radius:50%;
                          background:{bg};color:{color};display:flex;align-items:center;
                          justify-content:center;font-size:15px;border:1.5px solid {border};">
                {icon}
              </div>
              <span style="color:#F1EFE8;font-size:13px;font-weight:500;">{name}</span>
              <span style="margin-left:auto;font-size:12px;">{badge}</span>
            </div>
            """
        )
    return "".join(rows)


# ---------------------------------------------------------------------------
# Diff renderer
# ---------------------------------------------------------------------------
def _prompt_diff(old: str, new: str) -> str:
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm="", n=1))

    html_parts = []
    for line in diff:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        safe = line.replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith("+"):
            html_parts.append(
                f'<div style="color:#97C459;background:#173404;padding:2px 6px;'
                f'border-radius:4px;margin:1px 0;">{safe}</div>'
            )
        elif line.startswith("-"):
            html_parts.append(
                f'<div style="color:#F09595;background:#501313;padding:2px 6px;'
                f'border-radius:4px;margin:1px 0;">{safe}</div>'
            )
        else:
            html_parts.append(
                f'<div style="color:#B4B2A9;padding:2px 6px;">{safe}</div>'
            )

    if not html_parts:
        return '<div style="color:#B4B2A9;font-size:12px;">No changes detected.</div>'
    return (
        '<div style="font-family:SF Mono,Fira Code,monospace;font-size:11px;line-height:1.5;">'
        + "".join(html_parts)
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Single round block
# ---------------------------------------------------------------------------
def _render_round_block(record: dict, patch: dict | None, round_num: int, category: str):
    st.markdown(f'<div class="rd">Round {round_num} · {category}</div>', unsafe_allow_html=True)

    _bubble("⚔️", "#F09595", "#A32D2D", "Attacker", "#F09595", record["probe"], mono=True)
    _bubble("🤖", "#B4B2A9", "#5F5E5A", "Target bot", "#B4B2A9", record["response"])

    sev_color = "#F09595" if record["verdict"] == "FAIL" else "#97C459"
    st.markdown(
        f"""
        <div style="background:#412402;border:0.5px solid #854F0B;border-radius:12px;
                    padding:10px 12px;margin:0 0 12px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:16px;">⚖️</span>
            <span style="font-size:13px;font-weight:500;color:#FAC775;">Judge verdict</span>
            <span style="margin-left:auto;font-size:11px;font-weight:500;padding:2px 8px;
                         border-radius:6px;background:#501313;color:{sev_color};">{record["verdict"]}</span>
            <span style="font-size:11px;font-weight:500;padding:2px 8px;border-radius:6px;
                         background:#633806;color:#FAC775;">{record["severity"]}</span>
          </div>
          <div style="font-size:13px;color:#F1EFE8;line-height:1.5;">{record["reason"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if patch:
        _bubble(
            "🛡️", "#85B7EB", "#185FA5", "Defender", "#85B7EB",
            f"Patched prompt with OWASP guardrails. Ref: {patch['category']}",
        )


# ---------------------------------------------------------------------------
# MAIN SCREEN
# ---------------------------------------------------------------------------
def render_live_screen():
    cfg = st.session_state.get("test_config") or {}
    system_prompt = cfg.get("system_prompt", "")
    categories = cfg.get("categories", [])
    total_rounds = cfg.get("rounds", 5)

    # ============================================================
    # SIDEBAR — live agent status panel
    # ============================================================
    with st.sidebar:
        st.markdown(
            '<div style="font-size:11px;color:#B4B2A9;text-transform:uppercase;'
            'letter-spacing:0.7px;margin-bottom:8px;">🛡️ Agent status</div>',
            unsafe_allow_html=True,
        )
        status_slot = st.empty()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:11px;color:#B4B2A9;text-transform:uppercase;'
            'letter-spacing:0.7px;margin-bottom:8px;">📊 Progress</div>',
            unsafe_allow_html=True,
        )
        progress_slot = st.empty()

        st.markdown("---")
        st.caption(
            f"**Rounds:** {total_rounds}\n\n"
            f"**Categories:** {len(categories)}\n\n"
            + "  \n".join(f"- {c}" for c in categories)
        )

    # ============================================================
    # MAIN AREA
    # ============================================================
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-size:16px;font-weight:500;color:#F1EFE8;">📡 Live test</span>
          <span style="font-size:12px;color:#B4B2A9;">Round {st.session_state.get('round_display', 1)} of {total_rounds}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_area = st.container()

    # ============================================================
    # FIRST RUN — execute graph
    # ============================================================
    if "graph_done" not in st.session_state:
        graph = build_graph()
        initial_state = {
            "system_prompt": system_prompt,
            "categories": categories,
            "total_rounds": total_rounds,
            "round": 1,
            "history": [],
            "failures": [],
            "prompt_patches": [],
            "current_probe": "",
            "current_response": "",
            "current_verdict": {},
            "finished": False,
        }

        config = {"recursion_limit": (total_rounds * 4) + 8}

        # --- Status bookkeeping ---
        status_map = {name: "waiting" for name, *_ in AGENTS}
        timings = {}
        completed_in_round = set()
        last_agent_started = time.time()

        def paint_status():
            with status_slot.container():
                st.markdown(
                    _render_status_panel(status_map, timings),
                    unsafe_allow_html=True,
                )

        def paint_progress(current_round):
            with progress_slot.container():
                pct = min(current_round / max(total_rounds, 1), 1.0)
                st.progress(pct)
                st.caption(f"{current_round} / {total_rounds} rounds")

        paint_status()
        paint_progress(0)

        # --- Stream the graph ---
        final_state = initial_state
        last_history_len = 0
        last_patch_len = 0
        last_round = 1

        for step_state in graph.stream(initial_state, stream_mode="values", config=config):
            final_state = step_state
            history = step_state.get("history", [])
            patches = step_state.get("prompt_patches", [])
            rnd = step_state.get("round", 1)

            # Round transition → reset status
            if rnd != last_round:
                completed_in_round = set()
                status_map = {name: "waiting" for name, *_ in AGENTS}
                last_round = rnd
                st.session_state.round_display = rnd
                paint_progress(rnd - 1)
                paint_status()

            probe = step_state.get("current_probe", "")
            response = step_state.get("current_response", "")
            new_verdict = len(history) > last_history_len
            new_patch = len(patches) > last_patch_len

            now = time.time()

            # Attacker → done when probe is set but no response yet
            if probe and not response and "Attacker" not in completed_in_round:
                timings["Attacker"] = now - last_agent_started
                status_map["Attacker"] = "done"
                completed_in_round.add("Attacker")
                status_map["Target bot"] = "thinking"
                last_agent_started = now
                paint_status()

            # Target bot → done when response is set but no verdict yet
            if response and not new_verdict and "Target bot" not in completed_in_round:
                timings["Target bot"] = now - last_agent_started
                status_map["Target bot"] = "done"
                completed_in_round.add("Target bot")
                status_map["Judge"] = "thinking"
                last_agent_started = now
                paint_status()

            # Judge → done when verdict is added
            if new_verdict and "Judge" not in completed_in_round:
                timings["Judge"] = now - last_agent_started
                status_map["Judge"] = "done"
                completed_in_round.add("Judge")
                status_map["Defender"] = "thinking"
                last_agent_started = now
                paint_status()

            # Defender → done when patch is added
            if new_patch and "Defender" not in completed_in_round:
                timings["Defender"] = now - last_agent_started
                status_map["Defender"] = "done"
                completed_in_round.add("Defender")
                paint_status()

            # Render new verdict only once
            if new_verdict:
                last_history_len = len(history)
                this_patch = None
                for p in patches:
                    if p["round"] == history[-1]["round"]:
                        this_patch = p
                        break
                with chat_area:
                    _render_round_block(
                        history[-1],
                        this_patch,
                        history[-1]["round"],
                        history[-1]["category"],
                    )

            last_patch_len = len(patches)

        # Final state
        for name, *_ in AGENTS:
            status_map[name] = "done"
        paint_status()
        paint_progress(total_rounds)

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

    # ============================================================
    # SUBSEQUENT RERUNS — redraw from cache
    # ============================================================
    else:
        final_state = st.session_state.get("final_state", {})

        with status_slot.container():
            done_map = {name: "done" for name, *_ in AGENTS}
            st.markdown(_render_status_panel(done_map, {}), unsafe_allow_html=True)

        with progress_slot.container():
            st.progress(1.0)
            st.caption(f"{total_rounds} / {total_rounds} rounds")

        hist = final_state.get("history", [])
        patches = final_state.get("prompt_patches", [])
        patch_by_round = {p["round"]: p for p in patches}

        with chat_area:
            for record in hist:
                _render_round_block(
                    record,
                    patch_by_round.get(record["round"]),
                    record["round"],
                    record.get("category", "—"),
                )

    # ============================================================
    # SUMMARY + PROMPT EVOLUTION REPORT
    # ============================================================
    st.markdown("---")

    hist = final_state.get("history", [])
    patches = final_state.get("prompt_patches", [])

    if hist:
        passes = sum(1 for h in hist if h["verdict"] == "PASS")
        rate = int(passes / len(hist) * 100)

        col1, col2, col3 = st.columns(3)
        col1.metric("Pass rate", f"{rate}%")
        col2.metric("Rounds", len(hist))
        col3.metric("Prompt version", f"v{1 + len(patches)}")

    if patches:
        st.markdown("### 🧬 Prompt evolution")
        st.caption("See exactly what the Defender changed after each failure.")

        for i, patch in enumerate(patches, start=1):
            with st.expander(
                f"Patch {i} · Round {patch['round']} · {patch['category']} (v{i} → v{i+1})",
                expanded=(i == len(patches)),
            ):
                st.markdown(
                    '<div style="font-size:12px;color:#B4B2A9;margin-bottom:8px;">'
                    "<b>Diff:</b> <span style='color:#97C459;'>green = added</span>, "
                    "<span style='color:#F09595;'>red = removed</span></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    _prompt_diff(patch["old_prompt"], patch["new_prompt"]),
                    unsafe_allow_html=True,
                )

        st.markdown("### 📜 Final hardened prompt")
        st.caption(f"v{1 + len(patches)} — copy this into your production prompt.")
        st.code(final_state.get("system_prompt", ""), language="markdown")
    else:
        st.info(
            "✅ No patches were needed — your original prompt resisted all probes. "
            "Prompt version stayed at v1."
        )
        st.markdown("### 📜 System prompt used")
        st.code(final_state.get("system_prompt", ""), language="markdown")

    if st.button("🔄 New test", use_container_width=True):
        for key in ["graph_done", "final_state", "test_config", "round_display"]:
            st.session_state.pop(key, None)
        st.session_state.page = "app"
        st.rerun()
