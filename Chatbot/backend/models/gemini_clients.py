"""
Gemini Client Wrappers for Pukaar-GPT
Handles communication with different Gemini services
"""

import os
import json
import time
import logging
import asyncio
import google.generativeai as genai
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Gemini API
API_KEY = os.environ.get('GOOGLE_API_KEY')
if not API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables")
else:
    genai.configure(api_key=API_KEY)

# Default model
DEFAULT_MODEL = 'gemini-1.5-pro'

# Request timeouts
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Error types
class GeminiErrorType(Enum):
    TIMEOUT = "timeout"
    INVALID_RESPONSE = "invalid_response"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"

class GeminiBaseClient:
    """Base client for Gemini services"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
    def _validate_response(self, response: Any) -> bool:
        """Validate that the response is properly formatted"""
        return response and hasattr(response, 'text')
    
    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle different types of errors"""
        error_type = GeminiErrorType.UNKNOWN
        error_message = str(error)
        
        if "timeout" in error_message.lower():
            error_type = GeminiErrorType.TIMEOUT
        elif "rate limit" in error_message.lower():
            error_type = GeminiErrorType.RATE_LIMIT
        elif "authentication" in error_message.lower() or "api key" in error_message.lower():
            error_type = GeminiErrorType.AUTHENTICATION
        elif "service" in error_message.lower() and "unavailable" in error_message.lower():
            error_type = GeminiErrorType.SERVICE_UNAVAILABLE
            
        return {
            "error": True,
            "error_type": error_type.value,
            "error_message": error_message,
            "timestamp": time.time()
        }
    
    def call_with_retry(self, prompt: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Call Gemini with retry logic"""
        retries = 0
        last_error = None
        
        while retries < MAX_RETRIES:
            try:
                response = self.model.generate_content(prompt, timeout=timeout)
                
                if self._validate_response(response):
                    return {
                        "success": True,
                        "content": response.text,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Invalid response format from Gemini",
                        "timestamp": time.time()
                    }
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API call failed (attempt {retries+1}/{MAX_RETRIES}): {e}")
                retries += 1
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * retries)  # Exponential backoff
        
        return self._handle_error(last_error)
    
    async def call_async(self, prompt: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Asynchronous call to Gemini"""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, 
                lambda: self.call_with_retry(prompt, timeout)
            )


class ContextClassifierClient(GeminiBaseClient):
    """Client for context classification service"""
    
    SYSTEM_PROMPT = """
    You are a medical context classifier for a healthcare chatbot focused on infant and child health.
    Analyze the user's message and classify it into one of these categories:
    
    1. medical_screenable: Health concerns that can be screened using standard protocols (fever, cough, diarrhea, etc.)
    2. medical_non_screenable: Health concerns that require direct professional consultation (complex conditions, chronic issues)
    3. non_medical: Parenting questions, developmental concerns, or general inquiries not related to illness
    
    Return a JSON response with:
    {
        "classified_context": "medical_screenable|medical_non_screenable|non_medical",
        "confidence": 0-100,
        "reasoning": "Brief explanation of classification"
    }
    """
    
    def classify(self, user_input: str) -> Dict[str, Any]:
        """Classify the user input context"""
        prompt = f"{self.SYSTEM_PROMPT}\n\nUser message: {user_input}"
        response = self.call_with_retry(prompt)
        
        if response.get("success"):
            try:
                # Extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "classification": result,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Could not extract JSON from response",
                        "raw_response": content,
                        "timestamp": time.time()
                    }
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                    "error_message": "Invalid JSON in response",
                    "raw_response": response["content"],
                    "timestamp": time.time()
                }
        
        return response


class TriageClient(GeminiBaseClient):
    """Client for triage service"""
    
    SYSTEM_PROMPT = """
    You are a triage assistant for infant health screening. You must only use screening logic based on observational criteria that are scientifically validated by IMNCI, WHO, and IAP guidelines.

    ⚠️ Important: You must not offer a diagnosis. This tool is for screening potential signs only.

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
    
    def triage(self, user_input: str) -> Dict[str, Any]:
        """Perform triage analysis on user input"""
        prompt = f"{self.SYSTEM_PROMPT}\n\nParent's description: {user_input}"
        response = self.call_with_retry(prompt)
        
        if response.get("success"):
            try:
                # Extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "triage_result": result,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Could not extract JSON from response",
                        "raw_response": content,
                        "timestamp": time.time()
                    }
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                    "error_message": "Invalid JSON in response",
                    "raw_response": response["content"],
                    "timestamp": time.time()
                }
        
        return response


class RedFlagClient(GeminiBaseClient):
    """Client for red flag detection service"""
    
    SYSTEM_PROMPT = """
