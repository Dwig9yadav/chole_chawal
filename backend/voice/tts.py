import io
import os
from typing import Optional

import requests


def _groq_tts(text: str, model: str | None = None, voice: str | None = None) -> Optional[bytes]:
    api_key = os.getenv("GROQ_API_KEY", "").strip() or os.getenv("VITE_GROQ_API_KEY", "").strip()
    if not api_key:
        return None

    selected_model = (model or "").strip() or os.getenv("GROQ_TTS_MODEL", "").strip() or "playai-tts"
    selected_voice = (voice or "").strip() or os.getenv("GROQ_TTS_VOICE", "").strip() or "Arista-PlayAI"

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": selected_model,
                "voice": selected_voice,
                "input": text[:2500],
                "response_format": "mp3",
            },
            timeout=45,
        )
        if response.status_code >= 400:
            return None
        return response.content
    except Exception:
        return None


def synthesize_speech_bytes(text: str, model: str | None = None, voice: str | None = None) -> Optional[bytes]:
    if not text.strip():
        return None

    groq_audio = _groq_tts(text, model=model, voice=voice)
    if groq_audio:
        return groq_audio

    try:
        from gtts import gTTS

        audio_io = io.BytesIO()
        tts = gTTS(text=text[:2500], lang="en")
        tts.write_to_fp(audio_io)
        return audio_io.getvalue()
    except Exception:
        return None
