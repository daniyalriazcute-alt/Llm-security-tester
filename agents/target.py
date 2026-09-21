"""Target bot: the system under test."""
import os
import streamlit as st
from groq import Groq

MODELS = {
    "fast":     "llama-3.1-8b-instant",
    "balanced": "llama-3.1-8b-instant",
    "quality":  "openai/gpt-oss-120b",
}


def _model():
    choice = "balanced"
    try:
        choice = st.session_state.get("model_choice", "balanced")
    except Exception:
        pass
    return MODELS.get(choice, "llama-3.1-8b-instant")


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_target(system_prompt: str, user_message: str) -> str:
    try:
        resp = _client().chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=400,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        msg = str(e)
        if "rate_limit_exceeded" in msg or "429" in msg:
            return "[Rate limit — try again after midnight UTC or switch model to 'fast']"
        return f"[Target error: {e}]"
