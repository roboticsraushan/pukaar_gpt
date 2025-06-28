# from vertexai.generative_models import GenerativeModel
# import vertexai

# PROJECT_ID = "pukaar-462607"
# LOCATION = "us-central1"

# vertexai.init(project=PROJECT_ID, location=LOCATION)

# model = GenerativeModel("gemini-2.0-flash-001")

# Initial system prompt manually added to history
TRIAGE_CONTEXT = """
You are a triage assistant for infant health screening. You must only use screening logic based on observational criteria that are scientifically validated by IMNCI, WHO, and IAP guidelines.

⚠️ Important: You must not offer a diagnosis. This tool is for screening potential signs only.

At the start of the session, clearly show this message to the user:
"This is not a medical diagnosis. It is a screening tool based on WHO, IMNCI, and IAP guidelines to help identify potential warning signs. Please consult a pediatrician if unsure."

Analyze the parent's free-text description and assign a likelihood (0–100%) to:
- Pneumonia / ARI
- Diarrhea
- Malnutrition
- Neonatal Sepsis
- Neonatal Jaundice
- Looks Normal

Return ranked list. If unrelated (e.g., teething, reflux), output:
{"screenable": false, "other_issue_detected": true, "response": "Please consult a pediatrician for evaluation."}
"""

# Mock implementation for testing without Google Cloud credentials
def triage_with_gemini(user_input: str) -> str:
    """Mock triage function for testing without Google Cloud credentials."""
    
    # Simple keyword-based screening logic
    input_lower = user_input.lower()
    
    # Check for common symptoms
    if any(word in input_lower for word in ['breathing', 'cough', 'chest', 'pneumonia']):
        return """{
            "pneumonia_ari": 75,
            "diarrhea": 10,
            "malnutrition": 5,
            "neonatal_sepsis": 15,
            "neonatal_jaundice": 5,
            "looks_normal": 20,
            "screenable": true,
            "response": "Fast breathing and chest symptoms detected. This could indicate respiratory issues. Please consult a pediatrician immediately."
        }"""
    
    elif any(word in input_lower for word in ['yellow', 'jaundice', 'skin']):
        return """{
            "pneumonia_ari": 5,
            "diarrhea": 10,
            "malnutrition": 5,
            "neonatal_sepsis": 15,
            "neonatal_jaundice": 85,
            "looks_normal": 10,
            "screenable": true,
            "response": "Yellow skin or eyes detected. This could indicate jaundice. Please consult a pediatrician for evaluation."
        }"""
    
    elif any(word in input_lower for word in ['diarrhea', 'loose', 'watery', 'stool']):
        return """{
            "pneumonia_ari": 5,
            "diarrhea": 80,
            "malnutrition": 15,
            "neonatal_sepsis": 10,
            "neonatal_jaundice": 5,
            "looks_normal": 15,
            "screenable": true,
            "response": "Diarrhea symptoms detected. Monitor for dehydration and consult a pediatrician if symptoms persist."
        }"""
    
    elif any(word in input_lower for word in ['feeding', 'not eating', 'weight']):
        return """{
            "pneumonia_ari": 10,
            "diarrhea": 15,
            "malnutrition": 70,
            "neonatal_sepsis": 20,
            "neonatal_jaundice": 5,
            "looks_normal": 10,
            "screenable": true,
            "response": "Feeding issues detected. This could indicate malnutrition or other underlying conditions. Please consult a pediatrician."
        }"""
    
    elif any(word in input_lower for word in ['fever', 'temperature', 'hot']):
        return """{
            "pneumonia_ari": 25,
            "diarrhea": 15,
            "malnutrition": 5,
            "neonatal_sepsis": 60,
            "neonatal_jaundice": 5,
            "looks_normal": 10,
            "screenable": true,
            "response": "Fever detected. This could indicate infection. Please consult a pediatrician immediately."
        }"""
    
    else:
        return """{
            "pneumonia_ari": 10,
            "diarrhea": 10,
            "malnutrition": 10,
            "neonatal_sepsis": 10,
            "neonatal_jaundice": 10,
            "looks_normal": 50,
            "screenable": true,
            "response": "Symptoms described are not clearly indicative of the conditions we screen for. Please consult a pediatrician for proper evaluation."
        }"""

# Original implementation (commented out for now)
# chat = model.start_chat(history=[])
# chat.send_message(TRIAGE_CONTEXT)

# def triage_with_gemini(user_input: str) -> str:
#     """Send a message to Gemini with triage guardrails."""
#     response = chat.send_message(user_input)
#     return response.text

print("==============================================================================================")
print("=================================Triage prompt as system context==============================")
print("==============================================================================================")
print(triage_with_gemini("My baby is not feeding and has yellow skin."))
print("==============================================================================================")
