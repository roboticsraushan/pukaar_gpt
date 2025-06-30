#!/bin/bash

# Pukaar-GPT Incremental Build Script
# This script performs incremental builds using Docker layer caching

set -e  # Exit on any error

echo "🚀 Starting Pukaar-GPT Incremental Build..."
echo "=========================================="

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

# Function to check if files have changed
check_backend_changes() {
    local last_build_file=".last_backend_build"
    local current_hash=""
    
    # Create hash of backend files
    if [ -f "$last_build_file" ]; then
        current_hash=$(find backend/ -type f -name "*.py" -o -name "*.txt" -o -name "*.md" | xargs md5sum | sort | md5sum | cut -d' ' -f1)
        local last_hash=$(cat "$last_build_file")
        
        if [ "$current_hash" = "$last_hash" ]; then
            return 1  # No changes
        fi
    fi
    
    # Save current hash
    echo "$current_hash" > "$last_build_file"
    return 0  # Changes detected
}

check_frontend_changes() {
    local last_build_file=".last_frontend_build"
    local current_hash=""
    
    # Create hash of frontend files
    if [ -f "$last_build_file" ]; then
        current_hash=$(find frontend/ -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.css" -o -name "*.json" \) | xargs md5sum | sort | md5sum | cut -d' ' -f1)
        local last_hash=$(cat "$last_build_file")
        
        if [ "$current_hash" = "$last_hash" ]; then
            return 1  # No changes
        fi
    fi
    
    # Save current hash
    echo "$current_hash" > "$last_build_file"
    return 0  # Changes detected
}

# Build backend if needed
print_status "Checking backend for changes..."
if check_backend_changes; then
    print_status "Backend changes detected. Building backend..."
    docker build -f Dockerfile.backend -t pukaar-backend:latest .
    print_success "Backend built successfully!"
else
    print_status "No backend changes detected. Using cached image."
fi

# Build frontend if needed
print_status "Checking frontend for changes..."
if check_frontend_changes; then
    print_status "Frontend changes detected. Building frontend..."
    docker build -f Dockerfile.frontend -t pukaar-frontend:latest .
    print_success "Frontend built successfully!"
else
    print_status "No frontend changes detected. Using cached image."
fi

# Start containers using docker-compose (will use built images)
print_status "Starting containers..."
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

# Display service URLs
echo ""
print_success "Incremental build completed successfully!"
echo "=============================================="
echo "🌐 Frontend: http://34.47.240.92:3000"
echo "🔧 Backend API: http://34.47.240.92:5000"
echo "📚 API Documentation: http://34.47.240.92:5000/api-doc"
echo ""
print_status "To view logs: docker-compose logs -f"
print_status "To stop services: docker-compose down"
print_status "To force rebuild: rm .last_*_build && ./build_incremental.sh" 