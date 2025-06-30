#!/bin/bash

# Pukaar-GPT Quick Development Build
# Fast incremental build for development

set -e

echo "⚡ Quick Development Build..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    print_status "Containers are running. Restarting with latest changes..."
    docker-compose down
fi

# Quick build without cache (faster than full rebuild)
print_status "Building containers..."
docker-compose build

# Start containers
print_status "Starting containers..."
docker-compose up -d

print_success "Development build complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000" 