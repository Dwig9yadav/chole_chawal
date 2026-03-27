from fastapi import FastAPI, WebSocket, Depends, HTTPException, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from backend.config import get_settings
from backend.routes.api import router as api_router
from backend.database import init_db
from backend.logging_config import setup_logging
from backend.websocket_manager import manager, MessageType, create_message
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize logging
logger = setup_logging()

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("Starting VoxAI Backend...")
    logger.info(f"Environment: DEBUG={settings.DEBUG}")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down VoxAI Backend...")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter
app.state.limiter = limiter

# Include routers
app.include_router(api_router, prefix="/api/v1", tags=["API"])


# ========== WebSocket Endpoints ==========
@app.websocket("/ws/chat/{user_id}/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, conversation_id: str):
    """WebSocket endpoint for real-time chat"""
    try:
        await manager.connect(websocket, user_id)
        
        # Send connection confirmation
        await websocket.send_json(create_message(
            type=MessageType.SYSTEM,
            data={"status": "connected", "user_count": len(manager.get_connected_users())},
            user_id=user_id,
            conversation_id=conversation_id
        ))
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process message
            message = create_message(
                type=data.get("type", MessageType.CHAT),
                data=data.get("data", {}),
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Broadcast to user
            await manager.broadcast_to_user(user_id, message)
            
            logger.info(f"Message from {user_id} in conversation {conversation_id}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected from conversation {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)


# ========== Health Check Endpoints ==========
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "active_connections": manager.get_total_connections(),
        "connected_users": len(manager.get_connected_users())
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "message": f"{settings.API_TITLE} API is running"
    }


# ========== Error Handlers ==========
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "detail": str(exc),
        "error_code": "INTERNAL_SERVER_ERROR"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
