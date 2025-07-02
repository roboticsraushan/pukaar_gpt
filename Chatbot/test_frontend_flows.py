import requests
import json
import time
import csv
import os
from typing import List, Dict, Tuple

# Configuration
BACKEND_URL = "http://localhost:5000/api/screen"
CSV_FILE = "test_cases.csv"  # CSV file with test cases

def read_test_cases_from_csv(csv_file: str) -> List[Tuple[str, str, str, bool]]:
    """Read test cases from CSV file."""
    test_cases = []
    
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found. Creating sample CSV...")
        create_sample_csv(csv_file)
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            test_cases.append((
                row['description'],
                row['message'],
                row['expected_flow_type'],
                row['expect_urgent'].lower() == 'true'
            ))
    
    return test_cases

def create_sample_csv(csv_file: str):
    """Create a sample CSV file with test cases."""
    sample_cases = [
        # Follow-up Flow (1000 cases)
        ("Follow-up: checkup", "We were told to come back for a checkup after 2 days.", "follow_up", False),
        ("Follow-up: diarrhea not improved", "The diarrhea has not improved after 3 days of treatment.", "follow_up", False),
        ("Follow-up: antibiotics + fever", "My child was given antibiotics, but the fever is still there.", "follow_up", False),
        ("Follow-up: cough after medicine", "We finished the medicine, but my baby is still coughing.", "follow_up", False),
        ("Follow-up: rash follow-up", "The doctor asked us to follow up if the rash did not improve.", "follow_up", False),
        
        # Consult/Advice Flow (1000 cases)
        ("Consult: paracetamol", "Should I give paracetamol for fever?", "consult", False),
        ("Consult: water at 4 months", "Is it safe to give my baby water at 4 months?", "consult", False),
        ("Consult: feeding for diarrhea", "What should I feed my child with diarrhea?", "consult", False),
        ("Consult: prevent dehydration", "How can I prevent dehydration in my baby?", "consult", False),
        ("Consult: when to hospital", "When should I take my child to the hospital?", "consult", False),
        ("Consult: ibuprofen", "Can I give ibuprofen to my 1-year-old?", "consult", False),
        
        # Triage/Initial Flow (1000 cases)
        ("Initial: vague concern", "My baby is not feeling well.", "triage", False),
        ("Initial: health concern", "I have a health concern about my 2-year-old.", "triage", False),
        ("Initial: help request", "Can you help me with my child's symptoms?", "triage", False),
        
        # Red Flag/Emergency (1000 cases)
        ("Red flag: not waking up + fast breathing", "My baby is not waking up and is breathing very fast.", "red_flag", True),
        ("Red flag: seizure + not responding", "My child had a seizure and is not responding.", "red_flag", True),
        ("Red flag: unconscious after fall", "My child fell and is now unconscious.", "red_flag", True),
        ("Red flag: grunting + trouble breathing", "My baby is having trouble breathing and making grunting noises.", "red_flag", True),
        
        # Non-Urgent/Benign (1000 cases)
        ("Non-urgent: mild cold", "My child has a mild cold but is playing normally.", "triage", False),
        ("Non-urgent: sneezing", "My baby sneezes a lot but has no fever.", "triage", False),
        ("Non-urgent: small bruise", "My child has a small bruise from falling.", "triage", False),
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['description', 'message', 'expected_flow_type', 'expect_urgent'])
        for case in sample_cases:
            writer.writerow(case)
    
    print(f"Sample CSV created: {csv_file}")
    print("Please add more test cases to reach 1000 per category for extensive testing.")

def send_message_to_backend(message: str, session_id: str = "") -> Dict:
    """Send a message to the backend and get response."""
    if not session_id:
        session_id = f"test_session_{int(time.time())}"
    
    payload = {
        "session_id": session_id,
        "message": message
    }
    
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "flow_type": "error", "urgent": False}

