# Parenting Assistant for Non-Clinical Issues
class ConsultAdviceGPT:
    def __init__(self):
        self.expert_mapping = {
            "feeding": {
                "expert": "lactation consultant or pediatric nutritionist",
                "keywords": ["feeding", "breastfeeding", "bottle", "eating", "food", "milk", "formula", "latch", "nipple", "appetite", "refusing food", "feeding schedule"]
            },
            "sleep": {
                "expert": "pediatric sleep specialist",
                "keywords": ["sleep", "bedtime", "waking up", "naps", "crying at night", "sleep training", "co-sleeping", "crib", "bedtime routine", "night wakings", "sleep schedule"]
            },
            "behavior": {
                "expert": "child development specialist or pediatric psychologist",
                "keywords": ["crying", "tantrums", "behavior", "temperament", "development", "milestones", "social", "interaction", "play", "learning", "attention", "hyperactive"]
            },
            "development": {
                "expert": "pediatric developmental specialist",
                "keywords": ["milestones", "crawling", "walking", "talking", "speech", "motor skills", "cognitive", "learning", "development", "growth", "progress"]
            },
            "general": {
                "expert": "pediatrician",
                "keywords": ["general", "overall", "routine", "care", "parenting", "advice", "guidance"]
            }
        }
        
        self.guidance_templates = {
            "feeding": {
                "gentle_advice": [
                    "It's common for babies to have feeding preferences and patterns that change over time.",
                    "Try to maintain a calm, relaxed environment during feeding times.",
                    "Babies often go through phases where their feeding habits change - this is usually normal.",
                    "Consider keeping a feeding diary to track patterns and identify what works best.",
                    "Remember that every baby is unique and may have different feeding needs."
                ],
                "behavioral_tips": [
                    "Establish a consistent feeding routine with regular times.",
                    "Create a quiet, distraction-free environment for feeding.",
                    "Pay attention to your baby's hunger cues and feeding signals.",
                    "Be patient and avoid forcing feeding - let your baby set the pace.",
                    "Try different feeding positions to find what's most comfortable."
                ]
            },
            "sleep": {
                "gentle_advice": [
                    "Sleep patterns in babies can vary greatly and change frequently.",
                    "It's normal for babies to wake up during the night - this is part of healthy development.",
                    "Babies often need time to develop their own sleep rhythms.",
                    "Sleep challenges are very common and usually temporary.",
                    "Every family's sleep situation is different - find what works for you."
                ],
                "behavioral_tips": [
                    "Establish a consistent bedtime routine with calming activities.",
                    "Create a sleep-friendly environment (dark, quiet, comfortable temperature).",
                    "Try to put your baby down when drowsy but still awake.",
                    "Be consistent with nap times and bedtime.",
                    "Consider using white noise or gentle music to help with sleep."
                ]
            },
            "behavior": {
                "gentle_advice": [
                    "Babies communicate through their behavior - crying and fussing are normal ways to express needs.",
                    "Every baby has a unique temperament and personality.",
                    "Behavioral changes often coincide with developmental milestones.",
                    "It's normal for babies to have periods of increased fussiness.",
                    "Your baby's behavior is not a reflection of your parenting skills."
                ],
                "behavioral_tips": [
                    "Respond consistently to your baby's cues and signals.",
                    "Provide plenty of positive attention and interaction.",
                    "Create a predictable daily routine.",
                    "Use gentle, positive reinforcement for desired behaviors.",
                    "Take breaks when you need them - self-care is important."
                ]
            },
            "development": {
                "gentle_advice": [
                    "Every baby develops at their own pace - there's a wide range of normal.",
                    "Developmental milestones are guidelines, not strict deadlines.",
                    "Babies often focus on one area of development at a time.",
                    "It's normal for development to happen in spurts and pauses.",
                    "Your baby's unique personality will influence how they reach milestones."
                ],
                "behavioral_tips": [
                    "Provide plenty of opportunities for exploration and play.",
                    "Talk, sing, and read to your baby regularly.",
                    "Encourage tummy time and movement activities.",
                    "Offer age-appropriate toys and activities.",
                    "Celebrate your baby's progress, no matter how small."
                ]
            }
        }
    
    def identify_topic(self, user_input):
        """Identify the main topic of the user's concern."""
        input_lower = user_input.lower()
        
        # Count keyword matches for each topic
        topic_scores = {}
        for topic, data in self.expert_mapping.items():
            score = 0
            for keyword in data["keywords"]:
                if keyword in input_lower:
                    score += 1
            topic_scores[topic] = score
        
        # Return the topic with the highest score, or "general" if no clear match
        max_score = max(topic_scores.values())
        if max_score > 0:
            for topic, score in topic_scores.items():
                if score == max_score:
                    return topic
        else:
            return "general"
    
    def get_guidance(self, topic, user_input):
        """Generate gentle, behavioral guidance for the identified topic."""
        guidance = {
            "topic": topic,
            "expert": self.expert_mapping[topic]["expert"],
            "gentle_advice": [],
            "behavioral_tips": [],
            "consultation_offer": f"Would you like to consult a {self.expert_mapping[topic]['expert']}? We can help you book an appointment."
        }
        
        # Add topic-specific guidance if available
        if topic in self.guidance_templates:
            guidance["gentle_advice"] = self.guidance_templates[topic]["gentle_advice"]
            guidance["behavioral_tips"] = self.guidance_templates[topic]["behavioral_tips"]
        else:
            # General guidance for topics not specifically covered
            guidance["gentle_advice"] = [
                "It's completely normal to have questions and concerns about your baby's development.",
                "Every baby is unique and may have different needs and patterns.",
                "Trust your instincts as a parent - you know your baby best.",
                "Many parenting challenges are temporary and resolve with time.",
                "It's okay to seek support and guidance when you need it."
            ]
            guidance["behavioral_tips"] = [
                "Maintain consistent routines and schedules.",
                "Provide plenty of love, attention, and positive interaction.",
                "Create a safe, nurturing environment for your baby.",
                "Take care of yourself so you can be the best parent possible.",
                "Don't hesitate to reach out for professional support when needed."
            ]
        
        return guidance
    
    def generate_response(self, user_input):
        """Generate a complete response with guidance and consultation offer."""
        topic = self.identify_topic(user_input)
        guidance = self.get_guidance(topic, user_input)
        
        # Construct the response
        response = {
            "topic_identified": topic,
            "expert_type": guidance["expert"],
            "response": {
                "acknowledgment": f"I understand you're concerned about your baby's {topic}. This is a common parenting challenge.",
                "gentle_advice": guidance["gentle_advice"][:2],  # Limit to 2 pieces of advice
                "behavioral_tips": guidance["behavioral_tips"][:2],  # Limit to 2 tips
                "consultation_offer": guidance["consultation_offer"],
                "disclaimer": "This guidance is for general parenting support and should not replace professional medical advice."
            }
        }
        
        return response

# Global instance
consult_advice_gpt = ConsultAdviceGPT()

def get_consult_advice(user_input):
    """Main function to get parenting advice for non-clinical issues."""
    return consult_advice_gpt.generate_response(user_input)

# Test the function
if __name__ == "__main__":
    test_cases = [
        "My baby won't sleep through the night",
        "My baby is refusing to eat",
        "My baby cries all the time",
        "My baby isn't crawling yet",
        "I need general parenting advice"
    ]
    
    for test_input in test_cases:
        result = get_consult_advice(test_input)
        print(f"Input: {test_input}")
        print(f"Topic: {result['topic_identified']}")
        print(f"Expert: {result['expert_type']}")
        print(f"Response: {result['response']}")
        print("-" * 50) 