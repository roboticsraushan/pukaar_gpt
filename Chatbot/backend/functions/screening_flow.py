"""
Screening Flow State Machine
Manages the state transitions for the screening process
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from .session_manager import SessionManager, FLOW_TYPES

# Define screening flow states
class ScreeningState(Enum):
    INITIAL = "initial"
    TRIAGE = "triage"
    CONDITION_SELECTION = "condition_selection"
    QUESTION_COLLECTION = "question_collection"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    RED_FLAG_DETECTED = "red_flag_detected"
    FOLLOW_UP = "follow_up"
    COMPLETED = "completed"
    ERROR = "error"

# Define screening flow transitions
TRANSITIONS = {
    ScreeningState.INITIAL: [ScreeningState.TRIAGE],
    ScreeningState.TRIAGE: [
        ScreeningState.CONDITION_SELECTION, 
        ScreeningState.RED_FLAG_DETECTED
    ],
    ScreeningState.CONDITION_SELECTION: [ScreeningState.QUESTION_COLLECTION],
    ScreeningState.QUESTION_COLLECTION: [
        ScreeningState.ANALYSIS, 
        ScreeningState.RED_FLAG_DETECTED
    ],
    ScreeningState.ANALYSIS: [ScreeningState.RECOMMENDATION],
    ScreeningState.RECOMMENDATION: [
        ScreeningState.FOLLOW_UP, 
        ScreeningState.COMPLETED
    ],
    ScreeningState.RED_FLAG_DETECTED: [ScreeningState.COMPLETED],
    ScreeningState.FOLLOW_UP: [ScreeningState.COMPLETED],
    ScreeningState.COMPLETED: [],
    ScreeningState.ERROR: [
        ScreeningState.INITIAL, 
        ScreeningState.TRIAGE, 
        ScreeningState.COMPLETED
    ]
}

class ScreeningFlow:
    """Manages the screening flow state machine"""

    @staticmethod
    def get_current_state(session_id: str) -> Optional[ScreeningState]:
        """Get the current state for a session"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return None
            
        # Map flow_type and current_step to a state
        flow_type = session_data.get('flow_type')
        current_step = session_data.get('current_step', 0)
        
        if flow_type == FLOW_TYPES['INITIAL']:
            return ScreeningState.INITIAL
        elif flow_type == FLOW_TYPES['TRIAGE']:
            return ScreeningState.TRIAGE
        elif flow_type == FLOW_TYPES['SCREENING']:
            # Map screening steps to states
            screening_steps = {
                0: ScreeningState.CONDITION_SELECTION,
                1: ScreeningState.QUESTION_COLLECTION,
                2: ScreeningState.ANALYSIS,
                3: ScreeningState.RECOMMENDATION
            }
            return screening_steps.get(current_step, ScreeningState.ERROR)
        elif flow_type == FLOW_TYPES['RED_FLAG']:
            return ScreeningState.RED_FLAG_DETECTED
        elif flow_type == FLOW_TYPES['FOLLOW_UP']:
            return ScreeningState.FOLLOW_UP
        
        return ScreeningState.ERROR

    @staticmethod
    def can_transition_to(current_state: ScreeningState, target_state: ScreeningState) -> bool:
        """Check if a transition from current_state to target_state is valid"""
        if current_state not in TRANSITIONS:
            return False
            
        return target_state in TRANSITIONS[current_state]

    @staticmethod
    def transition_to(session_id: str, target_state: ScreeningState) -> bool:
        """Transition a session to a new state"""
        current_state = ScreeningFlow.get_current_state(session_id)
        if not current_state:
            return False
            
        if not ScreeningFlow.can_transition_to(current_state, target_state):
            return False
            
        # Map the target state to flow_type and current_step
        flow_type = FLOW_TYPES['INITIAL']
        current_step = 0
        
        if target_state == ScreeningState.TRIAGE:
            flow_type = FLOW_TYPES['TRIAGE']
        elif target_state in [
            ScreeningState.CONDITION_SELECTION,
            ScreeningState.QUESTION_COLLECTION,
            ScreeningState.ANALYSIS,
            ScreeningState.RECOMMENDATION
        ]:
            flow_type = FLOW_TYPES['SCREENING']
            # Map states to steps
            step_mapping = {
                ScreeningState.CONDITION_SELECTION: 0,
                ScreeningState.QUESTION_COLLECTION: 1,
                ScreeningState.ANALYSIS: 2,
                ScreeningState.RECOMMENDATION: 3
            }
            current_step = step_mapping.get(target_state, 0)
        elif target_state == ScreeningState.RED_FLAG_DETECTED:
            flow_type = FLOW_TYPES['RED_FLAG']
        elif target_state == ScreeningState.FOLLOW_UP:
            flow_type = FLOW_TYPES['FOLLOW_UP']
            
        # Update the session
        return SessionManager.update_session(
            session_id,
            {
                'flow_type': flow_type,
                'current_step': current_step
            }
        )

    @staticmethod
    def get_next_action(session_id: str) -> Dict[str, Any]:
        """Get the next action for the current state"""
        current_state = ScreeningFlow.get_current_state(session_id)
        if not current_state:
            return {'action': 'create_session', 'message': 'Session not found'}
            
        session_data = SessionManager.get_session(session_id)
        
        if current_state == ScreeningState.INITIAL:
            return {
                'action': 'start_triage',
                'message': 'Please describe the symptoms or concerns'
            }
        elif current_state == ScreeningState.TRIAGE:
            return {
                'action': 'perform_triage',
                'message': 'Analyzing symptoms...'
            }
        elif current_state == ScreeningState.CONDITION_SELECTION:
            # Check if a condition has already been selected
            if session_data and 'selected_condition' in session_data:
                return {
                    'action': 'collect_responses',
                    'condition': session_data['selected_condition'],
                    'message': 'Please answer the following questions'
                }
            else:
                return {
                    'action': 'select_condition',
                    'message': 'Please select a condition to screen for'
                }
        elif current_state == ScreeningState.QUESTION_COLLECTION:
            return {
                'action': 'analyze_responses',
                'message': 'Analyzing responses...'
            }
        elif current_state == ScreeningState.ANALYSIS:
            return {
                'action': 'provide_recommendation',
                'message': 'Generating recommendations...'
            }
        elif current_state == ScreeningState.RECOMMENDATION:
            return {
                'action': 'complete_screening',
                'message': 'Screening completed'
            }
        elif current_state == ScreeningState.RED_FLAG_DETECTED:
            return {
                'action': 'handle_red_flag',
                'message': 'Red flag detected! Urgent attention required.'
            }
        elif current_state == ScreeningState.FOLLOW_UP:
            return {
                'action': 'schedule_follow_up',
                'message': 'Please schedule a follow-up appointment'
            }
        elif current_state == ScreeningState.COMPLETED:
            return {
                'action': 'start_new_session',
                'message': 'Screening completed. Start a new session?'
            }
        else:
            return {
                'action': 'handle_error',
                'message': 'An error occurred in the screening flow'
            }

    @staticmethod
    def handle_red_flag_resume(session_id: str) -> Dict[str, Any]:
        """Handle resuming a session after a red flag was detected"""
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return {'success': False, 'message': 'Session not found'}
            
        red_flags = session_data.get('red_flags', [])
        if not red_flags:
            return {'success': False, 'message': 'No red flags found in session'}
            
        # Get the most recent red flag
        latest_red_flag = red_flags[-1]
        
        # Create a summary of the red flag situation
        summary = {
            'success': True,
            'red_flag': latest_red_flag,
            'message': 'Session resumed after red flag detection',
            'recommendation': 'Please seek immediate medical attention'
        }
        
        # Transition to completed state
        ScreeningFlow.transition_to(session_id, ScreeningState.COMPLETED)
        
        return summary 