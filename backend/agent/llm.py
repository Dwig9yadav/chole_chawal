import os
import json
import urllib.request
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def _groq_chat(system_prompt: str, user_prompt: str) -> Optional[str]:
    api_key = os.getenv("VITE_GROQ_API_KEY", "").strip()
    if not api_key:
        logger.warning("VITE_GROQ_API_KEY not set in environment")
        return None

    try:
        from groq import Groq

        model = "llama-3.1-70b-versatile"  # Groq's powerful general-purpose model
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return completion.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        return None


def generate_completion(system_prompt: str, user_prompt: str) -> str:
    response = _groq_chat(system_prompt, user_prompt)
    if response:
        return response

    # Offline-safe fallback for hackathon demos when API keys are absent.
    return (
        "I can still help, but no Groq API key is configured. "
        "Set VITE_GROQ_API_KEY in backend environment for full quality answers.\n\n"
        f"Your request was: {user_prompt[:350]}"
    )
