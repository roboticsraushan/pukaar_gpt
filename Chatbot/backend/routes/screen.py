from flask import Blueprint, request, jsonify
from models.gemini_direct import triage_with_gemini
from models.red_flag_model import detect_red_flags
from models.screening_model import run_screening
from models.context_classifier import classify_context
from models.consult_advice_model import get_consult_advice
from functions.session_manager import SessionManager
from functions.screening_flow import ScreeningFlow, ScreeningState
import uuid

screen_bp = Blueprint("screen", __name__)

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
        
        # Process based on flow type
        if flow_type == "initial":
            # Initial flow - start triage
            SessionManager.set_flow_type(session_id, "initial")
            ScreeningFlow.transition_to(session_id, ScreeningState.INITIAL)
            response["message"] = "Welcome to Pukaar-GPT. Please describe the symptoms or concerns."
            
        elif flow_type == "triage":
            # Triage flow - analyze symptoms and determine next steps
            SessionManager.set_flow_type(session_id, "triage")
            ScreeningFlow.transition_to(session_id, ScreeningState.TRIAGE)
            
            # Check for red flags first
            red_flag_result = detect_red_flags(user_message)
            if red_flag_result["red_flag_detected"]:
                # Red flag detected, transition to red flag state
                ScreeningFlow.transition_to(session_id, ScreeningState.RED_FLAG_DETECTED)
                SessionManager.add_red_flag(session_id, red_flag_result)
                
                response["message"] = "⚠️ URGENT: Red flag detected! Please seek immediate medical attention."
                response["data"] = red_flag_result
            else:
                # No red flags, perform triage
                triage_result = triage_with_gemini(user_message)
                
                # Store triage result in session
                SessionManager.update_session(
                    session_id,
                    {"triage_result": triage_result}
                )
                
                # Transition to condition selection
                ScreeningFlow.transition_to(session_id, ScreeningState.CONDITION_SELECTION)
                
                response["message"] = "Triage completed. Please select a condition to screen for."
                response["data"] = triage_result
        
        elif flow_type == "screening":
            # Screening flow - handle condition screening
            SessionManager.set_flow_type(session_id, "screening")
            
            # Get condition from metadata
            condition = metadata.get("condition", "")
            if not condition:
                response["success"] = False
                response["message"] = "Condition is required for screening flow"
                return jsonify(response), 400
            
            # Store selected condition
            SessionManager.update_session(
                session_id,
                {"selected_condition": condition}
            )
            
            # Get current state
            current_state = ScreeningFlow.get_current_state(session_id)
            
            if current_state == ScreeningState.CONDITION_SELECTION:
                # Transition to question collection
                ScreeningFlow.transition_to(session_id, ScreeningState.QUESTION_COLLECTION)
                
                # Get screening questions for the condition
                screening_info = run_screening(condition)
                
                response["message"] = f"Please answer the questions for {condition} screening."
                response["data"] = screening_info
                
            elif current_state == ScreeningState.QUESTION_COLLECTION:
                # Get user responses from metadata
                user_responses = metadata.get("responses", [])
                if not user_responses:
                    response["success"] = False
                    response["message"] = "Responses are required for question collection"
                    return jsonify(response), 400
                
                # Check for red flags in responses
                for resp in user_responses:
                    red_flag_result = detect_red_flags(resp)
                    if red_flag_result["red_flag_detected"]:
                        # Red flag detected, transition to red flag state
                        ScreeningFlow.transition_to(session_id, ScreeningState.RED_FLAG_DETECTED)
                        SessionManager.add_red_flag(session_id, red_flag_result)
                        
                        response["message"] = "⚠️ URGENT: Red flag detected in your responses! Please seek immediate medical attention."
                        response["data"] = red_flag_result
                        break
                else:
                    # No red flags, proceed with screening
                    ScreeningFlow.transition_to(session_id, ScreeningState.ANALYSIS)
                    
                    # Run screening with user responses
                    screening_result = run_screening(condition, user_responses)
                    
                    # Store screening result
                    SessionManager.set_screening_data(session_id, condition, screening_result)
                    
                    # Transition to recommendation
                    ScreeningFlow.transition_to(session_id, ScreeningState.RECOMMENDATION)
                    
                    response["message"] = "Screening completed. Here are the results."
                    response["data"] = screening_result
        
        elif flow_type == "red_flag":
            # Red flag flow - handle red flag scenarios
            SessionManager.set_flow_type(session_id, "red_flag")
            ScreeningFlow.transition_to(session_id, ScreeningState.RED_FLAG_DETECTED)
            
            # Resume session after red flag
            resume_result = ScreeningFlow.handle_red_flag_resume(session_id)
            
            response["message"] = "Red flag session resumed. Please seek immediate medical attention."
            response["data"] = resume_result
        
        elif flow_type == "follow_up":
            # Follow-up flow - handle follow-up actions
            SessionManager.set_flow_type(session_id, "follow_up")
            ScreeningFlow.transition_to(session_id, ScreeningState.FOLLOW_UP)
            
            # Process follow-up message
            if user_message:
                follow_up_result = get_consult_advice(user_message)
                
                # Store follow-up result
                SessionManager.update_session(
                    session_id,
                    {"follow_up_result": follow_up_result}
                )
                
                response["message"] = "Follow-up processed. Here is the consultation advice."
                response["data"] = follow_up_result
            else:
                response["message"] = "Please provide follow-up information."
        
        # Add system response to conversation history
        SessionManager.add_message_to_history(
            session_id,
            "system",
            response["message"],
            {"flow_type": flow_type, "data": response["data"]}
        )
        
        # Get next action based on current state
        response["nextAction"] = ScreeningFlow.get_next_action(session_id)
        
        return jsonify(response)
        
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
