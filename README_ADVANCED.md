# VoxAI - Advanced Voice AI Assistant v2.0

A comprehensive, production-ready voice AI assistant with real-time features, multi-user support, and enterprise-grade architecture.

## 🎯 Features

### Core Features
- 🎤 **Advanced Voice Processing** - Real-time STT/TTS with multiple voices
- 🤖 **Intelligent AI** - Multi-model LLM support (OpenAI, Groq)
- 📚 **RAG System** - Document ingestion and intelligent retrieval
- 🔄 **Real-time Chat** - WebSocket-powered instant messaging
- 👥 **Multi-user** - Complete user authentication and profiles

### Advanced Features
- 🔐 **Security** - JWT authentication, password hashing, rate limiting
- 📊 **Analytics** - Event tracking and performance monitoring
- 📁 **File Management** - Upload, process, and extract text from documents
- 🌍 **Multi-language** - Support for multiple languages and locales
- ⚙️ **Customization** - User settings for voice, AI parameters, preferences
- 📱 **WebSocket** - Real-time notifications and streaming responses
- 🐳 **Docker** - Containerized deployment ready
- 📝 **Logging** - Structured JSON logging for debugging

## 🏗️ Architecture

```
VoxAI/
├── backend/
│   ├── auth/              # Authentication & Security
│   ├── database/          # Database models & migrations
│   ├── routes/            # API endpoints
│   ├── agent/             # LLM agent & tools
│   ├── rag/               # RAG system
│   ├── voice/             # STT/TTS services
│   ├── config.py          # Configuration management
│   ├── schemas.py         # Pydantic models
│   ├── logging_config.py  # Logging setup
│   ├── websocket_manager.py  # WebSocket management
│   └── main.py            # FastAPI application
├── src/
│   ├── components/        # React components
│   ├── hooks/            # Custom React hooks
│   ├── engines/          # Frontend engines
│   └── App.jsx           # Main app
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Backend container
├── Dockerfile.frontend  # Frontend container
└── .env.example         # Configuration template
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+ (if not using Docker)
- Redis (if not using Docker)

### Using Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/Dwig9yadav/chole_chawal.git
cd chole_chawal

# 2. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec backend alembic upgrade head

# 5. Access applications
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development Setup

```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
createdb voxai
alembic upgrade head

# Start backend
python -m uvicorn backend.main:app --reload

# Frontend Setup (in new terminal)
npm install
npm run dev

# Frontend will be available at http://localhost:5173
# Backend API at http://localhost:8000
```

## 📚 API Documentation

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Create Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Study Session",
    "description": "Learning about AI",
    "system_prompt": "You are a helpful study assistant"
  }'
```

### Send Message

```bash
curl -X POST http://localhost:8000/api/v1/conversations/{id}/messages \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What is machine learning?",
    "role": "user"
  }'
```

### WebSocket Real-time Chat

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/{userId}/{conversationId}`
);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Message received:', message);
};

ws.send(JSON.stringify({
  type: 'chat',
  data: { content: 'Hello!' }
}));
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/voxai

# Redis
REDIS_URL=redis://localhost:6379

# Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_HOURS=24

# LLM Models
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...
DEFAULT_MODEL=gpt-3.5-turbo

# Voice Settings
ENABLE_STT=True
ENABLE_TTS=True
DEFAULT_VOICE=en-US

# File Upload
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=pdf,txt,docx,pptx

# Logging
LOG_LEVEL=INFO
SENTRY_DSN=https://...
```

## 📦 Deployment

### Production Deployment with Docker

```bash
# Build images
docker-compose -f docker-compose.yml build

# Deploy
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f backend
```

### Environment for Production

```bash
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com
SENTRY_DSN=your-sentry-url
```

## 🧪 Testing

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
npm test

# API integration tests
pytest backend/tests/integration/
```

## 📊 Monitoring & Analytics

- **Health Check**: `GET /health`
- **WebSocket Connections**: Real-time connection tracking
- **Event Analytics**: Automatic event logging for all user actions
- **Performance Metrics**: Built-in performance monitoring
- **Error Tracking**: Integrated with Sentry for error reporting

## 🔐 Security Features

- ✅ JWT Token Authentication
- ✅ Password Hashing (bcrypt)
- ✅ Rate Limiting
- ✅ CORS Configuration
- ✅ SQL Injection Prevention (SQLAlchemy ORM)
- ✅ Input Validation (Pydantic)
- ✅ Secure Headers
- ✅ Data Encryption

## 📝 Database Schema

### Users Table
- id, email, username, hashed_password
- full_name, avatar_url, bio
- language, theme, notifications_enabled
- is_active, is_verified
- created_at, updated_at, last_login

### Conversations Table
- id, user_id, title, description, status
- model_used, system_prompt
- message_count, token_usage
- created_at, updated_at, last_message_at

### Messages Table
- id, conversation_id, role, content
- tokens_used, confidence
- transcript, audio_url
- created_at

### UploadedFiles Table
- id, user_id, original_filename, stored_filename
- file_size, file_type
- is_processed, extraction_status, extracted_text
- created_at, processed_at

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

- 📧 Email: support@voxai.ai
- 💬 Discord: [Join our community](https://discord.gg/voxai)
- 📖 Documentation: [Full Docs](https://docs.voxai.ai)

## 🎉 Acknowledgments

- Built with FastAPI, React, PostgreSQL, and Redis
- Powered by OpenAI and Groq APIs
- Voice processing with gTTS and SpeechRecognition
- UI Components inspired by modern design systems

---

**VoxAI v2.0** - Making AI voice assistants accessible and powerful 🚀
