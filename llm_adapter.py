"""
Pluggable LLM adapter for the two genuinely generative stages (qualification
reasoning + email drafting). Deliberately built with zero hard dependency on
any single paid provider -- set ANY of the env vars below and it upgrades
automatically. With none set, it falls back to a clearly-labeled deterministic
template mode so the system still runs end-to-end (this directly answers the
"is it fair if some people have premium tools" question raised live in the
FlytBase session: the pipeline's *logic* doesn't depend on tool tier).

Supported (set one):
  ANTHROPIC_API_KEY   -> Claude
  OPENAI_API_KEY       -> GPT
  GOOGLE_API_KEY        -> Gemini (has a free tier)
  GROQ_API_KEY           -> Llama on Groq (free tier, fast)
"""
import os
import requests

MODE = "template"
_PROVIDER = None

if os.getenv("ANTHROPIC_API_KEY"):
    MODE, _PROVIDER = "live", "anthropic"
elif os.getenv("OPENAI_API_KEY"):
    MODE, _PROVIDER = "live", "openai"
elif os.getenv("GOOGLE_API_KEY"):
    MODE, _PROVIDER = "live", "gemini"
elif os.getenv("GROQ_API_KEY"):
    MODE, _PROVIDER = "live", "groq"


def generate(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
    """Returns generated text. In template mode, returns None so the caller's
    deterministic fallback (see each stage) produces the output instead --
    that fallback is real logic, not a canned string, it just doesn't do
    free-form language generation."""
    if MODE == "template":
        return None

    if _PROVIDER == "anthropic":
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-5-20250929", "max_tokens": max_tokens,
                  "system": system_prompt, "messages": [{"role": "user", "content": user_prompt}]},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]

    if _PROVIDER == "openai":
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
            json={"model": "gpt-4o-mini", "max_tokens": max_tokens,
                  "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    if _PROVIDER == "gemini":
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ['GOOGLE_API_KEY']}",
            json={"contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    if _PROVIDER == "groq":
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
            json={"model": "llama-3.3-70b-versatile", "max_tokens": max_tokens,
                  "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    return None
