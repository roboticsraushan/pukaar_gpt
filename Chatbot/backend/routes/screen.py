from flask import Blueprint, request, jsonify
from models.gemini_direct import triage_with_gemini
from models.red_flag_model import detect_red_flags
from models.screening_model import run_screening
from models.context_classifier import classify_context
from models.consult_advice_model import get_consult_advice
from functions.session_manager import SessionManager
from functions.screening_flow import ScreeningFlow, ScreeningState
import uuid
from models.gemini_clients import AdviceClient

screen_bp = Blueprint("screen", __name__)

advice_client = AdviceClient()

@screen_bp.route("/api/triage", methods=["POST"])
def triage():
    data = request.get_json()
    user_input = data.get("message", "")
    session_id = data.get("session_id", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Create or get session
        if not session_id:
            session_id = SessionManager.create_session()
            
        # Get or create session data
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            session_id = SessionManager.create_session()
            session_data = SessionManager.get_session(session_id)
        
        # Add user message to conversation history
        SessionManager.add_message_to_history(session_id, "user", user_input)
        
        # Check for red flags first
        red_flag_result = detect_red_flags(user_input)
        print(f"[DEBUG] Red flag detection result: {red_flag_result}")
        
        if red_flag_result.get("red_flag_detected", False):
            # Red flag detected, set flow type to red_flag
            print(f"[DEBUG] Red flag detected in message: {user_input}")
            SessionManager.set_flow_type(session_id, "red_flag")
            SessionManager.add_red_flag(session_id, red_flag_result)
            
            # Prepare red flag response
            response_text = f"⚠️ URGENT: {red_flag_result.get('reasoning', 'This appears to be an emergency situation.')}\n\n"
            response_text += f"Recommendation: {red_flag_result.get('recommendation', 'Please seek immediate medical attention.')}"
            
            # Add system response to conversation history
            SessionManager.add_message_to_history(session_id, "system", response_text)
            
            # Get updated session data
            session_data = SessionManager.get_session(session_id)
            flow_type = session_data.get('flow_type', 'red_flag')
            current_step = session_data.get('current_step', 0)
            
            # Prepare response with session information
            response = {
                "result": response_text,
                "session_id": session_id,
                "flow_type": flow_type,
                "current_step": current_step,
                "response": response_text,
                "red_flag": red_flag_result
            }
            
            print(f"[DEBUG] Red flag response with session info: {response}")
            return jsonify(response)
        
        # No red flags, proceed with triage
        # Set flow type to triage and advance step
        SessionManager.set_flow_type(session_id, "triage")
        current_step = SessionManager.advance_step(session_id)
        
        # Get triage result
        result = triage_with_gemini(user_input)
        
        # Add system response to conversation history
        SessionManager.add_message_to_history(session_id, "system", result)
        
        # Get updated session data
        session_data = SessionManager.get_session(session_id)
        flow_type = session_data.get('flow_type', 'triage')
        current_step = session_data.get('current_step', 0)
        
        # Prepare response with session information
        response = {
            "result": result,
            "session_id": session_id,
            "flow_type": flow_type,
            "current_step": current_step,
            "response": result
        }
        
        print(f"[DEBUG] Triage response with session info: {response}")
        return jsonify(response)
    except Exception as e:
        print(f"[ERROR] : {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/red-flag", methods=["POST"])
def red_flag_detection():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = detect_red_flags(user_input)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Red flag detection: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/screening/<condition>", methods=["GET"])
def get_screening_info(condition):
    """Get screening information and questions for a specific condition."""
    try:
        result = run_screening(condition)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Screening info: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/screening/<condition>/run", methods=["POST"])
def run_screening_condition(condition):
    """Run screening for a specific condition with user responses."""
    data = request.get_json()
    user_responses = data.get("responses", [])

    if not user_responses:
        return jsonify({"error": "Responses are required"}), 400

    try:
        result = run_screening(condition, user_responses)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Screening run: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/context-classifier", methods=["POST"])
def context_classification():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = classify_context(user_input)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Context classification: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/consult-advice", methods=["POST"])
def consult_advice():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = get_consult_advice(user_input)
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Consult advice: {e}")
        return jsonify({"error": str(e)}), 500

# --- Modular handler functions for each flow ---
def handle_triage(user_message, session_id, session):
    result = triage_with_gemini(user_message)
    # TODO: Add logic to check if a condition is identified and transition to screening
    SessionManager.set_flow_type(session_id, "triage")
    return {"message": result, "flow_type": "triage"}

def handle_screening(user_message, session_id, session):
    # TODO: Implement stepwise screening logic
    SessionManager.set_flow_type(session_id, "screening")
    return {"message": "Screening in progress (stub)", "flow_type": "screening"}

def handle_follow_up(user_message, session_id, session):
    result = triage_with_gemini(user_message)
    SessionManager.set_flow_type(session_id, "follow_up")
    return {"message": result, "flow_type": "follow_up"}

def handle_consult(user_message, session_id, session):
    result = advice_client.get_advice("general", user_message)
    advice_text = None
    if isinstance(result, dict):
        advice_text = result.get("advice_result", {}).get("advice")
    if not advice_text:
        advice_text = str(result)
    SessionManager.set_flow_type(session_id, "consult")
    return {"message": advice_text, "flow_type": "consult"}

def handle_developmental(user_message, session_id, session):
    # TODO: Implement developmental concerns logic
    SessionManager.set_flow_type(session_id, "developmental")
    return {"message": "Developmental concerns (stub)", "flow_type": "developmental"}

def handle_reassurance(user_message, session_id, session):
    # TODO: Implement reassurance logic
    SessionManager.set_flow_type(session_id, "reassurance")
    return {"message": "Reassurance and home care advice (stub)", "flow_type": "reassurance"}

def urgent_response(red_flag_result, session_id):
    SessionManager.set_flow_type(session_id, "red_flag")
    return {
        "flow_type": "red_flag",
        "message": red_flag_result.get("recommended_action", "URGENT: Seek emergency care immediately."),
        "urgent": True,
        "trigger": red_flag_result.get("trigger", "Red flag detected")
    }

# --- Main /api/screen logic ---
@screen_bp.route("/api/screen", methods=["POST"])
def screen():
    """
    Main screening endpoint with session management
    
    Request body:
    {
        "message": "User message",
        "flowType": "initial|triage|screening|red_flag|follow_up",
        "sessionId": "optional-session-id",
        "metadata": {
            "condition": "optional condition name",
            "responses": ["optional user responses"],
            "additional_data": {}
        }
    }
    """
    data = request.get_json()
    user_message = data.get("message", "")
    flow_type = data.get("flowType", "initial")
    session_id = data.get("sessionId", "")
    metadata = data.get("metadata", {})
    
    # Initialize response object
    response = {
        "success": True,
        "message": "",
        "data": {},
        "sessionId": session_id,
        "nextAction": {}
    }
    
    try:
        # Handle session management
        if not session_id:
            # Create a new session
            session_id = SessionManager.create_session()
            response["sessionId"] = session_id
            print(f"[INFO] Created new session: {session_id}")
        else:
            # Verify session exists
            session_data = SessionManager.get_session(session_id)
            if not session_data:
                # Session not found, create a new one
                session_id = SessionManager.create_session()
                response["sessionId"] = session_id
                print(f"[INFO] Session not found, created new session: {session_id}")
        
        # Add user message to conversation history if provided
        if user_message:
            SessionManager.add_message_to_history(
                session_id, 
                "user", 
                user_message,
                {"flow_type": flow_type, "metadata": metadata}
            )
        
        # --- Always check for red flags on every message ---
        if user_message:
            red_flag_result = detect_red_flags(user_message) or {}
            if red_flag_result.get("red_flag_detected", False):
                ScreeningFlow.transition_to(session_id, ScreeningState.RED_FLAG_DETECTED)
                SessionManager.set_flow_type(session_id, "red_flag")
                SessionManager.add_red_flag(session_id, red_flag_result)
                response["message"] = "⚠️ URGENT: Red flag detected! Please seek immediate medical attention."
                response["data"] = red_flag_result
                SessionManager.add_message_to_history(
                    session_id,
                    "system",
                    response["message"],
                    {"flow_type": "red_flag", "data": red_flag_result}
                )
                # Always include flow_type and current_step
                session_data = SessionManager.get_session(session_id) or {}
                response["flow_type"] = session_data.get("flow_type")
                response["current_step"] = session_data.get("current_step")
                response["nextAction"] = ScreeningFlow.get_next_action(session_id)
                return jsonify(response)

        # --- Use context classifier to determine flow type before Gemini ---
        context_result = classify_context(user_message)
        context_type = context_result.get("classified_context", "medical_screenable")
        session = SessionManager.get_session(session_id) or {}
        flow_type = session.get("flow_type", "initial")
        if context_type == "follow_up":
            return handle_follow_up(user_message, session_id, session or {})
        elif context_type == "consult":
            return handle_consult(user_message, session_id, session or {})
        elif context_type == "developmental":
            return handle_developmental(user_message, session_id, session or {})
        elif context_type == "reassurance":
            return handle_reassurance(user_message, session_id, session or {})
        elif context_type == "medical_screenable":
            # If already in screening, continue; else, start screening
            if (session or {}).get("flow_type", "initial") != "screening":
                SessionManager.set_flow_type(session_id, "screening")
                ScreeningFlow.transition_to(session_id, ScreeningState.CONDITION_SELECTION)
            return handle_screening(user_message, session_id, session or {})
        else:
            # Default to triage if unsure
            return handle_triage(user_message, session_id, session or {})
        
    except Exception as e:
        print(f"[ERROR] Screen endpoint: {e}")
        response["success"] = False
        response["message"] = f"An error occurred: {str(e)}"
        return jsonify(response), 500

@screen_bp.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    """Get session data by session ID"""
    try:
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({"error": "Session not found"}), 404
            
        return jsonify({"success": True, "session": session_data})
    except Exception as e:
        print(f"[ERROR] Get session: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/session/<session_id>/history", methods=["GET"])
def get_session_history(session_id):
    """Get conversation history for a session"""
    try:
        history = SessionManager.get_conversation_history(session_id)
        if history is None:
            return jsonify({"error": "Session not found"}), 404
            
        return jsonify({"success": True, "history": history})
    except Exception as e:
        print(f"[ERROR] Get session history: {e}")
        return jsonify({"error": str(e)}), 500

@screen_bp.route("/api/session", methods=["POST"])
def create_session():
    """Create a new session"""
    try:
        session_id = SessionManager.create_session()
        return jsonify({"success": True, "sessionId": session_id})
    except Exception as e:
        print(f"[ERROR] Create session: {e}")
        return jsonify({"error": str(e)}), 500
