#!/bin/bash

# Pukaar-GPT Deployment Script
# This script deploys both frontend and backend with proper configuration

set -e  # Exit on any error

echo "🚀 Starting Pukaar-GPT Deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_status "Creating .env file with template..."
    cat > .env << 'EOF'
# Google API Configuration
GOOGLE_API_KEY=your-google-api-key-here

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production

# Frontend Configuration
REACT_APP_API_URL=http://34.47.240.92:5000
EOF
    print_warning "Please update the GOOGLE_API_KEY in .env file with your actual API key!"
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=" .env || grep -q "your-google-api-key-here" .env; then
    print_error "GOOGLE_API_KEY not properly configured in .env file!"
    print_warning "Please set your actual Google API key in the .env file"
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start containers
print_status "Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 10

# Check if containers are running
print_status "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    print_success "All containers are running!"
else
    print_error "Some containers failed to start!"
    docker-compose logs
    exit 1
fi

# Test backend API
print_status "Testing backend API..."
if curl -s -X POST http://localhost:5000/api/triage \
    -H "Content-Type: application/json" \
    -d '{"message": "test"}' > /dev/null; then
    print_success "Backend API is responding!"
else
    print_error "Backend API is not responding!"
    docker-compose logs backend
    exit 1
fi

# Test frontend
print_status "Testing frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is accessible!"
else
    print_error "Frontend is not accessible!"
    docker-compose logs frontend
    exit 1
fi

# Display service URLs
echo ""
print_success "Deployment completed successfully!"
echo "=================================="
echo "🌐 Frontend: http://34.47.240.92:3000"
echo "🔧 Backend API: http://34.47.240.92:5000"
echo "📚 API Documentation: http://34.47.240.92:5000/api-doc"
echo ""
print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down" 