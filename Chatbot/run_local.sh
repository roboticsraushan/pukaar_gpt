#!/bin/bash

# Pukaar-GPT Local Development Run Script
# This script runs the local Docker Compose setup with incremental builds

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

# Parse command line arguments
DETACHED=false
REBUILD=false
DEBUG=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--detached) DETACHED=true ;;
        -r|--rebuild) REBUILD=true ;;
        --debug) DEBUG=true ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -d, --detached    Run containers in detached mode"
            echo "  -r, --rebuild     Force rebuild of containers"
            echo "  --debug           Run with debug mode enabled"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *) print_error "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "🚀 Starting Pukaar-GPT Local Development Environment..."
echo "======================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_status "Creating .env file with template..."
    cat > .env << 'EOF'
# Google API Configuration
GOOGLE_API_KEY=your-google-api-key-here

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
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

# Stop only local containers (using project name to avoid conflicts)
print_status "Stopping local development containers..."
docker-compose -f docker-compose.local.yml -p pukaar-local down

# Set Flask environment based on debug flag
if [ "$DEBUG" = true ]; then
    print_status "Running in DEBUG mode..."
    # Update .env file to set development mode
    sed -i 's/FLASK_ENV=production/FLASK_ENV=development/g' .env
    # Set Flask debug mode in docker-compose environment
    export FLASK_DEBUG=1
else
    # Set production mode if not debugging
    sed -i 's/FLASK_ENV=development/FLASK_ENV=production/g' .env
    export FLASK_DEBUG=0
fi

# Build containers
print_status "Building local development containers..."
if [ "$REBUILD" = true ]; then
    print_warning "Forcing full rebuild of containers..."
    docker-compose -f docker-compose.local.yml -p pukaar-local build --no-cache
else
    docker-compose -f docker-compose.local.yml -p pukaar-local build
fi

# Start containers
print_status "Starting local development containers..."
if [ "$DETACHED" = true ]; then
    print_status "Running in detached mode..."
    docker-compose -f docker-compose.local.yml -p pukaar-local up -d
    
    # Wait for containers to be ready
    print_status "Waiting for containers to be ready..."
    sleep 10
    
    # Check if containers are running
    print_status "Checking container status..."
    if docker-compose -f docker-compose.local.yml -p pukaar-local ps | grep -q "Up"; then
        print_success "All local development containers are running!"
    else
        print_error "Some containers failed to start!"
        docker-compose -f docker-compose.local.yml -p pukaar-local logs
        exit 1
    fi
else
    print_status "Running with logs visible (press Ctrl+C to stop)..."
    docker-compose -f docker-compose.local.yml -p pukaar-local up
    exit 0
fi

# Display service URLs
echo ""
print_success "Local development environment started successfully!"
echo "======================================================"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📚 API Documentation: http://localhost:5000/api-doc"
echo ""
print_status "To view logs: docker-compose -f docker-compose.local.yml -p pukaar-local logs -f"
print_status "To stop services: docker-compose -f docker-compose.local.yml -p pukaar-local down"
print_status "Note: This will only stop local containers, production containers remain unaffected"
print_status "For full rebuild: docker-compose -f docker-compose.local.yml -p pukaar-local build --no-cache" 