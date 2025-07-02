# Pukaar-GPT API Documentation

## Base URL : Backend
```
http://34.47.240.92:5000
```

## Base URL : Frontend (if you want to test yourself)
```
http://34.47.240.92:3000
```

## API Endpoints

### 1. Main Screening Endpoint with Session Management
**Endpoint:** `POST /api/screen`

**Description:** Main endpoint for the screening process with session management. Handles different flow types and maintains conversation state.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "My baby has fast breathing and yellow skin",
  "flowType": "initial|triage|screening|red_flag|follow_up",
  "sessionId": "optional-session-id",
  "metadata": {
    "condition": "optional condition name",
    "responses": ["optional user responses"],
    "additional_data": {}
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "message": "Triage completed. Please select a condition to screen for.",
  "data": {
    "pneumonia_ari": 75,
    "neonatal_jaundice": 85,
    "screenable": true,
    "response": "Fast breathing and yellow skin detected. This could indicate respiratory issues or jaundice."
  },
  "sessionId": "12345678-1234-5678-1234-567812345678",
  "nextAction": {
    "action": "select_condition",
    "message": "Please select a condition to screen for"
  }
}
```

### 2. Create Session
**Endpoint:** `POST /api/session`

**Description:** Creates a new session and returns the session ID.

**Response Format:**
```json
{
  "success": true,
  "sessionId": "12345678-1234-5678-1234-567812345678"
}
```

### 3. Get Session Data
**Endpoint:** `GET /api/session/{session_id}`

**Description:** Retrieves session data for the specified session ID.

**Response Format:**
```json
{
  "success": true,
  "session": {
    "id": "12345678-1234-5678-1234-567812345678",
    "created_at": 1625097600,
    "last_active": 1625097650,
    "flow_type": "triage",
    "current_step": 1,
    "conversation_history": [...],
    "screening_data": {...},
    "red_flags": [],
    "metadata": {}
  }
}
```

### 4. Get Session History
**Endpoint:** `GET /api/session/{session_id}/history`

**Description:** Retrieves conversation history for the specified session ID.

**Response Format:**
```json
{
  "success": true,
  "history": [
    {
      "role": "user",
      "content": "My baby has fast breathing and yellow skin",
      "timestamp": 1625097600,
      "metadata": {
        "flow_type": "initial"
      }
    },
    {
      "role": "system",
      "content": "I've analyzed the symptoms. Fast breathing and yellow skin could indicate respiratory issues or jaundice.",
      "timestamp": 1625097610,
      "metadata": {
        "flow_type": "triage",
        "data": {...}
      }
    }
  ]
}
```

### 5. Health Screening Triage
**Endpoint:** `POST /api/triage`

**Description:** Analyzes infant symptoms and provides health screening results using IMNCI/WHO/IAP guidelines.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "My baby has fast breathing and yellow skin"
}
```

**Response Format:**
```json
{
  "result": "{\"pneumonia_ari\": 75, \"diarrhea\": 10, \"malnutrition\": 5, \"neonatal_sepsis\": 15, \"neonatal_jaundice\": 85, \"looks_normal\": 10, \"screenable\": true, \"response\": \"Fast breathing and chest symptoms detected. This could indicate respiratory issues. Please consult a pediatrician immediately.\"}"
}
```

### 6. Red Flag Detection
**Endpoint:** `POST /api/red-flag`

**Description:** Detects medical emergency red flags in infant symptoms using conservative clinical interpretation.

**Request Body:**
```json
{
  "message": "My baby is not breathing and has blue lips"
}
```

**Response Format:**
```json
{
  "red_flag_detected": true,
  "trigger": "Detected: not breathing",
  "recommended_action": "Rush to emergency immediately"
}
```

**Alternative Response (No Red Flags):**
```json
{
  "red_flag_detected": false,
  "trigger": null,
  "recommended_action": null
}
```

### 7. Context Classification
**Endpoint:** `POST /api/context-classifier`

**Description:** Classifies user input into medical_screenable, medical_non_screenable, or non_medical contexts.

