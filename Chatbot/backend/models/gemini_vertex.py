from vertexai.generative_models import GenerativeModel
import vertexai
import google.auth

PROJECT_ID = "pkr-prod-in-core"
LOCATION = "us-central1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
            "https://www.googleapis.com/auth/aiplatform"
        ]
    )[0]
)

model = GenerativeModel("gemini-1.5-pro-001")

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

def triage_with_gemini(user_input: str) -> str:
    """Call Gemini 2.0 Flash model for nuanced, context-aware triage response."""
    try:
        prompt = f"{TRIAGE_CONTEXT}\n\nParent's description: {user_input}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"{{'error': 'Failed to get response from Gemini model', 'details': '{str(e)}'}}"

# Original implementation (commented out for now)
# chat = model.start_chat(history=[])
# chat.send_message(TRIAGE_CONTEXT)

# def triage_with_gemini(user_input: str) -> str:
#     """Send a message to Gemini with triage guardrails."""
#     response = chat.send_message(user_input)
#     return response.text
