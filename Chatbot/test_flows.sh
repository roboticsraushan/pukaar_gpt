#!/bin/bash

# Pukaar-GPT API Test Script
# Tests all flow types and health endpoints

BASE_URL="http://localhost:5000"
API_ENDPOINT="$BASE_URL/api/screen"

echo "🏥 Pukaar-GPT API Test Suite"
echo "=============================="
echo "Base URL: $BASE_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local test_name="$1"
    local message="$2"
    local expected_flow="$3"
    local expected_urgent="$4"
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    echo "Message: $message"
    
    response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}")
    
    # Extract flow_type and urgent from response
    flow_type=$(echo "$response" | grep -o '"flow_type":"[^"]*"' | cut -d'"' -f4)
    urgent=$(echo "$response" | grep -o '"urgent":[^,]*' | cut -d':' -f2 | tr -d '}')
    
    echo "Response: $response"
    echo "Got flow_type: $flow_type (expected: $expected_flow)"
    echo "Got urgent: $urgent (expected: $expected_urgent)"
    
    # Check if test passed
    if [ "$flow_type" = "$expected_flow" ] && [ "$urgent" = "$expected_urgent" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    echo ""
}

# Health checks
echo -e "${YELLOW}🔍 Health Checks${NC}"
echo "=================="

echo "Testing basic health endpoint..."
health_response=$(curl -s "$BASE_URL/health")
echo "Health response: $health_response"
echo ""

echo "Testing detailed health endpoint..."
detailed_health_response=$(curl -s "$BASE_URL/health/detailed")
echo "Detailed health response: $detailed_health_response"
echo ""

echo "Testing metrics endpoint..."
metrics_response=$(curl -s "$BASE_URL/metrics")
echo "Metrics response: $metrics_response"
echo ""

# Test each flow type
echo -e "${YELLOW}🧪 Flow Type Tests${NC}"
echo "=================="

# 1. Initial/Triage Flow
test_endpoint "Initial/Triage" "My baby is not feeling well" "triage" "false"
test_endpoint "Initial/Triage" "I have a health concern about my 2-year-old" "triage" "false"

# 2. Red Flag/Emergency Detection
test_endpoint "Red Flag" "My baby is not waking up and is breathing very fast" "red_flag" "true"
test_endpoint "Red Flag" "My child had a seizure and is not responding" "red_flag" "true"
test_endpoint "Red Flag" "My child fell and is now unconscious" "red_flag" "true"

# 3. Follow-up Flow
test_endpoint "Follow-up" "The diarrhea has not improved after 3 days of treatment" "follow_up" "false"
test_endpoint "Follow-up" "My child was given antibiotics, but the fever is still there" "follow_up" "false"
test_endpoint "Follow-up" "We finished the medicine, but my baby is still coughing" "follow_up" "false"

# 4. Consult/Advice Flow
test_endpoint "Consult" "Should I give paracetamol for fever?" "consult" "false"
test_endpoint "Consult" "Is it safe to give my baby water at 4 months?" "consult" "false"
test_endpoint "Consult" "What should I feed my child with diarrhea?" "consult" "false"

# 5. Non-Urgent/Reassurance
test_endpoint "Non-Urgent" "My child has a mild cold but is playing normally" "triage" "false"
test_endpoint "Non-Urgent" "My baby sneezes a lot but has no fever" "triage" "false"
test_endpoint "Non-Urgent" "My child has a small bruise from falling" "triage" "false"

# Session continuity test
echo -e "${YELLOW}🔄 Session Continuity Test${NC}"
echo "=============================="

echo "Sending first message..."
first_response=$(curl -s -X POST "$API_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"message": "My baby has a fever"}')

session_id=$(echo "$first_response" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
echo "First response: $first_response"
echo "Session ID: $session_id"
echo ""

if [ -n "$session_id" ]; then
    echo "Sending follow-up message with same session..."
    followup_response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "{\"session_id\": \"$session_id\", \"message\": \"The fever is still there after giving medicine\"}")
    
    echo "Follow-up response: $followup_response"
    echo -e "${GREEN}✅ Session continuity test completed${NC}"
else
    echo -e "${RED}❌ No session ID found in first response${NC}"
fi

echo ""
echo -e "${YELLOW}🎯 Test Summary${NC}"
echo "=============="
echo "All tests completed. Check the output above for results."
echo ""
echo "To run individual tests, use:"
echo "curl -X POST $API_ENDPOINT -H \"Content-Type: application/json\" -d '{\"message\": \"your message here\"}'"
echo ""
echo "For health checks:"
echo "curl $BASE_URL/health"
echo "curl $BASE_URL/health/detailed"
echo "curl $BASE_URL/metrics" 