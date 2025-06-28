# Screening agent for infant health conditions using IMNCI/WHO/IAP observational criteria
from .red_flag_model import detect_red_flags

class ScreeningAgent:
    def __init__(self):
        self.conditions = {
            "pneumonia_ari": {
                "name": "Pneumonia/Acute Respiratory Infection",
                "description": "A serious lung infection that can cause breathing difficulties and is a leading cause of infant mortality worldwide.",
                "importance": "Early detection is crucial as respiratory distress can rapidly worsen in infants.",
                "questions": [
                    {"question": "Is the baby breathing faster than normal?", "type": "yes_no"},
                    {"question": "Can you see the baby's ribs or chest pulling in when breathing?", "type": "yes_no"},
                    {"question": "Is the baby making grunting sounds while breathing?", "type": "yes_no"},
                    {"question": "Does the baby have a cough?", "type": "yes_no"},
                    {"question": "How many breaths per minute is the baby taking? (Count for 1 minute)", "type": "descriptive"},
                    {"question": "Is the baby's nose flaring when breathing?", "type": "yes_no"},
                    {"question": "Does the baby seem to be working hard to breathe?", "type": "yes_no"}
                ]
            },
            "diarrhea": {
                "name": "Diarrhea",
                "description": "Frequent loose or watery stools that can lead to dehydration, a serious complication in infants.",
                "importance": "Dehydration can develop quickly and become life-threatening in young infants.",
                "questions": [
                    {"question": "How many loose or watery stools has the baby had in the last 24 hours?", "type": "descriptive"},
                    {"question": "Is the baby's stool watery or runny?", "type": "yes_no"},
                    {"question": "Has the baby been vomiting?", "type": "yes_no"},
                    {"question": "Is the baby drinking or feeding normally?", "type": "yes_no"},
                    {"question": "How many wet diapers has the baby had in the last 6 hours?", "type": "descriptive"},
                    {"question": "Are the baby's eyes sunken?", "type": "yes_no"},
                    {"question": "Does the baby seem thirsty or dehydrated?", "type": "yes_no"}
                ]
            },
            "malnutrition": {
                "name": "Malnutrition",
                "description": "Inadequate nutrition that can affect growth, development, and immune function.",
                "importance": "Early detection can prevent long-term developmental issues and complications.",
                "questions": [
                    {"question": "Has the baby been feeding less than usual?", "type": "yes_no"},
                    {"question": "How many feeds has the baby taken in the last 24 hours?", "type": "descriptive"},
                    {"question": "Does the baby seem less active or energetic?", "type": "yes_no"},
                    {"question": "Has the baby lost weight recently?", "type": "yes_no"},
                    {"question": "Are the baby's ribs or bones more visible than before?", "type": "yes_no"},
                    {"question": "Is the baby's skin loose or wrinkled?", "type": "yes_no"},
                    {"question": "How long does the baby typically feed for?", "type": "descriptive"}
                ]
            },
            "neonatal_sepsis": {
                "name": "Neonatal Sepsis",
                "description": "A serious bloodstream infection that can affect newborns and young infants.",
                "importance": "Sepsis can progress rapidly and requires immediate medical attention.",
                "questions": [
                    {"question": "Does the baby have a fever (temperature above 38°C)?", "type": "yes_no"},
                    {"question": "Is the baby feeding poorly or refusing feeds?", "type": "yes_no"},
                    {"question": "Is the baby unusually sleepy or difficult to wake?", "type": "yes_no"},
                    {"question": "Does the baby seem irritable or inconsolable?", "type": "yes_no"},
                    {"question": "Is the baby's skin color normal?", "type": "yes_no"},
                    {"question": "Is the baby breathing normally?", "type": "yes_no"},
                    {"question": "Has the baby's behavior changed suddenly?", "type": "yes_no"}
                ]
            },
            "neonatal_jaundice": {
                "name": "Neonatal Jaundice",
                "description": "Yellowing of the skin and eyes due to high bilirubin levels, common in newborns.",
                "importance": "Severe jaundice can cause brain damage if not treated promptly.",
                "questions": [
                    {"question": "Is the baby's skin or eyes yellow?", "type": "yes_no"},
                    {"question": "How old is the baby in days?", "type": "descriptive"},
                    {"question": "Is the yellow color spreading to the baby's arms and legs?", "type": "yes_no"},
                    {"question": "What color is the baby's stool?", "type": "descriptive"},
                    {"question": "Is the baby feeding normally?", "type": "yes_no"},
                    {"question": "Is the baby sleepy or difficult to wake?", "type": "yes_no"},
                    {"question": "Has the yellow color appeared suddenly or gradually?", "type": "descriptive"}
                ]
            }
        }
    
    def get_condition_info(self, condition_key):
        """Get information about a specific condition."""
        return self.conditions.get(condition_key, None)
    
    def get_screening_questions(self, condition_key):
        """Get the screening questions for a specific condition."""
        condition = self.get_condition_info(condition_key)
        if condition:
            return condition["questions"]
        return []
    
    def run_red_flag_check(self, user_response):
        """Run red flag detection on user response."""
        return detect_red_flags(user_response)
    
    def calculate_confidence_score(self, condition_key, responses):
        """Calculate confidence score based on responses."""
        # This is a simplified scoring system
        # In a real implementation, this would use more sophisticated logic
        condition = self.get_condition_info(condition_key)
        if not condition:
            return 0
        
        total_questions = len(condition["questions"])
        positive_responses = 0
        
        # Simple scoring based on yes responses and concerning descriptive responses
        for i, response in enumerate(responses):
            if response.lower() in ["yes", "true", "1", "positive"]:
                positive_responses += 1
            elif "descriptive" in condition["questions"][i]["type"]:
                # Check for concerning keywords in descriptive responses
                concerning_keywords = ["fast", "rapid", "high", "low", "none", "zero", "not", "refusing", "poor", "bad"]
                if any(keyword in response.lower() for keyword in concerning_keywords):
                    positive_responses += 0.5
        
        # Calculate percentage
        confidence = (positive_responses / total_questions) * 100
        return min(confidence, 100)  # Cap at 100%
    
    def get_recommended_action(self, confidence_score):
        """Get recommended action based on confidence score."""
        if confidence_score >= 70:
            return "Please consult a pediatrician immediately."
        elif confidence_score >= 40:
            return "Please consult a pediatrician soon."
        else:
            return "Please consult a pediatrician for routine check-up."
    
    def screen_condition(self, condition_key, user_responses):
        """Screen a specific condition and return results."""
        condition = self.get_condition_info(condition_key)
        if not condition:
            return {
                "error": "Condition not found"
            }
        
        # Check for red flags in each response
        red_flags_detected = []
        for response in user_responses:
            red_flag_result = self.run_red_flag_check(response)
            if red_flag_result["red_flag_detected"]:
                red_flags_detected.append(red_flag_result)
        
        # If red flags detected, return emergency response
        if red_flags_detected:
            return {
                "red_flag_detected": True,
                "trigger": red_flags_detected[0]["trigger"],
                "recommended_action": "Rush to emergency immediately",
                "condition_screened": condition["name"]
            }
        
        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(condition_key, user_responses)
        
        # Determine likelihood
        likelihood = "likely" if confidence_score >= 50 else "unlikely"
        
        return {
            "condition_screened": condition["name"],
            "confidence_score": round(confidence_score, 1),
            "likelihood": likelihood,
            "recommended_action": self.get_recommended_action(confidence_score),
            "disclaimer": "This is a screening result based on IMNCI/WHO/IAP standards and not a medical diagnosis.",
            "red_flag_detected": False
        }

# Global screening agent instance
screening_agent = ScreeningAgent()

def run_screening(condition_key, user_responses=None):
    """Main function to run screening for a condition."""
    if user_responses is None:
        # Return condition information and questions
        condition = screening_agent.get_condition_info(condition_key)
        if condition:
            return {
                "condition": condition["name"],
                "description": condition["description"],
                "importance": condition["importance"],
                "questions": condition["questions"],
                "disclaimer": "This is not a medical diagnosis. This is a screening based on IMNCI/WHO/IAP guidelines to help identify potential warning signs."
            }
        else:
            return {"error": "Condition not found"}
    else:
        # Run the actual screening
        return screening_agent.screen_condition(condition_key, user_responses)

# Test the screening function
if __name__ == "__main__":
    # Test getting condition info
    print("=== Testing Condition Info ===")
    result = run_screening("pneumonia_ari")
    print(result)
    
    # Test screening with responses
    print("\n=== Testing Screening ===")
    test_responses = ["yes", "no", "yes", "yes", "65", "yes", "yes"]
    result = run_screening("pneumonia_ari", test_responses)
    print(result)