def calculate_accuracy_metrics(results: List[Dict]) -> Dict:
    """Calculate comprehensive accuracy metrics."""
    # Group results by expected flow type
    flow_groups = {}
    for result in results:
        expected_flow = result['expected_flow_type']
        if expected_flow not in flow_groups:
            flow_groups[expected_flow] = []
        flow_groups[expected_flow].append(result)
    
    # Calculate metrics for each flow type
    metrics = {}
    total_correct = 0
    total_tests = len(results)
    
    for flow_type, cases in flow_groups.items():
        correct_flow = sum(1 for case in cases if case['got_flow_type'] == case['expected_flow_type'])
        correct_urgent = sum(1 for case in cases if case['got_urgent'] == case['expect_urgent'])
        total_cases = len(cases)
        
        flow_accuracy = (correct_flow / total_cases) * 100 if total_cases > 0 else 0
        urgent_accuracy = (correct_urgent / total_cases) * 100 if total_cases > 0 else 0
        overall_accuracy = ((correct_flow + correct_urgent) / (total_cases * 2)) * 100 if total_cases > 0 else 0
        
        metrics[flow_type] = {
            'total_cases': total_cases,
            'flow_accuracy': flow_accuracy,
            'urgent_accuracy': urgent_accuracy,
            'overall_accuracy': overall_accuracy,
            'correct_flow': correct_flow,
            'correct_urgent': correct_urgent
        }
        
        total_correct += correct_flow
    
    # Overall accuracy
    overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    
    return {
        'overall_accuracy': overall_accuracy,
        'total_tests': total_tests,
        'total_correct': total_correct,
        'flow_metrics': metrics
    }

def run_extensive_test():
    """Run extensive test with CSV input."""
    print("--- Pukaar-GPT Extensive Flow Test ---")
    print(f"Reading test cases from: {CSV_FILE}")
    
    # Read test cases from CSV
    test_cases = read_test_cases_from_csv(CSV_FILE)
    print(f"Loaded {len(test_cases)} test cases")
    
    if len(test_cases) == 0:
        print("No test cases found. Please check the CSV file.")
        return
    
    # Group by expected flow type for reporting
    flow_counts = {}
    for _, _, expected_flow, _ in test_cases:
        flow_counts[expected_flow] = flow_counts.get(expected_flow, 0) + 1
    
    print("\nTest case distribution:")
    for flow_type, count in flow_counts.items():
        print(f"  {flow_type}: {count} cases")
    
    # Run tests
    results = []
    session_id = f"extensive_test_{int(time.time())}"
    
    print(f"\nStarting extensive test with {len(test_cases)} cases...")
    
    for i, (description, message, expected_flow_type, expect_urgent) in enumerate(test_cases, 1):
        print(f"\nTest {i}/{len(test_cases)}: {description}")
        print(f"  Input: {message}")
        
        # Send to backend
        response = send_message_to_backend(message, session_id)
        
        # Extract flow type and urgency
        got_flow_type = response.get("flow_type", "unknown")
        got_urgent = response.get("urgent", False)
        
        # Determine if test passed
        flow_correct = got_flow_type == expected_flow_type
        urgent_correct = got_urgent == expect_urgent
        passed = flow_correct and urgent_correct
        
        print(f"  Expected flow: {expected_flow_type}, Got: {got_flow_type}")
        print(f"  Urgent expected: {expect_urgent}, Got: {got_urgent}")
        print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")
        
        # Store result
        results.append({
            'description': description,
            'message': message,
            'expected_flow_type': expected_flow_type,
            'expect_urgent': expect_urgent,
            'got_flow_type': got_flow_type,
            'got_urgent': got_urgent,
            'passed': passed,
            'response': response
        })
        
        # Progress indicator for large test sets
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(test_cases)} tests completed")
    
    # Calculate and display comprehensive metrics
    print("\n" + "="*60)
    print("EXTENSIVE TEST RESULTS")
    print("="*60)
    
    metrics = calculate_accuracy_metrics(results)
    
    print(f"\nOverall Accuracy: {metrics['overall_accuracy']:.2f}%")
    print(f"Total Tests: {metrics['total_tests']}")
    print(f"Total Correct: {metrics['total_correct']}")
    
    print(f"\nDetailed Metrics by Flow Type:")
    print("-" * 60)
    for flow_type, flow_metrics in metrics['flow_metrics'].items():
        print(f"{flow_type.upper()}:")
        print(f"  Total Cases: {flow_metrics['total_cases']}")
        print(f"  Flow Accuracy: {flow_metrics['flow_accuracy']:.2f}%")
        print(f"  Urgent Accuracy: {flow_metrics['urgent_accuracy']:.2f}%")
        print(f"  Overall Accuracy: {flow_metrics['overall_accuracy']:.2f}%")
        print()
    
    # Save detailed results to file
    results_file = f"extensive_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': metrics,
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    run_extensive_test() 