#!/usr/bin/env python3
"""
Test script for Pukaar-GPT session management functionality
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"  # Change to your server URL
HEADERS = {"Content-Type": "application/json"}

def print_colored(text, color):
    """Print colored text"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def make_request(method, endpoint, data=None):
    """Make a request to the API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=HEADERS)
        elif method.lower() == "post":
            response = requests.post(url, headers=HEADERS, json=data)
        else:
            print_colored(f"Unsupported method: {method}", "red")
            return None
            
        return response
    except Exception as e:
        print_colored(f"Error making request: {e}", "red")
        return None

def test_health_check():
    """Test the health check endpoint"""
    print_colored("\n=== Testing Health Check ===", "blue")
    response = make_request("get", "/api/health")
    if response and response.status_code == 200:
        print_colored("Health check successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Health check failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_create_session():
    """Test creating a new session"""
    print_colored("\n=== Testing Session Creation ===", "blue")
    response = make_request("post", "/api/session")
    if response and response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("sessionId"):
            print_colored(f"Session created successfully! Session ID: {data['sessionId']}", "green")
            return data["sessionId"]
        else:
            print_colored("Session creation response missing required fields!", "red")
            return None
    else:
        print_colored(f"Session creation failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return None

def test_initial_screen(session_id):
    """Test the initial screen flow"""
    print_colored("\n=== Testing Initial Screen ===", "blue")
    data = {
        "message": "Hello, I'm worried about my baby",
        "flowType": "initial",
        "sessionId": session_id
    }
    response = make_request("post", "/api/screen", data)
    if response and response.status_code == 200:
        print_colored("Initial screen successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Initial screen failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_triage_flow(session_id):
    """Test the triage flow"""
    print_colored("\n=== Testing Triage Flow ===", "blue")
    data = {
        "message": "My baby has fast breathing and yellow skin",
        "flowType": "triage",
        "sessionId": session_id
    }
    response = make_request("post", "/api/screen", data)
    if response and response.status_code == 200:
        print_colored("Triage flow successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Triage flow failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_screening_flow(session_id):
    """Test the screening flow"""
    print_colored("\n=== Testing Screening Flow ===", "blue")
    data = {
        "message": "",
        "flowType": "screening",
        "sessionId": session_id,
        "metadata": {
            "condition": "pneumonia_ari"
        }
    }
    response = make_request("post", "/api/screen", data)
    if response and response.status_code == 200:
        print_colored("Screening flow (condition selection) successful!", "green")
        print(json.dumps(response.json(), indent=2))
        
        # Now test with responses
        data["metadata"]["responses"] = ["yes", "yes", "no", "yes", "60", "yes", "yes"]
        response = make_request("post", "/api/screen", data)
        if response and response.status_code == 200:
            print_colored("Screening flow (with responses) successful!", "green")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print_colored(f"Screening flow (with responses) failed! Status code: {response.status_code if response else 'N/A'}", "red")
            return False
    else:
        print_colored(f"Screening flow (condition selection) failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_get_session(session_id):
    """Test getting session data"""
    print_colored("\n=== Testing Get Session ===", "blue")
    response = make_request("get", f"/api/session/{session_id}")
    if response and response.status_code == 200:
        print_colored("Get session successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Get session failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_get_session_history(session_id):
    """Test getting session history"""
    print_colored("\n=== Testing Get Session History ===", "blue")
    response = make_request("get", f"/api/session/{session_id}/history")
    if response and response.status_code == 200:
        print_colored("Get session history successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Get session history failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def test_red_flag_flow(session_id):
    """Test the red flag flow"""
    print_colored("\n=== Testing Red Flag Flow ===", "blue")
    data = {
        "message": "My baby is not breathing and has blue lips",
        "flowType": "triage",
        "sessionId": session_id
    }
    response = make_request("post", "/api/screen", data)
    if response and response.status_code == 200:
        print_colored("Red flag flow successful!", "green")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print_colored(f"Red flag flow failed! Status code: {response.status_code if response else 'N/A'}", "red")
        return False

def run_all_tests():
    """Run all tests"""
    print_colored("Starting Pukaar-GPT Session Management Tests...", "blue")
    
    # Test health check
    if not test_health_check():
        print_colored("Health check failed! Aborting tests.", "red")
        return
    
    # Test session creation
    session_id = test_create_session()
    if not session_id:
        print_colored("Session creation failed! Aborting tests.", "red")
        return
    
    # Test initial screen
    if not test_initial_screen(session_id):
        print_colored("Initial screen test failed!", "red")
    
    # Test triage flow
    if not test_triage_flow(session_id):
        print_colored("Triage flow test failed!", "red")
    
    # Test screening flow
    if not test_screening_flow(session_id):
        print_colored("Screening flow test failed!", "red")
    
    # Test get session
    if not test_get_session(session_id):
        print_colored("Get session test failed!", "red")
    
    # Test get session history
    if not test_get_session_history(session_id):
        print_colored("Get session history test failed!", "red")
    
    # Create a new session for red flag test
    red_flag_session_id = test_create_session()
    if not red_flag_session_id:
        print_colored("Session creation for red flag test failed!", "red")
    else:
        # Test red flag flow
        if not test_red_flag_flow(red_flag_session_id):
            print_colored("Red flag flow test failed!", "red")
    
    print_colored("\nAll tests completed!", "blue")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    run_all_tests() 