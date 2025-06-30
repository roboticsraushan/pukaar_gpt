#!/bin/bash

# Script to run the Gemini and other model tests inside Docker

echo "Running model tests inside Docker container..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not installed."
  exit 1
fi

# Define test files
TEST_FILES=(
  "test_gemini_docker.py"
  "test_triage_docker.py"
  "test_all_models_docker.py"
)

# Check if the Docker container is running
if docker-compose ps | grep -q backend; then
  echo "Found running backend container, executing tests..."
else
  echo "Backend container is not running."
  echo "Starting container with docker-compose..."
  
  # Start the container
  docker-compose up -d backend
  
  # Wait for container to be ready
  echo "Waiting for container to be ready..."
  sleep 5
fi

# Copy all test files to the container and run them
for test_file in "${TEST_FILES[@]}"; do
  echo ""
  echo "===================================================="
  echo "Running test: $test_file"
  echo "===================================================="
  
  # Copy the test file to the container
  docker-compose cp "$test_file" backend:/app/
  
  # Make the test file executable
  docker-compose exec backend chmod +x "/app/$test_file"
  
  # Run the test inside the container
  docker-compose exec backend python "/app/$test_file"
  
  # Check the exit code
  if [ $? -eq 0 ]; then
    echo "Test $test_file completed successfully."
  else
    echo "Test $test_file failed with exit code $?."
  fi
  
  echo "===================================================="
done

echo ""
echo "All tests execution completed." 