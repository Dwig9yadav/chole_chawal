"""Database models for VoxAI"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # Settings
    language = Column(String(10), default="en")
    theme = Column(String(20), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    files = relationship("UploadedFile", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserSettings(Base):
    """User preferences and settings"""
    __tablename__ = "user_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Voice settings
    voice_model = Column(String(50), default="neural")
    voice_speed = Column(Integer, default=100)  # 0-200
    voice_pitch = Column(Integer, default=100)  # 0-200
    
    # AI settings
    temperature = Column(Integer, default=70)  # 0-100
    max_tokens = Column(Integer, default=2000)
    context_memory = Column(Integer, default=10)  # Number of previous messages to remember
    
    # Privacy
    data_retention_days = Column(Integer, default=90)
    share_analytics = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")


class ConversationStatus(str, enum.Enum):
    """Conversation status enum"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(Base):
    """Conversation/Chat session"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    
    # Metadata
    model_used = Column(String(100))
    system_prompt = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    
    # Stats
    message_count = Column(Integer, default=0)
    token_usage = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.title}>"


class Message(Base):
    """Message in a conversation"""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Message metadata
    tokens_used = Column(Integer, default=0)
    confidence = Column(Integer)  # 0-100 for assistant responses
    
    # Voice/Transcription
    transcript = Column(Text)  # Original transcription if voice input
    audio_url = Column(String(500))  # URL to audio file if voice message
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.role}>"


class UploadedFile(Base):
    """Uploaded file metadata"""
    __tablename__ = "uploaded_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(50))  # MIME type
    
    # Processing
    is_processed = Column(Boolean, default=False)
    extraction_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    extracted_text = Column(Text)
    file_metadata = Column("metadata", JSON)  # Additional extracted metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="files")
    
    def __repr__(self):
        return f"<UploadedFile {self.original_filename}>"


class AnalyticsEvent(Base):
    """Analytics event tracking"""
    __tablename__ = "analytics_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    
    event_name = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON)
    session_id = Column(String(36), index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AnalyticsEvent {self.event_name}>"