Red Flag GPT
You are a red flag detection agent responsible for identifying signs of medical emergencies in infants. Your output will stop all further conversation and trigger an emergency alert.

You must detect symptoms that match or strongly resemble red flag indicators defined in the IMNCI, WHO IMCI, IAP, or AIIMS pediatric emergency protocols.

⚠ If the user's language suggests a possible emergency, even without exact phrasing, raise the red flag. Parents may use imprecise or emotional language — interpret their intent conservatively using clinical knowledge.

However, do not raise a flag if the concern clearly falls outside these validated emergency categories.

Your goal is to avoid missing any serious case (false negatives), while not overwhelming the user with unnecessary alerts (false positives). When uncertain, prefer caution — if it could plausibly indicate a red flag, raise it.

Return:
{
  "red_flag_detected": true,
  "trigger": "Refusal to feed for over 6 hours",
  "recommended_action": "Rush to emergency immediately"
}
"""
    
    def detect_red_flags(self, user_input: str) -> Dict[str, Any]:
        """Detect red flags in user input"""
        prompt = f"{self.SYSTEM_PROMPT}\n\nParent's message: {user_input}"
        response = self.call_with_retry(prompt)
        
        if response.get("success"):
            try:
                # Extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "red_flag_result": result,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Could not extract JSON from response",
                        "raw_response": content,
                        "timestamp": time.time()
                    }
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                    "error_message": "Invalid JSON in response",
                    "raw_response": response["content"],
                    "timestamp": time.time()
                }
        
        return response


class ScreeningClient(GeminiBaseClient):
    """Client for detailed screening service"""
    
    SYSTEM_PROMPT = """
    You are a pediatric screening assistant specialized in detailed assessment of infant and child health concerns.
    
    Based on the provided condition and symptoms, perform a detailed screening assessment following IMNCI, WHO, and IAP guidelines.
    
    Return a JSON response with:
    {
        "condition": "condition_name",
        "risk_level": "high|medium|low|minimal",
        "urgency": "immediate|soon|routine|monitor",
        "assessment": "Detailed assessment of the symptoms",
        "recommendations": {
            "action": "Recommended action",
            "timeframe": "When to take action",
            "monitoring": "What to monitor",
            "warning_signs": "Signs that require immediate attention"
        }
    }
    """
    
    def screen_condition(self, condition: str, symptoms: List[str]) -> Dict[str, Any]:
        """Perform detailed screening for a specific condition"""
        symptoms_text = "\n".join([f"- {symptom}" for symptom in symptoms])
        prompt = f"{self.SYSTEM_PROMPT}\n\nCondition: {condition}\n\nSymptoms:\n{symptoms_text}"
        response = self.call_with_retry(prompt)
        
        if response.get("success"):
            try:
                # Extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "screening_result": result,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Could not extract JSON from response",
                        "raw_response": content,
                        "timestamp": time.time()
                    }
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                    "error_message": "Invalid JSON in response",
                    "raw_response": response["content"],
                    "timestamp": time.time()
                }
        
        return response


class AdviceClient(GeminiBaseClient):
    """Client for medical advice service"""
    
    SYSTEM_PROMPT = """
    You are a pediatric advice assistant providing evidence-based guidance for infant and child health concerns.
    
    Important: Do not diagnose conditions. Provide only general guidance based on scientifically validated information from reputable medical sources.
    
    For any serious concerns, always recommend consulting a healthcare professional.
    
    Return a JSON response with:
    {
        "advice": "General guidance on managing the condition",
        "home_care": "Appropriate home care measures if applicable",
        "when_to_consult": "Clear guidance on when to seek professional help",
        "prevention": "Preventive measures if applicable",
        "references": ["List of medical guidelines or sources used"]
    }
    """
    
    def get_advice(self, condition: str, user_input: str) -> Dict[str, Any]:
        """Get medical advice for a condition"""
        prompt = f"{self.SYSTEM_PROMPT}\n\nCondition: {condition}\n\nParent's concern: {user_input}"
        response = self.call_with_retry(prompt)
        
        if response.get("success"):
            try:
                # Extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "advice_result": result,
                        "model": self.model_name,
                        "timestamp": time.time()
                    }
                else:
                    return {
                        "error": True,
                        "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                        "error_message": "Could not extract JSON from response",
                        "raw_response": content,
                        "timestamp": time.time()
                    }
            except json.JSONDecodeError:
                return {
                    "error": True,
                    "error_type": GeminiErrorType.INVALID_RESPONSE.value,
                    "error_message": "Invalid JSON in response",
                    "raw_response": response["content"],
                    "timestamp": time.time()
                }
        
        return response 