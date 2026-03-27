# VoxAI Installation & Setup Guide

## System Requirements

### Minimum
- **OS**: macOS 11+, Ubuntu 20.04+, Windows 10+
- **RAM**: 8GB
- **Disk**: 10GB free space
- **CPU**: 4 cores

### Production
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 16GB+
- **Disk**: 50GB SSD
- **CPU**: 8+ cores

## Prerequisites

### 1. Install Python 3.11+

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**Windows:**
- Download from https://www.python.org/downloads/
- Add Python to PATH during installation

### 2. Install Node.js 18+

**macOS:**
```bash
brew install node
```

**Ubuntu:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
- Download from https://nodejs.org/
- Follow installer instructions

### 3. Install PostgreSQL 16

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu:**
```bash
sudo apt install postgresql-16
sudo systemctl start postgresql
```

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Follow installer, remember postgres password

### 4. Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**Windows:**
- Download: https://github.com/microsoftarchive/redis/releases
- Or use WSL: `wsl --install -d Ubuntu && wsl apt install redis-server`

### 5. (Optional) Install Docker & Docker Compose

**Docker Desktop:** https://www.docker.com/products/docker-desktop

Or install individually:

**Ubuntu:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Installation Steps

### Option 1: Docker (Recommended for beginners)

```bash
# 1. Clone repository
git clone https://github.com/Dwig9yadav/chole_chawal.git
cd chole_chawal

# 2. Create environment file
cp .env.example .env

# 3. Edit .env (update API keys)
nano .env

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be ready
docker-compose logs -f backend

# 6. Initialize database
docker-compose exec backend python -c "from backend.database import init_db; init_db()"

# Services will be available at:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Adminer (PostgreSQL UI): http://localhost:8081
```

### Option 2: Local Development Setup

#### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/Dwig9yadav/chole_chawal.git
cd chole_chawal

# 2. Create Python virtual environment
python3.11 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Create database
createdb voxai

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create .env file
cp .env.example .env

# 7. Edit .env with your settings
nano .env

# 8. Initialize database
python -c "from backend.database import init_db; init_db()"

# 9. Run backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

#### Frontend Setup (in new terminal)

```bash
# 1. Navigate to project root
cd chole_chawal

# 2. Install Node dependencies
npm install

# 3. Create .env file for frontend
cp .env.example .env.local

# 4. Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Option 3: Cloud Deployment (AWS/GCP/Azure)

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed cloud deployment guides.

## Verification

### Check Backend

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "active_connections": 0,
  "connected_users": []
}
```

### Check Frontend

Open http://localhost:5173 in your browser

### Check Database

```bash
# Access PostgreSQL
psql voxai

# List tables
\dt

# Quit
\q
```

## Configuration

### Environment Variables

All configuration is managed through `.env` file. Key variables:

```env
# Backend Port
BACKEND_PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voxai

# API Keys
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### API Keys Setup

#### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Groq
1. Visit https://groq.com
2. Create account and generate API key
3. Add to `.env`: `GROQ_API_KEY=gsk-...`

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python -m uvicorn backend.main:app --port 8001
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
psql postgres

# Create database if not exists
createdb voxai

# Check connection string in .env
```

### Redis Connection Error

```bash
# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Node Modules Issues

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Python Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear cache
rm -rf __pycache__ .pytest_cache
```

## Next Steps

1. **Create User Account**: Register at http://localhost:5173
2. **Configure Voice**: Voice settings in user preferences
3. **Upload Documents**: Test RAG with PDF upload
4. **Test Voice Chat**: Use microphone for voice input
5. **Check API Docs**: http://localhost:8000/docs

## Getting Help

- **Documentation**: See [README_ADVANCED.md](./README_ADVANCED.md)
- **API Documentation**: http://localhost:8000/docs
- **Issues**: https://github.com/Dwig9yadav/chole_chawal/issues
- **Discord**: [Join Community](https://discord.gg/voxai)

## Performance Tips

- Use SSD for database
- Allocate at least 4GB to Docker
- Enable HTTP/2 for better performance
- Use CDN for static assets in production
- Enable caching in Redis

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Use strong database password
- [ ] Enable HTTPS in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Use environment-specific configurations
- [ ] Regularly update dependencies

---

For advanced configuration and production deployment, see [DEPLOYMENT.md](./docs/DEPLOYMENT.md)
