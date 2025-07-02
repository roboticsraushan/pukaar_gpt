# Pukaar-GPT: Pediatric Healthcare Chatbot

A comprehensive pediatric healthcare chatbot that provides triage, screening, and emergency detection for infant and child health concerns. Built with Python Flask, Google Gemini LLM, and following IMNCI/WHO/IAP clinical protocols.

## 🚀 Features

- **Multi-Flow Orchestration**: Initial, Triage, Screening, Red Flag, Follow-up, Consult, Developmental, and Reassurance flows
- **Emergency Detection**: Real-time red flag detection for life-threatening situations
- **Clinical Protocols**: Based on IMNCI, WHO IMCI, IAP, and AIIMS guidelines
- **Session Management**: Persistent conversation context and flow tracking
- **LLM-Powered**: Google Gemini integration for intelligent responses
- **Production Ready**: Docker containerization and scalable architecture

## 🏗️ Architecture

```
Frontend (React) ←→ Backend (Flask) ←→ Google Gemini API
                      ↓
                Session Manager (Redis)
                      ↓
                Context Classifier
                      ↓
                Flow Orchestrator
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key
- Redis (optional, falls back to in-memory)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd pukaar_gpt/Chatbot
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Backend Configuration
FLASK_ENV=production
FLASK_DEBUG=false
```

### 3. Production Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 4. Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## 📡 API Documentation

### Single Endpoint: `/api/screen`

**URL:** `POST /api/screen`

**Purpose:** Main entry point for all pediatric health interactions. Automatically routes to appropriate flow based on user input.

**Request Body:**
```json
{
  "session_id": "optional-session-id",
  "message": "User's health concern or question"
}
```

**Response:**
```json
{
  "message": "AI response text",
  "flow_type": "triage|screening|red_flag|follow_up|consult|developmental|reassurance",
  "urgent": false,
  "session_id": "session-id",
  "current_step": 0,
  "data": "additional response data"
}
```

## 🧪 Testing Examples

### 1. Initial/Triage Flow

```bash
# Vague health concern
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby is not feeling well"
  }'
```

**Expected Response:**
```json
{
  "message": "Please describe your child's specific symptoms...",
  "flow_type": "triage",
  "urgent": false
}
```

### 2. Red Flag/Emergency Detection

```bash
# Emergency situation
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby is not waking up and is breathing very fast"
  }'
```

**Expected Response:**
```json
{
  "message": "⚠️ URGENT: Red flag detected! Please seek immediate medical attention.",
  "flow_type": "red_flag",
  "urgent": true,
  "trigger": "not waking up and breathing very fast"
}
```

### 3. Follow-up Flow

```bash
# Follow-up after treatment
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The diarrhea has not improved after 3 days of treatment"
  }'
```

**Expected Response:**
```json
{
  "message": "Persistent diarrhea after 3 days of treatment requires...",
  "flow_type": "follow_up",
  "urgent": false
}
```

### 4. Consult/Advice Flow

```bash
# General health advice
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I give paracetamol for fever?"
  }'
```

**Expected Response:**
```json
{
  "message": "Fever is a common symptom in children...",
  "flow_type": "consult",
  "urgent": false
}
```

### 5. Non-Urgent/Reassurance

```bash
# Mild symptoms
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My child has a mild cold but is playing normally"
  }'
```

**Expected Response:**
```json
{
  "message": "A mild cold with normal activity is common...",
  "flow_type": "triage",
  "urgent": false
}
```

### 6. Session Continuity

```bash
# First message
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My baby has a fever"
  }'

# Follow-up in same session
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-id-from-previous-response",
    "message": "The fever is still there after giving medicine"
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Docker Compose Services

- **backend**: Flask API server
- **frontend**: React web interface (optional)
- **redis**: Session storage (optional)

## 🧪 Testing

### Automated Test Suite

```bash
# Run comprehensive test suite
python3 test_frontend_flows.py

# Generate test cases
python3 generate_large_test_csv.py

# Run with custom test file
python3 test_frontend_flows.py --csv-file my_test_cases.csv
```

### Manual Testing

```bash
# Health check
curl http://localhost:5000/health

# Test each flow type
./test_flows.sh
```

## 📊 Monitoring

### Health Endpoints

```bash
# Basic health
curl http://localhost:5000/health

# Detailed health
curl http://localhost:5000/health/detailed

# Metrics
curl http://localhost:5000/metrics
```

### Logs

```bash
# View backend logs
docker-compose -f docker-compose.prod.yml logs -f backend

# View all logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🔒 Security

- **API Key Management**: Store `GOOGLE_API_KEY` securely
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Implement rate limiting for production
- **HTTPS**: Use HTTPS in production environments

## 🚨 Emergency Protocols

The system follows validated clinical protocols:

- **IMNCI Guidelines**: Integrated Management of Neonatal and Childhood Illnesses
- **WHO IMCI**: World Health Organization guidelines
- **IAP Protocols**: Indian Academy of Pediatrics standards
- **AIIMS Guidelines**: All India Institute of Medical Sciences protocols

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

## 📞 Support

For technical support or clinical questions, contact: [Your Contact Information]