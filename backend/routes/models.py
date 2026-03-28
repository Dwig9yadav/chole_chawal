from pydantic import BaseModel, Field


class ModelRouting(BaseModel):
    reasoning_model: str | None = None
    tool_model: str | None = None
    text_model: str | None = None
    vision_model: str | None = None
    multilingual_model: str | None = None
    stt_model: str | None = None
    tts_model: str | None = None
    tts_voice: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    model_routing: ModelRouting | None = None


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=2)
    model_routing: ModelRouting | None = None


class TTSRequest(BaseModel):
    text: str
    model: str | None = None
    voice: str | None = None
