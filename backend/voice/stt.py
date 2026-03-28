import os
import tempfile
from typing import Optional


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip() or os.getenv("VITE_GROQ_API_KEY", "").strip()
    if not audio_bytes:
        return ""

    if not api_key:
        return "STT fallback: no GROQ_API_KEY configured."

    suffix = ".webm"
    if "." in filename:
        suffix = "." + filename.rsplit(".", 1)[-1]

    try:
        from groq import Groq

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            client = Groq(api_key=api_key)
            with open(tmp.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                )
        text = getattr(transcript, "text", "")
        return text or ""
    except Exception as exc:
        return f"STT failed: {exc}"
