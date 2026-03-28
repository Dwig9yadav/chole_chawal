import os
import tempfile


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.webm", model: str | None = None) -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip() or os.getenv("VITE_GROQ_API_KEY", "").strip()
    if not audio_bytes:
        return ""

    if not api_key:
        return "STT fallback: no GROQ_API_KEY configured."

    suffix = ".webm"
    if "." in filename:
        suffix = "." + filename.rsplit(".", 1)[-1]

    selected_model = (model or "").strip() or "whisper-large-v3-turbo"
    fallback_models = [selected_model, "whisper-large-v3-turbo", "whisper-large-v3"]
    deduped_models = []
    for m in fallback_models:
        if m and m not in deduped_models:
            deduped_models.append(m)

    try:
        from groq import Groq

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            client = Groq(api_key=api_key)
            with open(tmp.name, "rb") as audio_file:
                for model_name in deduped_models:
                    try:
                        audio_file.seek(0)
                        transcript = client.audio.transcriptions.create(
                            model=model_name,
                            file=audio_file,
                        )
                        text = getattr(transcript, "text", "")
                        if text:
                            return text
                    except Exception:
                        continue
        return ""
    except Exception as exc:
        return f"STT failed: {exc}"
