from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from backend.agent.agent import generate_quiz, run_agent
from backend.rag.ingest import PDF_DIR, rebuild_index
from backend.rag.retrieve import retrieve_docs
from backend.routes.models import QueryRequest, QuizRequest, TTSRequest
from backend.voice.stt import transcribe_audio_bytes
from backend.voice.tts import synthesize_speech_bytes

router = APIRouter(prefix="/api", tags=["voxai"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "VoxAI backend"}


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PDF_DIR / file.filename

    content = await file.read()
    out_path.write_bytes(content)

    ingest_info = rebuild_index()
    return {
        "message": "PDF uploaded and indexed",
        "file": file.filename,
        "index": ingest_info,
    }


@router.post("/query")
def query(payload: QueryRequest):
    docs = retrieve_docs(payload.query, k=4)
    result = run_agent(payload.query, docs, payload.model_routing)
    return {
        "query": payload.query,
        "answer": result["answer"],
        "sources": result["sources"],
        "tool_calls": result["tool_calls"],
        "models": result.get("models", {}),
    }


@router.post("/quiz")
def quiz(payload: QuizRequest):
    docs = retrieve_docs(payload.topic, k=6)
    return generate_quiz(payload.topic, docs, payload.model_routing)


@router.post("/stt")
async def stt(file: UploadFile = File(...), model: str | None = Form(default=None)):
    audio = await file.read()
    text = transcribe_audio_bytes(audio, filename=file.filename, model=model)
    return {"text": text}


@router.post("/tts")
def tts(payload: TTSRequest):
    audio_bytes = synthesize_speech_bytes(payload.text, model=payload.model, voice=payload.voice)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="TTS failed. Check internet or gTTS install.")
    return Response(content=audio_bytes, media_type="audio/mpeg")
