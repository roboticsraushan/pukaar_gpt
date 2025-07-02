# Context Classifier for User Input Analysis
class ContextClassifier:
    def __init__(self):
        # Medical conditions that can be screened using our system
        self.screenable_conditions = {
            "pneumonia_ari": [
                "cough", "breathing", "chest", "respiratory", "pneumonia", "lung", "airway",
                "fast breathing", "rapid breathing", "breathing fast", "breathing difficulty",
                "chest indrawing", "chest retraction", "grunting", "wheezing", "stridor",
                "blue lips", "cyanosis", "shortness of breath", "respiratory distress"
            ],
            "diarrhea": [
                "diarrhea", "loose stool", "watery stool", "runny poop", "frequent bowel movements",
                "stool", "poop", "bowel", "dehydration", "sunken eyes", "dry mouth",
                "no urination", "no wet diapers", "thirsty", "vomiting", "nausea"
            ],
            "malnutrition": [
                "not eating", "refusing food", "feeding problems", "weight loss", "underweight",
                "poor appetite", "feeding issues", "not feeding", "malnutrition", "nutrition",
                "growth", "development", "weight", "thin", "skinny", "ribs showing"
            ],
            "neonatal_sepsis": [
                "fever", "temperature", "hot", "infection", "sepsis", "bacterial infection",
                "bloodstream infection", "high fever", "very hot", "burning up", "infection",
                "poor feeding", "lethargy", "irritable", "not responding", "unconscious"
            ],
            "neonatal_jaundice": [
                "yellow", "jaundice", "yellow skin", "yellow eyes", "bilirubin", "liver",
                "pale stool", "white stool", "grey stool", "clay colored", "acholic stool",
                "yellowing", "yellow below knees", "yellow extremities"
            ]
        }
        
        # Medical conditions that are outside our screening scope
        self.non_screenable_medical = [
            "teething", "reflux", "colic", "gas", "constipation", "eczema", "rash", "allergy",
            "ear infection", "eye infection", "thrush", "diaper rash", "cradle cap",
            "birthmark", "mole", "skin condition", "dental", "oral", "throat", "ear",
            "eye", "vision", "hearing", "heart", "cardiac", "blood", "anemia", "diabetes",
            "thyroid", "genetic", "chromosomal", "birth defect", "congenital", "surgery",
            "post-operative", "medication", "drug", "vaccine", "immunization", "shot"
        ]
        
        # Non-medical parenting concerns
        self.non_medical_concerns = [
            "sleep", "bedtime", "naps", "sleep training", "crying", "tantrums", "behavior",
            "temperament", "development", "milestones", "crawling", "walking", "talking",
            "speech", "motor skills", "learning", "play", "toys", "activities", "routine",
            "schedule", "discipline", "parenting", "bonding", "attachment", "social",
            "interaction", "communication", "language", "reading", "books", "music",
            "feeding schedule", "feeding routine", "bottle", "breastfeeding", "formula",
            "solid food", "weaning", "pacifier", "thumb sucking", "comfort", "soothing"
        ]
        
        # Emergency/red flag indicators that require immediate attention
        self.emergency_indicators = [
            "emergency", "urgent", "serious", "critical", "immediate", "rush", "ambulance",
            "hospital", "ER", "emergency room", "unconscious", "not breathing", "choking",
            "seizure", "convulsion", "bleeding", "broken", "fracture", "burn", "poison",
            "overdose", "accident", "injury", "trauma", "head injury", "fall"
        ]
    
    def analyze_input(self, user_input):
        """Analyze user input and classify the context."""
        input_lower = user_input.lower()
        
        # Check for emergency indicators first
        if any(indicator in input_lower for indicator in self.emergency_indicators):
            return {
                "classified_context": "medical_non_screenable",
                "reasoning": "Contains emergency indicators requiring immediate medical attention",
                "confidence": "high"
            }
        
        # Check for screenable medical conditions
        screenable_matches = []
        for condition, keywords in self.screenable_conditions.items():
            for keyword in keywords:
                if keyword in input_lower:
                    screenable_matches.append(condition)
                    break  # Found one keyword for this condition
        
        # Check for non-screenable medical conditions
        non_screenable_matches = []
        for keyword in self.non_screenable_medical:
            if keyword in input_lower:
                non_screenable_matches.append(keyword)
        
        # Check for non-medical concerns
        non_medical_matches = []
        for keyword in self.non_medical_concerns:
            if keyword in input_lower:
                non_medical_matches.append(keyword)
        
        # Check for follow-up keywords
        follow_up_keywords = [
            "follow up", "checkup", "come back", "not improved", "still sick", "after treatment",
            "antibiotics", "medicine", "treatment", "persistent", "not better", "not resolved",
            "not gone", "keeps happening", "did not improve", "symptoms remain", "after medication",
            "after antibiotics", "not responding", "not working", "not effective"
        ]
        if any(kw in input_lower for kw in follow_up_keywords):
            return {
                "classified_context": "follow_up",
                "reasoning": "Detected follow-up intent",
                "confidence": "high"
            }
        
        # Check for consult/advice keywords (expanded)
        consult_keywords = [
            "should i", "is it safe", "can i give", "what should i do", "advice", "consult",
            "is it ok", "is it okay", "can my child", "can i use", "how can i", "what can i do",
            "tips for", "prevent", "manage", "care for", "when should i", "is it normal",
            "is it necessary", "is it recommended", "is it possible", "is it allowed", "is it harmful",
            "is it beneficial", "is it required", "is it important", "is it urgent", "is it dangerous"
        ]
        if any(kw in input_lower for kw in consult_keywords):
            return {
                "classified_context": "consult",
                "reasoning": "Detected consult/advice intent",
                "confidence": "high"
            }
        
        # Prefer consult if message is a question and not a clear screenable symptom
        question_starts = ("how ", "what ", "when ", "should ", "is ", "can ", "could ", "would ", "do ", "does ", "did ")
        if user_input.strip().lower().startswith(question_starts):
            if not screenable_matches:
                return {
                    "classified_context": "consult",
                    "reasoning": "Message is a question and not a clear screenable symptom",
                    "confidence": "medium"
                }
        
        # Determine classification based on matches
        if screenable_matches:
            # If screenable conditions are mentioned, prioritize medical screening
            condition_names = [condition.replace("_", " ") for condition in screenable_matches]
            reasoning = f"Mentions {', '.join(condition_names)} which can be screened using our system"
            return {
                "classified_context": "medical_screenable",
                "reasoning": reasoning,
                "confidence": "high",
                "detected_conditions": screenable_matches
            }
        
        elif non_screenable_matches:
            # Medical conditions outside our screening scope
            reasoning = f"Medical concerns ({', '.join(non_screenable_matches[:3])}) outside our screening scope"
            return {
                "classified_context": "medical_non_screenable",
                "reasoning": reasoning,
                "confidence": "high",
                "detected_conditions": non_screenable_matches
            }
        
        elif non_medical_matches:
            # Non-medical parenting concerns
            reasoning = f"Non-medical parenting concerns ({', '.join(non_medical_matches[:3])})"
            return {
                "classified_context": "non_medical",
                "reasoning": reasoning,
                "confidence": "high",
                "detected_concerns": non_medical_matches
            }
        
        else:
            # Ambiguous or unclear input
            return {
                "classified_context": "medical_screenable",  # Default to screening for safety
                "reasoning": "Unclear symptoms - defaulting to medical screening for safety",
                "confidence": "low"
            }
    
    def get_classification_with_context(self, user_input):
        """Get detailed classification with additional context information."""
        classification = self.analyze_input(user_input)
        
        # Add context-specific information
        if classification["classified_context"] == "medical_screenable":
            classification["next_action"] = "Proceed with medical screening using our triage system"
            classification["expert_type"] = "Medical screening assistant"
        
        elif classification["classified_context"] == "medical_non_screenable":
            classification["next_action"] = "Recommend consultation with appropriate medical specialist"
            classification["expert_type"] = "Medical specialist referral"
        
        elif classification["classified_context"] == "non_medical":
            classification["next_action"] = "Provide parenting guidance and behavioral support"
            classification["expert_type"] = "Parenting consultant"
        
        return classification

# Global instance
context_classifier = ContextClassifier()

def classify_context(user_input):
    """Main function to classify user input context."""
    return context_classifier.get_classification_with_context(user_input)

# Test the classifier
if __name__ == "__main__":
    test_cases = [
        "My baby has a cough and fast breathing",
        "My baby is teething and crying a lot",
        "My baby won't sleep through the night",
        "My baby has a fever and is not responding",
        "My baby has yellow skin and eyes",
        "My baby is refusing to eat",
        "My baby has a rash on the face",
        "My baby is not crawling yet",
        "Emergency! My baby is not breathing properly",
        "My baby has gas and is fussy"
    ]
    
    for test_input in test_cases:
        result = classify_context(test_input)
        print(f"Input: {test_input}")
        print(f"Classification: {result['classified_context']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Next Action: {result['next_action']}")
        print("-" * 50) 