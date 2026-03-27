# VoxAI - Real-Time Voice AI Agent with RAG + Actions

VoxAI is a Track-1 (AI/GenAI) project focused on one concrete use case:

Voice Study Assistant.

It supports:
- Voice-first Q&A on uploaded PDF notes
- RAG retrieval from local study documents
- Agent-style tool actions (web search, calculator, summarizer)
- Quiz mode for revision
- Text-to-speech response playback

## Project Architecture

Frontend (React + Vite)
-> Backend (FastAPI)
-> Router
   - RAG pipeline (PDF ingest + retrieve)
   - Agent tools (Search, Calculator, Summarizer)
   - LLM response generation
-> TTS audio output

## Repository Structure

- [backend/main.py](backend/main.py)
- [backend/routes/api.py](backend/routes/api.py)
- [backend/rag/ingest.py](backend/rag/ingest.py)
- [backend/rag/retrieve.py](backend/rag/retrieve.py)
- [backend/agent/tools.py](backend/agent/tools.py)
- [backend/agent/agent.py](backend/agent/agent.py)
- [backend/voice/stt.py](backend/voice/stt.py)
- [backend/voice/tts.py](backend/voice/tts.py)
- [src/App.jsx](src/App.jsx)
- [src/lib/api.js](src/lib/api.js)
- [src/index.css](src/index.css)
- [data/pdfs/.gitkeep](data/pdfs/.gitkeep)
- [data/embeddings/.gitkeep](data/embeddings/.gitkeep)

## Quick Start

## 1) Frontend setup

1. Install dependencies:

   npm install

2. Start frontend:

   npm run dev

Frontend runs on port 5173 by default.

## 2) Backend setup

1. Create a Python environment and install backend dependencies:

   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Optional env config:

   cp backend/.env.example backend/.env

3. Start backend:

   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

Backend runs on port 8000.

## Environment Variables

See [backend/.env.example](backend/.env.example).

- OPENAI_API_KEY: optional, enables cloud LLM answers + Whisper STT.
- OPENAI_MODEL: default gpt-4o-mini.

If keys are not set, VoxAI still runs with fallback behavior for demos.

## Demo Flow

1. Upload a PDF from your notes.
2. Ask a voice or text question:
   Explain operating system deadlock.
3. Ask a web tool query:
   Find best AI courses and summarize.
4. Trigger quiz mode:
   CPU scheduling quiz.
5. Listen to spoken response output.

## Notes

- RAG index is rebuilt on each PDF upload.
- Embeddings and index files are stored under data/embeddings.
- Voice recognition in frontend uses browser SpeechRecognition API.
# chole_chawal
