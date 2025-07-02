import requests
import time

API_URL = "http://localhost:5000/api/screen"

# Test cases: (description, message, expected_flow_type, expect_urgent)
test_cases = [
    # Follow-up Flow (should trigger Gemini, not a placeholder)
    ("Follow-up: checkup", "We were told to come back for a checkup after 2 days.", "follow_up", False),
    ("Follow-up: diarrhea not improved", "The diarrhea has not improved after 3 days of treatment.", "follow_up", False),
    ("Follow-up: antibiotics + fever", "My child was given antibiotics, but the fever is still there.", "follow_up", False),
    ("Follow-up: cough after medicine", "We finished the medicine, but my baby is still coughing.", "follow_up", False),
    ("Follow-up: rash follow-up", "The doctor asked us to follow up if the rash did not improve.", "follow_up", False),

    # Consult/Advice Flow (should trigger Gemini, not a placeholder)
    ("Consult: paracetamol", "Should I give paracetamol for fever?", "consult", False),
    ("Consult: water at 4 months", "Is it safe to give my baby water at 4 months?", "consult", False),
    ("Consult: feeding for diarrhea", "What should I feed my child with diarrhea?", "consult", False),
    ("Consult: prevent dehydration", "How can I prevent dehydration in my baby?", "consult", False),
    ("Consult: when to hospital", "When should I take my child to the hospital?", "consult", False),
    ("Consult: ibuprofen", "Can I give ibuprofen to my 1-year-old?", "consult", False),

    # Triage/Initial Flow (should remain in triage, not advance to screening)
    ("Initial: vague concern", "My baby is not feeling well.", "triage", False),
    ("Initial: health concern", "I have a health concern about my 2-year-old.", "triage", False),
    ("Initial: help request", "Can you help me with my child's symptoms?", "triage", False),

    # Red Flag/Emergency (should trigger urgent alert)
    ("Red flag: not waking up + fast breathing", "My baby is not waking up and is breathing very fast.", "red_flag", True),
    ("Red flag: seizure + not responding", "My child had a seizure and is not responding.", "red_flag", True),
    ("Red flag: unconscious after fall", "My child fell and is now unconscious.", "red_flag", True),
    ("Red flag: grunting + trouble breathing", "My baby is having trouble breathing and making grunting noises.", "red_flag", True),

    # Non-Urgent/Benign (should NOT trigger red flag)
    ("Non-urgent: mild cold", "My child has a mild cold but is playing normally.", "triage", False),
    ("Non-urgent: sneezing", "My baby sneezes a lot but has no fever.", "triage", False),
    ("Non-urgent: small bruise", "My child has a small bruise from falling.", "triage", False),
]

def run_tests():
    print("\n--- Pukaar-GPT End-to-End Flow Test ---\n")
    session_id = None
    for idx, (desc, msg, expected_flow, expect_urgent) in enumerate(test_cases):
        payload = {
            "message": msg,
            "sessionId": session_id if session_id else None,
        }
        print(f"Test {idx+1}: {desc}")
        r = requests.post(API_URL, json=payload)
        try:
            data = r.json()
        except Exception as e:
            print(f"  [FAIL] Could not parse JSON: {e}")
            continue
        # Save session_id for continuity
        if data.get("session_id"):
            session_id = data["session_id"]
        elif data.get("sessionId"):
            session_id = data["sessionId"]
        # Check flow type
        flow_type = data.get("flow_type") or data.get("flowType")
        urgent = False
        if flow_type == "red_flag" or (data.get("message") and ("URGENT" in data["message"] or "⚠️" in data["message"])):
            urgent = True
        # Print and assert
        print(f"  Input: {msg}")
        print(f"  Expected flow: {expected_flow}, Got: {flow_type}")
        print(f"  Urgent expected: {expect_urgent}, Got: {urgent}")
        print(f"  Response: {data.get('message') or data.get('response')}")
        try:
            assert (expected_flow == flow_type or (expected_flow == "triage" and flow_type in ["triage", "screening"]))
            assert urgent == expect_urgent
            print("  [PASS]")
        except AssertionError:
            print("  [FAIL] Flow or urgency mismatch!")
        print("-")
        time.sleep(0.5)  # To avoid flooding the server

if __name__ == "__main__":
    run_tests() 