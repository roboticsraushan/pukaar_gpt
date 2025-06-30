# Pukaar-GPT API Documentation

## Base URL : Backend
```
http://34.131.162.187:5000
```

## Base URL : Frontend (if you want to test yourself)
```
http://34.131.162.187:3000
```

## API Endpoints

### 1. Health Screening Triage
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

### 2. Red Flag Detection
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

### 3. Context Classification
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


### 4. Run Screening
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

### 5. Consult Advice
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





## Testing Examples

### cURL Commands

#### 1. Test Health Screening
```bash
curl -X POST http://34.131.162.187:5000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has fast breathing and yellow skin"
  }'
```

#### 2. Test Red Flag Detection
```bash
curl -X POST http://34.131.162.187:5000/api/red-flag \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby is not breathing and has blue lips"
  }'
```

#### 3. Test Context Classification
```bash
curl -X POST http://34.131.162.187:5000/api/context-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has a cough and fast breathing"
  }'
```

#### 4. Test Run Screening
```bash
curl -X POST http://34.131.162.187:5000/api/screening/pneumonia_ari/run \
  -H "Content-Type: application/json" \
  -d '{
    "responses": ["yes", "no", "yes", "yes", "65", "yes", "yes"]
  }'
```

#### 5. Test Consult Advice
```bash
curl -X POST http://34.131.162.187:5000/api/consult-advice \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby won't sleep through the night"
  }'
```