**Request Body:**
```json
{
  "message": "My baby has a cough and fast breathing"
}
```

**Response Format:**
```json
{
  "classified_context": "medical_screenable",
  "reasoning": "Mentions pneumonia ari which can be screened using our system",
  "confidence": "high",
  "detected_conditions": ["pneumonia_ari"],
  "next_action": "Proceed with medical screening using our triage system",
  "expert_type": "Medical screening assistant"
}
```


### 8. Run Screening
**Endpoint:** `POST /api/screening/<condition>/run`

**Description:** Run screening for a specific condition with user responses.

**Request Body:**
```json
{
  "responses": ["yes", "no", "yes", "yes", "65", "yes", "yes"]
}
```

**Response Format:**
```json
{
  "condition_screened": "Pneumonia/Acute Respiratory Infection",
  "confidence_score": 72.5,
  "likelihood": "likely",
  "recommended_action": "Please consult a pediatrician immediately.",
  "disclaimer": "This is a screening result based on IMNCI/WHO/IAP standards and not a medical diagnosis.",
  "red_flag_detected": false
}
```

### 9. Consult Advice
**Endpoint:** `POST /api/consult-advice`

**Description:** Provides parenting guidance for non-clinical issues and offers expert consultation.

**Request Body:**
```json
{
  "message": "My baby won't sleep through the night"
}
```

**Response Format:**
```json
{
  "topic_identified": "sleep",
  "expert_type": "pediatric sleep specialist",
  "response": {
    "acknowledgment": "I understand you're concerned about your baby's sleep. This is a common parenting challenge.",
    "gentle_advice": [
      "Sleep patterns in babies can vary greatly and change frequently.",
      "It's normal for babies to wake up during the night - this is part of healthy development."
    ],
    "behavioral_tips": [
      "Establish a consistent bedtime routine with calming activities.",
      "Create a sleep-friendly environment (dark, quiet, comfortable temperature)."
    ],
    "consultation_offer": "Would you like to consult a pediatric sleep specialist? We can help you book an appointment.",
    "disclaimer": "This guidance is for general parenting support and should not replace professional medical advice."
  }
}
```

### 10. Health Check
**Endpoint:** `GET /api/health`

**Description:** Checks the health of the application and its dependencies.

**Response Format:**
```json
{
  "status": "healthy",
  "redis": "Connected",
  "session_type": "redis"
}
```

## Testing Examples

### cURL Commands

#### 1. Test Main Screening Endpoint
```bash
curl -X POST http://34.47.240.92:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has fast breathing and yellow skin",
    "flowType": "triage"
  }'
```

#### 2. Create a New Session
```bash
curl -X POST http://34.47.240.92:5000/api/session
```

#### 3. Get Session Data
```bash
curl -X GET http://34.47.240.92:5000/api/session/12345678-1234-5678-1234-567812345678
```

#### 4. Get Session History
```bash
curl -X GET http://34.47.240.92:5000/api/session/12345678-1234-5678-1234-567812345678/history
```

#### 5. Test Health Screening
```bash
curl -X POST http://34.47.240.92:5000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has fast breathing and yellow skin"
  }'
```

#### 6. Test Red Flag Detection
```bash
curl -X POST http://34.47.240.92:5000/api/red-flag \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby is not breathing and has blue lips"
  }'
```

#### 7. Test Context Classification
```bash
curl -X POST http://34.47.240.92:5000/api/context-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has a cough and fast breathing"
  }'
```

#### 8. Test Run Screening
```bash
curl -X POST http://34.47.240.92:5000/api/screening/pneumonia_ari/run \
  -H "Content-Type: application/json" \
  -d '{
    "responses": ["yes", "no", "yes", "yes", "65", "yes", "yes"]
  }'
```

#### 9. Test Consult Advice
```bash
curl -X POST http://34.47.240.92:5000/api/consult-advice \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby won't sleep through the night"
  }'
```

#### 10. Test Health Check
```bash
curl -X GET http://34.47.240.92:5000/api/health
```

