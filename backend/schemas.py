"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ========== User Schemas ==========
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    bio: Optional[str]
    language: str
    theme: str
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# ========== Authentication Schemas ==========
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ========== Conversation Schemas ==========
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    role: str = Field(default="user")
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    tokens_used: int
    confidence: Optional[int]
    transcript: Optional[str]
    audio_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    model_used: Optional[str]
    message_count: int
    token_usage: int
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = []


# ========== File Upload Schemas ==========
class FileMetadata(BaseModel):
    original_filename: str
    file_size: int
    file_type: str
    created_at: datetime


class FileUploadResponse(BaseModel):
    id: str
    original_filename: str
    file_size: int
    file_type: str
    is_processed: bool
    extraction_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Settings Schemas ==========
class UserSettingsUpdate(BaseModel):
    voice_model: Optional[str] = None
    voice_speed: Optional[int] = Field(None, ge=0, le=200)
    voice_pitch: Optional[int] = Field(None, ge=0, le=200)
    temperature: Optional[int] = Field(None, ge=0, le=100)
    max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    context_memory: Optional[int] = Field(None, ge=1, le=50)
    data_retention_days: Optional[int] = None
    share_analytics: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    voice_model: str
    voice_speed: int
    voice_pitch: int
    temperature: int
    max_tokens: int
    context_memory: int
    data_retention_days: int
    share_analytics: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== Query Schemas ==========
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    use_voice: bool = False


class QueryResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    tokens_used: int
    processing_time: float


# ========== Analytics Schemas ==========
class AnalyticsEventCreate(BaseModel):
    event_name: str
    event_data: Optional[dict] = None
    session_id: Optional[str] = None


class AnalyticsEventResponse(BaseModel):
    id: str
    event_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Error Schemas ==========
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
