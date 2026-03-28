import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


def _get_groq_api_key() -> str:
    # Support both backend-style and Vite-style env names to avoid deploy misconfig issues.
    return (
        os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("VITE_GROQ_API_KEY", "").strip()
    )


def _groq_chat(system_prompt: str, user_prompt: str, model: str | None = None) -> Optional[str]:
    api_key = _get_groq_api_key()
    logger.info(f"DEBUG: Checking Groq API key: {'SET' if api_key else 'NOT SET'}")
    if api_key:
        logger.info(f"DEBUG: API key starts with: {api_key[:10]}...")
    if not api_key:
        logger.warning("Groq API key not set (checked GROQ_API_KEY and VITE_GROQ_API_KEY)")
        return None

    try:
        configured_model = os.getenv("GROQ_MODEL", "").strip()
        model_candidates = [
            (model or "").strip(),
            configured_model,
            "gpt-oss-120b",
            "gpt-oss-20b",
            "qwen/qwen3-32b",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
        ]
        deduped_models = []
        for candidate in model_candidates:
            if candidate and candidate not in deduped_models:
                deduped_models.append(candidate)

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        for model_name in deduped_models:
            try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1024,
                }

                response = requests.post(url, json=payload, headers=headers, timeout=45)
                if response.status_code >= 400:
                    body = response.text[:500]
                    logger.warning(f"Groq model failed ({model_name}) status={response.status_code}: {body}")
                    continue

                data = response.json()
                text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
                if text:
                    return text
            except Exception as model_error:
                logger.warning(f"Groq model failed ({model_name}): {model_error}")

        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        return None


def generate_completion(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    response = _groq_chat(system_prompt, user_prompt, model=model)
    if response:
        return response

    # Offline-safe fallback for hackathon demos when API keys are absent.
    return (
        "I can still help, but Groq is not configured or available right now. "
        "Set GROQ_API_KEY (or VITE_GROQ_API_KEY) and optionally GROQ_MODEL in backend environment.\n\n"
        f"Your request was: {user_prompt[:350]}"
    )
