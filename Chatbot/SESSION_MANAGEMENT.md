# Pukaar-GPT Session Management

## Overview
This document describes the session management implementation for the Pukaar-GPT healthcare chatbot. The session management system enables stateful conversations, tracking user interactions, and maintaining context across multiple requests.

## Key Components

### 1. Session Manager
The `SessionManager` class in `backend/functions/session_manager.py` provides the core functionality for session management:
- Creating and managing user sessions
- Storing conversation history
- Tracking screening progress
- Handling red flag scenarios
- Supporting both Redis and in-memory storage options

### 2. Screening Flow State Machine
The `ScreeningFlow` class in `backend/functions/screening_flow.py` implements a state machine for managing the screening process:
- Defining valid states and transitions
- Tracking the current state of a session
- Determining the next appropriate action
- Managing red flag scenarios and resumption

### 3. Main API Endpoint
The `/api/screen` endpoint in `backend/routes/screen.py` serves as the main entry point for the application:
- Handling different flow types (initial, triage, screening, red flag, follow-up)
- Managing session creation and retrieval
- Processing user messages
- Coordinating state transitions
- Providing appropriate responses based on the current state

### 4. Session Storage
The system supports two storage options:
- **Redis**: For production environments, providing persistence and scalability
- **In-memory**: Fallback option for development or when Redis is unavailable

## Flow Types

1. **Initial**: Starting point for new conversations
2. **Triage**: Analyzing symptoms to determine appropriate screening
3. **Screening**: Collecting and analyzing responses for specific conditions
4. **Red Flag**: Handling emergency situations that require immediate attention
5. **Follow-up**: Managing post-screening interactions and recommendations

## State Machine

The screening process follows a defined state machine with the following states:
- `INITIAL`: Starting point
- `TRIAGE`: Analyzing symptoms
- `CONDITION_SELECTION`: Selecting a condition to screen
- `QUESTION_COLLECTION`: Collecting responses to screening questions
- `ANALYSIS`: Analyzing responses
- `RECOMMENDATION`: Providing recommendations based on analysis
- `RED_FLAG_DETECTED`: Handling emergency situations
- `FOLLOW_UP`: Managing follow-up actions
- `COMPLETED`: End of the screening process
- `ERROR`: Handling error conditions

## Session Data Structure

```json
{
  "id": "session-uuid",
  "created_at": 1625097600,
  "last_active": 1625097650,
  "flow_type": "screening",
  "current_step": 2,
  "conversation_history": [
    {
      "role": "user",
      "content": "My baby has fast breathing",
      "timestamp": 1625097600
    },
    {
      "role": "system",
      "content": "I've analyzed the symptoms...",
      "timestamp": 1625097610
    }
  ],
  "screening_data": {
    "pneumonia_ari": {
      "confidence_score": 75,
      "recommended_action": "Please consult a pediatrician immediately."
    }
  },
  "red_flags": [],
  "metadata": {}
}
```

## API Endpoints

### Main Endpoint
- `POST /api/screen`: Main endpoint for the screening process

### Session Management
- `POST /api/session`: Create a new session
- `GET /api/session/{session_id}`: Get session data
- `GET /api/session/{session_id}/history`: Get conversation history

### Health Check
- `GET /api/health`: Check system health and dependencies

## Testing

A test script (`test_session_management.py`) is provided to verify the session management functionality:
- Testing all endpoints
- Verifying state transitions
- Checking session persistence
- Testing red flag scenarios

## Configuration

The session management system can be configured through environment variables:
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (optional)
- `REDIS_DB`: Redis database number (default: 0)

## Deployment

The system is deployed using Docker Compose with the following services:
- Backend (Flask)
- Frontend (React)
- Redis (for session storage)

## Future Enhancements

1. **Authentication**: Add user authentication to associate sessions with specific users
2. **Session Expiry**: Implement automatic cleanup of expired sessions
3. **Analytics**: Track session data for analytics and reporting
4. **Multi-device Support**: Enable seamless continuation of sessions across devices
5. **Offline Support**: Add offline capabilities with local storage and synchronization 