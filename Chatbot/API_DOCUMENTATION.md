# Pukaar GPT API Documentation

## Base URL
```
http://34.131.151.166:5000
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

### 4. Screening Information
**Endpoint:** `GET /api/screening/<condition>`

**Description:** Get screening information and questions for a specific condition.

**Available Conditions:**
- `pneumonia_ari`
- `diarrhea`
- `malnutrition`
- `neonatal_sepsis`
- `neonatal_jaundice`

**Example Request:**
```
GET /api/screening/pneumonia_ari
```

**Response Format:**
```json
{
  "condition": "Pneumonia/Acute Respiratory Infection",
  "description": "A serious lung infection that can cause breathing difficulties and is a leading cause of infant mortality worldwide.",
  "importance": "Early detection is crucial as respiratory distress can rapidly worsen in infants.",
  "questions": [
    {"question": "Is the baby breathing faster than normal?", "type": "yes_no"},
    {"question": "Can you see the baby's ribs or chest pulling in when breathing?", "type": "yes_no"},
    {"question": "Is the baby making grunting sounds while breathing?", "type": "yes_no"},
    {"question": "Does the baby have a cough?", "type": "yes_no"},
    {"question": "How many breaths per minute is the baby taking? (Count for 1 minute)", "type": "descriptive"},
    {"question": "Is the baby's nose flaring when breathing?", "type": "yes_no"},
    {"question": "Does the baby seem to be working hard to breathe?", "type": "yes_no"}
  ],
  "disclaimer": "This is not a medical diagnosis. This is a screening based on IMNCI/WHO/IAP guidelines to help identify potential warning signs."
}
```

### 5. Run Screening
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

### 6. Consult Advice
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

### 7. Follow-up Options
**Endpoint:** `GET /api/followup/options`

**Description:** Returns available follow-up consultation options.

**Response:**
```json
{
  "options": [
    "Book an online consultation",
    "Find nearby pediatrician"
  ]
}
```

## Testing Examples

### cURL Commands

#### 1. Test Health Screening
```bash
curl -X POST http://34.131.151.166:5000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has fast breathing and yellow skin"
  }'
```

#### 2. Test Red Flag Detection
```bash
curl -X POST http://34.131.151.166:5000/api/red-flag \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby is not breathing and has blue lips"
  }'
```

#### 3. Test Context Classification
```bash
curl -X POST http://34.131.151.166:5000/api/context-classifier \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has a cough and fast breathing"
  }'
```

#### 4. Test Screening Information
```bash
curl -X GET http://34.131.151.166:5000/api/screening/pneumonia_ari
```

#### 5. Test Run Screening
```bash
curl -X POST http://34.131.151.166:5000/api/screening/pneumonia_ari/run \
  -H "Content-Type: application/json" \
  -d '{
    "responses": ["yes", "no", "yes", "yes", "65", "yes", "yes"]
  }'
```

#### 6. Test Consult Advice
```bash
curl -X POST http://34.131.151.166:5000/api/consult-advice \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby won't sleep through the night"
  }'
```

#### 7. Test Follow-up Options
```bash
curl -X GET http://34.131.151.166:5000/api/followup/options
```

### JavaScript/Fetch Examples

#### 1. Health Screening
```javascript
const response = await fetch('http://34.131.151.166:5000/api/triage', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'My baby has fast breathing and yellow skin'
  })
});

const data = await response.json();
if (data.result) {
  const parsedResult = JSON.parse(data.result);
  console.log('Parsed result:', parsedResult);
}
```

#### 2. Red Flag Detection
```javascript
const response = await fetch('http://34.131.151.166:5000/api/red-flag', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'My baby is not breathing and has blue lips'
  })
});

const data = await response.json();
console.log('Red flag result:', data);
```

#### 3. Context Classification
```javascript
const response = await fetch('http://34.131.151.166:5000/api/context-classifier', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'My baby has a cough and fast breathing'
  })
});

const data = await response.json();
console.log('Context classification:', data);
```

#### 4. Screening Information
```javascript
const response = await fetch('http://34.131.151.166:5000/api/screening/pneumonia_ari');
const data = await response.json();
console.log('Screening info:', data);
```

#### 5. Run Screening
```javascript
const response = await fetch('http://34.131.151.166:5000/api/screening/pneumonia_ari/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    responses: ['yes', 'no', 'yes', 'yes', '65', 'yes', 'yes']
  })
});

const data = await response.json();
console.log('Screening result:', data);
```

#### 6. Consult Advice
```javascript
const response = await fetch('http://34.131.151.166:5000/api/consult-advice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'My baby won\'t sleep through the night'
  })
});

const data = await response.json();
console.log('Consult advice:', data);
```

## Test Cases

### Test Case 1: Respiratory Symptoms
```json
{
  "message": "My baby is breathing fast and has a cough"
}
```
**Expected:** High `pneumonia_ari` score

### Test Case 2: Emergency Red Flag
```json
{
  "message": "My baby is not breathing and has blue lips"
}
```
**Expected:** Red flag detected with emergency action

### Test Case 3: Non-Medical Concern
```json
{
  "message": "My baby won't sleep through the night"
}
```
**Expected:** Context classified as "non_medical", consult advice provided

### Test Case 4: Medical Non-Screenable
```json
{
  "message": "My baby is teething and crying a lot"
}
```
**Expected:** Context classified as "medical_non_screenable"

## Frontend Integration Notes

### 1. Response Parsing
The triage endpoint returns the screening result as a JSON string in the `result` field. You need to parse it:

```javascript
const data = await response.json();
if (data.result) {
  const parsedResult = JSON.parse(data.result);
  // Use parsedResult for display
}
```

### 2. Error Handling
Always check for errors in the response:

```javascript
if (response.ok) {
  const data = await response.json();
  // Process data
} else {
  const errorData = await response.json();
  console.error('Error:', errorData.error);
}
```

### 3. CORS
The backend has CORS enabled, so you can make requests from any origin.

### 4. Environment Variables
For development, you can use:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://34.131.151.166:5000';
```

## Development Workflow

### 1. Backend Development
- Backend runs on port 5000
- Uses Flask with CORS enabled
- Mock implementation for testing (no Google Cloud credentials needed)
- Real implementation available when credentials are configured

### 2. Frontend Development
- Can run independently on any port
- Make API calls to backend endpoints
- Handle response parsing and error cases
- Test with various symptom descriptions

### 3. Testing Strategy
1. Test with mock data first
2. Test error scenarios (missing message, server errors)
3. Test with real symptom descriptions
4. Test response parsing and display

## Current Status
- ✅ All API endpoints working
- ✅ Mock implementation for testing
- ✅ CORS enabled
- ✅ Error handling implemented
- ✅ Response format standardized
- ✅ Comprehensive documentation

## Next Steps
1. Frontend developer can start building UI
2. Test all endpoints with provided examples
3. Implement response parsing and display
4. Add error handling and loading states
5. Test with real symptom data 