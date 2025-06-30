from flask import Blueprint, request, jsonify
from models.gemini_direct import triage_with_gemini
from models.red_flag_model import detect_red_flags
from models.screening_model import run_screening
from models.context_classifier import classify_context
from models.consult_advice_model import get_consult_advice

screen_bp = Blueprint("screen", __name__)

@screen_bp.route("/api/triage", methods=["POST"])
def triage():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = triage_with_gemini(user_input)
        print(f"[DEBUG] result with screen : {result}")
        return jsonify({"result": result})
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
