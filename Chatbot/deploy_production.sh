#!/bin/bash

# Pukaar-GPT Production Deployment Script
# Handles complete production deployment with health checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 Pukaar-GPT Production Deployment${NC}"
echo "======================================"

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="pukaar-prod"
BACKEND_URL="http://localhost:5000"
HEALTH_TIMEOUT=120  # 2 minutes

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be healthy
wait_for_health() {
    local service_name="$1"
    local url="$2"
    local timeout="$3"
    
    print_status "Waiting for $service_name to be healthy..."
    
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_success "$service_name is healthy!"
            return 0
        fi
        
        sleep 5
        elapsed=$((elapsed + 5))
        print_status "Still waiting... ($elapsed/$timeout seconds)"
    done
    
    print_error "$service_name failed to become healthy within $timeout seconds"
    return 1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Prerequisites check passed"

# Check environment file
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please create .env file with required environment variables."
    echo "Required variables:"
    echo "  GOOGLE_API_KEY=your_gemini_api_key_here"
    echo "  REDIS_URL=redis://localhost:6379 (optional)"
    echo "  FLASK_ENV=production"
    echo "  FLASK_DEBUG=false"
    exit 1
fi

print_success "Environment file found"

# Load environment variables
print_status "Loading environment variables..."
source .env

# Check required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    print_error "GOOGLE_API_KEY is not set in .env file"
    exit 1
fi

print_success "Environment variables loaded"

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down --remove-orphans || true
print_success "Existing containers stopped"

# Clean up old images (optional)
read -p "Do you want to clean up old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up old images..."
    docker system prune -f
    print_success "Cleanup completed"
fi

# Build and start services
print_status "Building and starting services..."
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Check service status
print_status "Checking service status..."
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps

# Wait for backend to be healthy
if ! wait_for_health "Backend" "$BACKEND_URL/health" $HEALTH_TIMEOUT; then
    print_error "Backend health check failed"
    print_status "Showing backend logs..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs backend
    exit 1
fi

# Test API endpoints
print_status "Testing API endpoints..."

# Health check
if curl -s -f "$BACKEND_URL/health" >/dev/null; then
    print_success "Health endpoint is working"
else
    print_error "Health endpoint is not working"
    exit 1
fi

# Basic API test
print_status "Testing main API endpoint..."
test_response=$(curl -s -X POST "$BACKEND_URL/api/screen" \
    -H "Content-Type: application/json" \
    -d '{"message": "My baby is not feeling well"}')

if echo "$test_response" | grep -q "flow_type"; then
    print_success "Main API endpoint is working"
    echo "Test response: $test_response"
else
    print_error "Main API endpoint is not working"
    echo "Response: $test_response"
    exit 1
fi

# Show final status
print_status "Final service status:"
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps

print_success "🎉 Production deployment completed successfully!"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo "========================"
echo "• Backend API: $BACKEND_URL"
echo "• Health Check: $BACKEND_URL/health"
echo "• API Endpoint: $BACKEND_URL/api/screen"
echo "• Frontend: http://localhost:3000 (if enabled)"
echo ""
echo -e "${BLUE}🧪 Testing Commands:${NC}"
echo "====================="
echo "• Run test suite: ./test_flows.sh"
echo "• Health check: curl $BACKEND_URL/health"
echo "• API test: curl -X POST $BACKEND_URL/api/screen -H \"Content-Type: application/json\" -d '{\"message\": \"test\"}'"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "==============="
echo "• View logs: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f"
echo "• Service status: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps"
echo "• Stop services: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down"
echo ""
print_success "Deployment script completed successfully!" 