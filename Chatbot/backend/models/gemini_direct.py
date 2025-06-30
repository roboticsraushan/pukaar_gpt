import google.generativeai as genai
import os
import json
import re

# Configure the API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Use Gemini Pro model
model = genai.GenerativeModel('gemini-1.5-pro')

# Initial system prompt
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

Return a JSON response with these percentages and a brief explanation. If unrelated (e.g., teething, reflux), output:
{"screenable": false, "other_issue_detected": true, "response": "Please consult a pediatrician for evaluation."}
"""

def triage_with_gemini(user_input: str) -> str:
    """Call Gemini model for nuanced, context-aware triage response."""
    try:
        prompt = f"{TRIAGE_CONTEXT}\n\nParent's description: {user_input}"
        response = model.generate_content(prompt)
        response_text = response.text
        # Extract the first JSON object from the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json_match.group(0)
        return json.dumps({
            "screenable": False,
            "other_issue_detected": True,
            "response": "Unable to process the response. Please try again."
        })
    except Exception as e:
        return json.dumps({
            "error": "Failed to get response from Gemini model",
            "details": str(e)
        }) 