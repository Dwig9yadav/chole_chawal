from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class QuizRequest(BaseModel):
    topic: str = Field(..., min_length=2)


class TTSRequest(BaseModel):
    text: str
