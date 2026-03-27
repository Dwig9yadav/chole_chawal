import io
from typing import Optional


def synthesize_speech_bytes(text: str) -> Optional[bytes]:
    if not text.strip():
        return None

    try:
        from gtts import gTTS

        audio_io = io.BytesIO()
        tts = gTTS(text=text[:2500], lang="en")
        tts.write_to_fp(audio_io)
        return audio_io.getvalue()
    except Exception:
        return None
