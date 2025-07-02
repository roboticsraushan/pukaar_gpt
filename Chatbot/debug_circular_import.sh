#!/bin/bash

# Debug Circular Import Script for Pukaar-GPT
# This script helps debug circular import issues in the models

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

echo "🔍 Debugging Circular Import Issues in Pukaar-GPT..."
echo "======================================================"

# Check for circular imports in the models directory
print_status "Checking for circular imports in models directory..."

# First, let's check if there's a circular import between screening_model.py and enhanced_screening_model.py
print_status "Checking screening_model.py imports..."
grep -n "import" backend/models/screening_model.py

print_status "Checking enhanced_screening_model.py imports..."
grep -n "import" backend/models/enhanced_screening_model.py

print_status "Checking for screening_agent usage in enhanced_screening_model.py..."
grep -n "screening_agent" backend/models/enhanced_screening_model.py

# Fix the circular import by removing the problematic import
print_status "Fixing circular import in enhanced_screening_model.py..."
if grep -q "from .screening_model import screening_agent" backend/models/enhanced_screening_model.py; then
    print_warning "Found circular import! Removing it..."
    sed -i 's/from .screening_model import screening_agent/# Removed circular import/g' backend/models/enhanced_screening_model.py
    print_success "Circular import removed!"
else
    print_success "No circular import found in enhanced_screening_model.py"
fi

# Test importing the modules to see if the circular import is fixed
print_status "Testing imports..."
cd backend
python -c "from models.screening_model import run_screening; print('✅ Import successful!')" || print_error "Import failed!"
cd ..

print_status "Debug complete! You can now run the application with:"
print_status "./run_local.sh"
print_status "Or with debug mode:"
print_status "./run_local.sh --debug" 