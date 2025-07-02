"""
Orchestrator Service for Pukaar-GPT
Coordinates the flow between different Gemini services based on session state
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from concurrent.futures import ThreadPoolExecutor

from .session_manager import SessionManager, FLOW_TYPES
from .screening_flow import ScreeningFlow, ScreeningState
from models.gemini_clients import (
    ContextClassifierClient, 
    TriageClient, 
    RedFlagClient, 
    ScreeningClient, 
    AdviceClient
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    """Orchestrates the flow between different Gemini services"""
    
    def __init__(self):
        """Initialize the orchestrator with client instances"""
        self.context_client = ContextClassifierClient()
        self.triage_client = TriageClient()
        self.red_flag_client = RedFlagClient()
        self.screening_client = ScreeningClient()
        self.advice_client = AdviceClient()
        
    async def process_message(self, user_input: str = '', session_id: str = '', metadata: Dict = {}) -> Dict[str, Any]:
        """Process a user message through the appropriate flow"""
        user_input = user_input or ''
        session_id = session_id or ''
        metadata = metadata or {}
        start_time = time.time()
        
        # Create session if it doesn't exist
        if not session_id:
            session_id = SessionManager.create_session()
            logger.info(f"Created new session: {session_id}")
        
        # Get current session state
        session_data = SessionManager.get_session(session_id) or {}
        if not session_data:
            session_id = SessionManager.create_session()
            session_data = SessionManager.get_session(session_id) or {}
            logger.info(f"Created new session after failed retrieval: {session_id}")
        
        # Add user message to conversation history
        SessionManager.add_message_to_history(session_id, "user", user_input)
        
        # Get current state and flow type
        current_state = ScreeningFlow.get_current_state(session_id)
        flow_type = session_data.get('flow_type', FLOW_TYPES['INITIAL']) if isinstance(session_data, dict) else FLOW_TYPES['INITIAL']
        
        # Run red flag detection in parallel with other processing
        red_flag_future = asyncio.create_task(self._check_red_flags(user_input))
        
        # Process based on current flow type
        result = {}
        
        if flow_type == FLOW_TYPES['INITIAL']:
            # For initial messages, classify context first
            result = await self._handle_initial_flow(user_input, session_id)
        elif flow_type == FLOW_TYPES['TRIAGE']:
            # For triage flow, perform triage analysis
            result = await self._handle_triage_flow(user_input, session_id)
        elif flow_type == FLOW_TYPES['SCREENING']:
            # For screening flow, handle screening steps
            result = await self._handle_screening_flow(user_input, session_id, metadata)
        elif flow_type == FLOW_TYPES['RED_FLAG']:
            # For red flag flow, provide emergency guidance
            result = await self._handle_red_flag_flow(user_input, session_id)
        elif flow_type == FLOW_TYPES['FOLLOW_UP']:
            # For follow-up flow, handle follow-up questions
            result = await self._handle_follow_up_flow(user_input, session_id)
        else:
            # Default to initial flow for unknown flow types
            result = await self._handle_initial_flow(user_input, session_id)
        
        # Check red flag results
        red_flag_result = await red_flag_future or {}
        if red_flag_result.get("red_flag_result", {}).get("red_flag_detected", False):
            # Override with red flag flow if detected
            result = await self._handle_red_flag_detected(red_flag_result, session_id)
        
        # Add system response to conversation history
        if isinstance(result, dict) and "response" in result:
            SessionManager.add_message_to_history(session_id, "system", result["response"])
        
        # Add session info to result
        session_data = SessionManager.get_session(session_id) or {}
        result.update({
            "session_id": session_id,
            "flow_type": session_data.get('flow_type', FLOW_TYPES['INITIAL']) if isinstance(session_data, dict) else FLOW_TYPES['INITIAL'],
            "current_step": session_data.get('current_step', 0) if isinstance(session_data, dict) else 0,
            "processing_time": time.time() - start_time
        })
        
        return result
    
    async def _check_red_flags(self, user_input: str) -> Dict[str, Any]:
        """Check for red flags in user input"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(
                    executor,
                    lambda: self.red_flag_client.detect_red_flags(user_input)
                )
        except Exception as e:
            logger.error(f"Error in red flag detection: {e}")
            return {"error": True, "error_message": str(e)}
    
    async def _handle_initial_flow(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle the initial flow with context classification"""
        try:
            # Classify the context
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                classification_result = await loop.run_in_executor(
                    executor,
                    lambda: self.context_client.classify(user_input)
                )
            
            if not classification_result.get("success", False):
                return {
                    "error": True,
                    "error_message": "Failed to classify context",
                    "response": "I'm having trouble understanding your concern. Could you please provide more details?"
                }
            
            classification = classification_result.get("classification", {})
            classified_context = classification.get("classified_context", "medical_screenable")
            
            # Update session with classification result
            SessionManager.update_session(session_id, {
                "context_classification": classification
            })
            
            # Determine next flow based on classification
            if classified_context == "medical_screenable":
                # Transition to triage flow
                SessionManager.set_flow_type(session_id, FLOW_TYPES['TRIAGE'])
                
                # Perform triage
                triage_result = await self._handle_triage_flow(user_input, session_id)
                return triage_result
            
            elif classified_context == "medical_non_screenable":
                # For non-screenable medical concerns, provide advice
                advice_result = await loop.run_in_executor(
                    executor,
                    lambda: self.advice_client.get_advice("general", user_input)
                )
                
                if not advice_result.get("success", False):
                    return {
                        "error": True,
                        "error_message": "Failed to get advice",
                        "response": "I recommend consulting with a healthcare professional about this concern."
                    }
                
                advice = advice_result.get("advice_result", {})
                response = f"{advice.get('advice', '')}\n\n{advice.get('when_to_consult', '')}"
                
                return {
                    "success": True,
                    "classification": classification,
                    "advice": advice,
                    "response": response
                }
            
            else:  # non_medical
                # For non-medical concerns, provide general guidance
                advice_result = await loop.run_in_executor(
                    executor,
                    lambda: self.advice_client.get_advice("parenting", user_input)
                )
                
                if not advice_result.get("success", False):
                    return {
                        "error": True,
                        "error_message": "Failed to get advice",
                        "response": "This appears to be a general parenting question. I can provide general guidance, but for specific concerns, please consult with a healthcare professional."
                    }
                
                advice = advice_result.get("advice_result", {})
                response = advice.get('advice', 'This appears to be a general parenting question. I can provide general guidance, but for specific concerns, please consult with a healthcare professional.')
                
                return {
                    "success": True,
                    "classification": classification,
                    "advice": advice,
                    "response": response
                }
            
        except Exception as e:
            logger.error(f"Error in initial flow: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "I'm having trouble processing your request. Please try again."
            }
    
    async def _handle_triage_flow(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle the triage flow"""
        try:
            # Perform triage analysis
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                triage_result = await loop.run_in_executor(
                    executor,
                    lambda: self.triage_client.triage(user_input)
                )
            
            if not triage_result.get("success", False):
                return {
                    "error": True,
                    "error_message": "Failed to perform triage",
                    "response": "I'm having trouble analyzing your concern. Could you please provide more specific details about the symptoms?"
                }
            
            # Update session with triage result
            triage_data = triage_result.get("triage_result", {})
            SessionManager.update_session(session_id, {
                "triage_result": triage_data
            })
            
            # Check if screenable
            screenable = triage_data.get("screenable", True)
            
            if screenable:
                # Transition to screening flow if screenable
                SessionManager.set_flow_type(session_id, FLOW_TYPES['SCREENING'])
                
                # Determine the condition with highest score
                conditions = {
                    "Pneumonia / ARI": triage_data.get("Pneumonia / ARI", 0),
                    "Diarrhea": triage_data.get("Diarrhea", 0),
                    "Malnutrition": triage_data.get("Malnutrition", 0),
                    "Neonatal Sepsis": triage_data.get("Neonatal Sepsis", 0),
                    "Neonatal Jaundice": triage_data.get("Neonatal Jaundice", 0)
                }
                
                highest_condition = max(conditions.items(), key=lambda x: x[1])
                condition_name = highest_condition[0]
                condition_score = highest_condition[1]
                
                # Store selected condition in session
                SessionManager.update_session(session_id, {
                    "selected_condition": condition_name,
                    "condition_score": condition_score
                })
                
                response = triage_data.get("response", "Based on your description, I'd like to ask a few more questions to better understand the situation.")
                
                return {
                    "success": True,
                    "triage_data": triage_data,
                    "selected_condition": condition_name,
                    "condition_score": condition_score,
                    "response": response,
                    "result": triage_result.get("content", "")
                }
            else:
                # For non-screenable concerns, provide advice
                response = triage_data.get("response", "Based on your description, I recommend consulting with a healthcare professional.")
                
                return {
                    "success": True,
                    "triage_data": triage_data,
                    "screenable": False,
                    "response": response,
                    "result": triage_result.get("content", "")
                }
            
        except Exception as e:
            logger.error(f"Error in triage flow: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "I'm having trouble analyzing your concern. Please try again with more details about the symptoms."
            }
    
    async def _handle_screening_flow(self, user_input: str = '', session_id: str = '', metadata: Dict = {}) -> Dict[str, Any]:
        """Handle the screening flow based on the current step"""
        user_input = user_input or ''
        session_id = session_id or ''
        metadata = metadata or {}
        try:
            session_data = SessionManager.get_session(session_id) or {}
            current_step = session_data.get('current_step', 0) if isinstance(session_data, dict) else 0
            # Get selected condition from session
            selected_condition = session_data.get('selected_condition', '') if isinstance(session_data, dict) else ''
            if not selected_condition and metadata:
                selected_condition = metadata.get('condition', '') if isinstance(metadata, dict) else ''
            if not selected_condition:
                return {
                    "error": True,
                    "error_message": "No condition selected for screening",
                    "response": "I'm not sure which condition we're discussing. Could you please provide more details about the symptoms?"
                }
            # Handle different steps in the screening flow
            if current_step == 0:  # Condition selection
                # Condition already selected from triage, move to next step
                SessionManager.advance_step(session_id)
                return {
                    "success": True,
                    "selected_condition": selected_condition,
                    "response": f"I'd like to ask you some questions about {selected_condition}. Could you provide more details about the symptoms?"
                }
            elif current_step == 1:  # Question collection
                # Collect user responses
                responses = []
                if metadata and isinstance(metadata, dict) and 'responses' in metadata:
                    responses = metadata['responses']
                else:
                    responses = [user_input]
                # Store responses in session
                SessionManager.update_session(session_id, {
                    "screening_responses": responses
                })
                # Move to analysis step
                SessionManager.advance_step(session_id)
                # Perform screening analysis
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    screening_result = await loop.run_in_executor(
                        executor,
                        lambda: self.screening_client.screen_condition(selected_condition, responses)
                    )
                if not screening_result or not screening_result.get("success", False):
                    return {
                        "error": True,
                        "error_message": "Failed to analyze screening responses",
                        "response": "I'm having trouble analyzing your responses. Could you please provide more details?"
                    }
                # Store screening result in session
                screening_data = screening_result.get("screening_result", {}) if isinstance(screening_result, dict) else {}
                SessionManager.set_screening_data(session_id, selected_condition, screening_data)
                # Move to recommendation step
                SessionManager.advance_step(session_id)
                # Generate response with recommendations
                risk_level = screening_data.get("risk_level", "low") if isinstance(screening_data, dict) else "low"
                urgency = screening_data.get("urgency", "routine") if isinstance(screening_data, dict) else "routine"
                assessment = screening_data.get("assessment", "") if isinstance(screening_data, dict) else ""
                recommendations = screening_data.get("recommendations", {}) if isinstance(screening_data, dict) else {}
                response = f"Based on your description about {selected_condition}, here's my assessment:\n\n"
                response += f"{assessment}\n\n"
                response += f"Risk Level: {risk_level.capitalize()}\n"
                response += f"Recommended Action: {recommendations.get('action', '')}\n"
                response += f"Timeframe: {recommendations.get('timeframe', '')}\n\n"
                response += f"Things to monitor: {recommendations.get('monitoring', '')}\n"
                response += f"Warning signs: {recommendations.get('warning_signs', '')}"
                return {
                    "success": True,
                    "screening_data": screening_data,
                    "selected_condition": selected_condition,
                    "response": response
                }
            else:  # Other steps (analysis, recommendation already handled)
                # Provide advice based on previous screening
                screening_data_dict = session_data.get('screening_data', {}) if isinstance(session_data, dict) else {}
                screening_data = screening_data_dict.get(selected_condition, {}) if isinstance(screening_data_dict, dict) else {}
                if not screening_data:
                    return {
                        "error": True,
                        "error_message": "No screening data available",
                        "response": "I don't have enough information to provide specific guidance. Could you please describe the symptoms again?"
                    }
                # Get additional advice
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    advice_result = await loop.run_in_executor(
                        executor,
                        lambda: self.advice_client.get_advice(selected_condition, user_input)
                    )
                if not advice_result or not advice_result.get("success", False):
                    # Fallback to existing screening data
                    recommendations = screening_data.get("recommendations", {}) if isinstance(screening_data, dict) else {}
                    response = f"For {selected_condition}, I recommend:\n\n"
                    response += f"- {recommendations.get('action', 'Consult with a healthcare professional')}\n"
                    response += f"- {recommendations.get('monitoring', 'Monitor symptoms closely')}"
                    return {
                        "success": True,
                        "screening_data": screening_data,
                        "selected_condition": selected_condition,
                        "response": response
                    }
                # Combine screening data with advice
                advice_data = advice_result.get("advice_result", {}) if advice_result else {}
                response = f"Regarding {selected_condition}:\n\n"
                response += f"{advice_data.get('advice', '')}\n\n"
                response += f"Home care: {advice_data.get('home_care', '')}\n\n"
                response += f"When to consult a doctor: {advice_data.get('when_to_consult', '')}"
                return {
                    "success": True,
                    "screening_data": screening_data,
                    "advice_data": advice_data,
                    "selected_condition": selected_condition,
                    "response": response
                }
            
        except Exception as e:
            logger.error(f"Error in screening flow: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "I'm having trouble processing your screening information. Please try again."
            }
    
    async def _handle_red_flag_flow(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle the red flag flow"""
        try:
            session_data = SessionManager.get_session(session_id) or {}
            red_flags = session_data.get('red_flags', []) if isinstance(session_data, dict) else []
            if not red_flags:
                # No red flags found, revert to triage flow
                SessionManager.set_flow_type(session_id, FLOW_TYPES['TRIAGE'])
                return await self._handle_triage_flow(user_input, session_id)
            # Get the most recent red flag
            latest_red_flag = red_flags[-1] if isinstance(red_flags, list) and red_flags else {}
            # Get additional advice for the emergency
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                advice_result = await loop.run_in_executor(
                    executor,
                    lambda: self.advice_client.get_advice("emergency", user_input)
                )
            if not advice_result or not advice_result.get("success", False):
                # Fallback to red flag data
                reasoning = latest_red_flag.get('reasoning', 'This appears to be an emergency situation.') if isinstance(latest_red_flag, dict) else 'This appears to be an emergency situation.'
                recommendation = latest_red_flag.get('recommendation', 'Please seek immediate medical attention.') if isinstance(latest_red_flag, dict) else 'Please seek immediate medical attention.'
                response = f"URGENT: {reasoning}\n\n"
                response += f"Recommendation: {recommendation}"
                return {
                    "success": True,
                    "red_flag": latest_red_flag,
                    "response": response
                }
            # Combine red flag with advice
            advice_data = advice_result.get("advice_result", {}) if advice_result else {}
            reasoning = latest_red_flag.get('reasoning', 'This appears to be an emergency situation.') if isinstance(latest_red_flag, dict) else 'This appears to be an emergency situation.'
            recommendation = latest_red_flag.get('recommendation', 'Please seek immediate medical attention.') if isinstance(latest_red_flag, dict) else 'Please seek immediate medical attention.'
            response = f"URGENT: {reasoning}\n\n"
            response += f"Recommendation: {recommendation}\n\n"
            response += f"While seeking help: {advice_data.get('home_care', '')}"
            return {
                "success": True,
                "red_flag": latest_red_flag,
                "advice_data": advice_data,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error in red flag flow: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "This appears to be an urgent situation. Please seek immediate medical attention."
            }
    
    async def _handle_follow_up_flow(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Handle the follow-up flow with full context and safety checks"""
        try:
            session_data = SessionManager.get_session(session_id) or {}
            if not session_data:
                return {
                    "error": True,
                    "error_message": "Session not found",
                    "response": "Session not found. Please start a new session."
                }
            # Gather context
            selected_condition = session_data.get('selected_condition', '') or ''
            triage_result = session_data.get('triage_result', {}) or {}
            screening_data = session_data.get('screening_data', {}) or {}
            red_flags = session_data.get('red_flags', []) or []
            conversation_history = session_data.get('conversation_history', []) or []

            # Build a context-rich prompt for Gemini
            context_lines = []
            if selected_condition:
                context_lines.append(f"- Main condition: {selected_condition}")
            if triage_result:
                context_lines.append(f"- Triage result: {triage_result}")
            if screening_data:
                context_lines.append(f"- Screening data: {screening_data}")
            if red_flags:
                context_lines.append(f"- Red flags: {red_flags}")
            context_lines.append(f"- Previous conversation: {[{'role': m.get('role', ''), 'content': m.get('content', '')} for m in conversation_history[-5:]]}")
            context_lines.append(f"- Parent follow-up question: {user_input}")
            context_lines.append("Instructions: Provide clear, safe, evidence-based advice. If the follow-up question suggests a new red flag, escalate and recommend immediate medical attention.")
            prompt = "\n".join(context_lines)

            # Red flag check on follow-up question
            red_flag_result = self.red_flag_client.detect_red_flags(user_input) or {}
            if red_flag_result.get('red_flag_detected'):
                # Escalate to red flag flow
                SessionManager.set_flow_type(session_id, 'red_flag')
                SessionManager.add_red_flag(session_id, red_flag_result)
                response = f"⚠️ URGENT: {red_flag_result.get('reasoning', 'This appears to be an emergency situation.')}\n\nRecommendation: {red_flag_result.get('recommendation', 'Please seek immediate medical attention.')}"
                SessionManager.add_message_to_history(session_id, "system", response)
                return {
                    "success": True,
                    "response": response,
                    "flow_type": "red_flag",
                    "red_flag": red_flag_result
                }

            # Call Gemini for follow-up advice
            advice_result = self.advice_client.get_advice(selected_condition if selected_condition else "follow_up", prompt) or {}
            if not advice_result.get("success", False):
                return {
                    "error": True,
                    "error_message": "Failed to get follow-up advice",
                    "response": "For follow-up concerns, I recommend consulting with your healthcare provider."
                }
            advice_data = advice_result.get("advice_result", {}) or {}
            response = f"{advice_data.get('advice', '')}\n\nFor ongoing care: {advice_data.get('home_care', '')}\n\nWhen to consult again: {advice_data.get('when_to_consult', '')}"
            # Update session with follow-up Q&A
            SessionManager.add_message_to_history(session_id, "user", user_input)
            SessionManager.add_message_to_history(session_id, "system", response)
            SessionManager.set_flow_type(session_id, 'follow_up')
            return {
                "success": True,
                "advice_data": advice_data,
                "response": response,
                "flow_type": "follow_up"
            }
        except Exception as e:
            logger.error(f"Error in follow-up flow: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "For follow-up concerns, I recommend consulting with your healthcare provider."
            }
    
    async def _handle_red_flag_detected(self, red_flag_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle when a red flag is detected"""
        try:
            red_flag_data = red_flag_result.get("red_flag_result", {})
            
            # Add red flag to session
            SessionManager.add_red_flag(session_id, red_flag_data)
            
            # Transition to red flag flow
            SessionManager.set_flow_type(session_id, FLOW_TYPES['RED_FLAG'])
            
            # Generate response for red flag
            emergency_level = red_flag_data.get("emergency_level", "high")
            reasoning = red_flag_data.get("reasoning", "This appears to be an emergency situation.")
            recommendation = red_flag_data.get("recommendation", "Please seek immediate medical attention.")
            
            response = f"URGENT: {reasoning}\n\n"
            response += f"Recommendation: {recommendation}"
            
            if emergency_level == "high":
                response += "\n\nPlease seek immediate emergency care."
            elif emergency_level == "medium":
                response += "\n\nPlease contact your healthcare provider right away."
            else:
                response += "\n\nPlease consult with a healthcare provider as soon as possible."
            
            return {
                "success": True,
                "red_flag": red_flag_data,
                "emergency_level": emergency_level,
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error handling red flag: {e}")
            return {
                "error": True,
                "error_message": str(e),
                "response": "This appears to be an urgent situation. Please seek immediate medical attention."
            }