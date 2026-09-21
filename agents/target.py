"""Target bot: the system under test."""
import os
from groq import Groq

MODEL = "openai/gpt-oss-20b"


def _client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_target(system_prompt: str, user_message: str) -> str:
    try:
        resp = _client().chat.completions.create(
            model=MODEL,
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
            return "[Rate limit — try again after midnight UTC]"
        return f"[Target error: {e}]"
