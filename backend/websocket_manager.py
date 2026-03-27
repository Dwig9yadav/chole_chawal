"""WebSocket management for real-time features"""
from typing import Set, Dict, List
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # user_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # connection_id -> user_id mapping
        self.connection_user_map: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a closed WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(f"User {user_id} disconnected")
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a user"""
        if user_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
    
    async def broadcast_to_all(self, message: dict):
        """Send message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(user_id, message)
    
    async def send_personal_message(self, user_id: str, message: dict):
        """Send a personal message to a specific user"""
        await self.broadcast_to_user(user_id, message)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_connected_users(self) -> List[str]:
        """Get list of all connected user IDs"""
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()


# Message types for WebSocket protocol
class MessageType:
    """WebSocket message types"""
    CHAT = "chat"
    STATUS = "status"
    NOTIFICATION = "notification"
    TYPING = "typing"
    FILE_UPLOAD = "file_upload"
    ERROR = "error"
    SYSTEM = "system"


def create_message(
    type: str,
    data: dict,
    user_id: str = None,
    conversation_id: str = None,
    timestamp: datetime = None
) -> dict:
    """Create a formatted WebSocket message"""
    return {
        "type": type,
        "data": data,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "timestamp": (timestamp or datetime.utcnow()).isoformat()
    }
