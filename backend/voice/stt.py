import os
import tempfile
from typing import Optional


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not audio_bytes:
        return ""

    if not api_key:
        return "STT fallback: no OPENAI_API_KEY configured."

    suffix = ".webm"
    if "." in filename:
        suffix = "." + filename.rsplit(".", 1)[-1]

    try:
        from openai import OpenAI

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            client = OpenAI(api_key=api_key)
            with open(tmp.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )
        text = getattr(transcript, "text", "")
        return text or ""
    except Exception as exc:
        return f"STT failed: {exc}"
