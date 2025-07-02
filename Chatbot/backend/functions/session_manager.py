"""
Session Manager for Pukaar-GPT
Handles user session management, persistence, and state tracking
"""

import json
import uuid
import time
from typing import Dict, Any, Optional, List, Union
import redis
import os

# Initialize Redis client
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Session expiration time (24 hours in seconds)
SESSION_EXPIRY = 86400

# Flow types
FLOW_TYPES = {
    'INITIAL': 'initial',
    'TRIAGE': 'triage',
    'SCREENING': 'screening',
    'RED_FLAG': 'red_flag',
    'FOLLOW_UP': 'follow_up',
    'CONSULT': 'consult'
}

# Try to connect to Redis, fallback to in-memory storage if Redis is not available
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True
    )
    redis_client.ping()  # Test connection
    print("[INFO] Connected to Redis successfully")
    USE_REDIS = True
except Exception as e:
    print(f"[WARNING] Redis connection failed: {e}. Using in-memory session storage.")
    USE_REDIS = False
    # In-memory session storage as fallback
    in_memory_sessions = {}


class SessionManager:
    """Session manager for handling user sessions and state"""

    @staticmethod
    def create_session() -> str:
        """Create a new session and return the session ID"""
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'created_at': time.time(),
            'last_active': time.time(),
            'flow_type': FLOW_TYPES['INITIAL'],
            'current_step': 0,
            'conversation_history': [],
            'screening_data': {},
            'red_flags': [],
            'metadata': {}
        }
        
        if USE_REDIS:
            redis_client.setex(
                f"session:{session_id}", 
                SESSION_EXPIRY, 
                json.dumps(session_data)
            )
        else:
            in_memory_sessions[session_id] = session_data
            
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        if not session_id:
            return None
            
        if USE_REDIS:
            session_data = redis_client.get(f"session:{session_id}")
            if session_data:
                return json.loads(session_data)
        else:
            return in_memory_sessions.get(session_id)
            
        return None

    @staticmethod
    def update_session(session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session with new data"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return False
            
        # Update session data
        session_data.update(updates)
        session_data['last_active'] = time.time()
        
        if USE_REDIS:
            redis_client.setex(
                f"session:{session_id}", 
                SESSION_EXPIRY, 
                json.dumps(session_data)
            )
        else:
            in_memory_sessions[session_id] = session_data
            
        return True

    @staticmethod
    def add_message_to_history(
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to the conversation history"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return False
            
        message = {
            'role': role,
            'content': content,
            'timestamp': time.time()
        }
        
        if metadata:
            message['metadata'] = metadata
            
        if 'conversation_history' not in session_data:
            session_data['conversation_history'] = []
            
        session_data['conversation_history'].append(message)
        session_data['last_active'] = time.time()
        
        if USE_REDIS:
            redis_client.setex(
                f"session:{session_id}", 
                SESSION_EXPIRY, 
                json.dumps(session_data)
            )
        else:
            in_memory_sessions[session_id] = session_data
            
        return True

    @staticmethod
    def get_conversation_history(session_id: str) -> List[Dict[str, Any]]:
        """Get the conversation history for a session"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return []
            
        return session_data.get('conversation_history', [])

    @staticmethod
    def set_flow_type(session_id: str, flow_type: str) -> bool:
        """Set the flow type for a session"""
        if flow_type not in FLOW_TYPES.values():
            return False
            
        return SessionManager.update_session(
            session_id, 
            {'flow_type': flow_type, 'current_step': 0}
        )

    @staticmethod
    def advance_step(session_id: str) -> bool:
        """Advance to the next step in the current flow"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return False
            
        current_step = session_data.get('current_step', 0)
        return SessionManager.update_session(
            session_id, 
            {'current_step': current_step + 1}
        )

    @staticmethod
    def set_screening_data(session_id: str, condition: str, data: Dict[str, Any]) -> bool:
        """Set screening data for a specific condition"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return False
            
        if 'screening_data' not in session_data:
            session_data['screening_data'] = {}
            
        session_data['screening_data'][condition] = data
        
        if USE_REDIS:
            redis_client.setex(
                f"session:{session_id}", 
                SESSION_EXPIRY, 
                json.dumps(session_data)
            )
        else:
            in_memory_sessions[session_id] = session_data
            
        return True

    @staticmethod
    def add_red_flag(session_id: str, red_flag_data: Dict[str, Any]) -> bool:
        """Add a red flag to the session"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return False
            
        if 'red_flags' not in session_data:
            session_data['red_flags'] = []
            
        session_data['red_flags'].append(red_flag_data)
        
        if USE_REDIS:
            redis_client.setex(
                f"session:{session_id}", 
                SESSION_EXPIRY, 
                json.dumps(session_data)
            )
        else:
            in_memory_sessions[session_id] = session_data
            
        return True

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a session"""
        if USE_REDIS:
            return bool(redis_client.delete(f"session:{session_id}"))
        else:
            if session_id in in_memory_sessions:
                del in_memory_sessions[session_id]
                return True
            return False 