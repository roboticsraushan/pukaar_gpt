# Red flag detection agent for infant medical emergencies
def detect_red_flags(user_input: str) -> dict:
    """
    Red flag detection agent responsible for identifying signs of medical emergencies in infants.
    Uses conservative interpretation of parent language with clinical knowledge.
    Prefers caution to avoid missing serious cases.
    """
    
    # Convert to lowercase for easier matching
    input_lower = user_input.lower()
    
    # Comprehensive red flag patterns based on IMNCI, WHO IMCI, IAP, and AIIMS protocols
    red_flags = {
        # Neurological emergencies
        "convulsions_seizures": [
            "convulsion", "seizure", "fits", "jerking", "twitching", "shaking", 
            "uncontrolled movement", "spasms", "tremors", "stiff", "rigid"
        ],
        "unconsciousness": [
            "unconscious", "passed out", "not responding", "no response", "blacked out",
            "fainted", "collapsed", "not moving", "limp", "floppy"
        ],
        "altered_consciousness": [
            "very sleepy", "extremely drowsy", "hard to wake", "won't wake up", 
            "difficult to wake", "not alert", "confused", "disoriented"
        ],
        
        # Respiratory emergencies
        "respiratory_distress": [
            "fast breathing", "rapid breathing", "breathing fast", ">60 breaths", "60+ breaths",
            "breathing difficulty", "struggling to breathe", "shortness of breath",
            "breathing problems", "respiratory distress"
        ],
        "chest_indrawing": [
            "chest indrawing", "chest sinking", "chest retraction", "ribs showing",
            "chest pulling in", "chest caving", "sternal retraction"
        ],
        "grunting": [
            "grunting", "grunting sounds", "noisy breathing", "wheezing", "stridor"
        ],
        "cyanosis": [
            "blue lips", "blue face", "blue skin", "cyanosis", "blue extremities",
            "blue fingers", "blue toes", "bluish", "purple", "discolored"
        ],
        
        # Feeding and hydration
        "feeding_refusal": [
            "not feeding", "refusing food", "no interest in feeding", "won't eat", "not eating",
            "refusing breast", "refusing bottle", "no appetite", "not drinking",
            "refusing to feed", "feeding problems", "feeding issues"
        ],
        "dehydration": [
            "sunken eyes", "no urination", "no pee", "dehydrated", "dry mouth",
            "no wet diapers", "dry diapers", "no tears", "crying without tears",
            "very thirsty", "excessive thirst"
        ],
        
        # Temperature abnormalities
        "high_fever": [
            "fever >38.5", "temperature >38.5", "high fever", "very hot", "burning up",
            "feverish", "hot to touch", "very high temperature", "fever above 38.5"
        ],
        "hypothermia": [
            "cold", "low temperature", "hypothermia", "feels cold", "very cold",
            "cold to touch", "chilled", "shivering", "cold extremities"
        ],
        
        # Jaundice and liver issues
        "jaundice_danger": [
            "yellow below knees", "white stool", "grey stool", "pale stool",
            "yellow skin", "yellow eyes", "jaundice", "yellowing", "pale poop",
            "clay colored stool", "acholic stool"
        ],
        
        # Swelling and edema
        "severe_swelling": [
            "swollen feet", "swollen face", "swollen body", "severe swelling",
            "puffy", "edema", "fluid retention", "swollen all over", "bloated"
        ],
        
        # Gastrointestinal emergencies
        "bloody_stools": [
            "bloody stool", "blood in stool", "bloody poop", "blood in poop",
            "red stool", "black stool", "tarry stool", "bloody diarrhea"
        ],
        "vomiting_everything": [
            "vomiting everything", "throwing up everything", "can't keep anything down",
            "projectile vomiting", "severe vomiting", "vomiting repeatedly",
            "vomiting all the time", "continuous vomiting"
        ],
        
        # General distress
        "weak_cry": [
            "weak cry", "no cry", "absent cry", "barely crying", "feeble cry",
            "soft cry", "quiet cry", "no sound", "silent cry"
        ],
        "lethargy": [
            "lethargic", "very tired", "exhausted", "no energy", "weak",
            "listless", "not active", "very quiet", "unusually quiet"
        ],
        
        # Time-based concerns (conservative interpretation)
        "extended_feeding_refusal": [
            "not eating for hours", "hasn't fed for hours", "refusing food for hours",
            "no feeding for 6 hours", "hasn't eaten for 6 hours", "feeding refusal for hours"
        ],
        "extended_no_urination": [
            "no pee for hours", "no wet diaper for hours", "hasn't peed for hours",
            "no urination for 6 hours", "dry diapers for hours"
        ]
    }
    
    # Check for red flags with conservative interpretation
    detected_flags = []
    
    for flag_type, patterns in red_flags.items():
        for pattern in patterns:
            if pattern in input_lower:
                detected_flags.append({
                    "type": flag_type,
                    "trigger": pattern,
                    "severity": "high"
                })
                break  # Found one pattern for this flag type, move to next
    
    # Additional clinical interpretation for imprecise language
    clinical_indicators = {
        "emergency_language": [
            "emergency", "urgent", "serious", "worried", "scared", "panicked",
            "terrible", "awful", "very bad", "extremely", "severely"
        ],
        "time_pressure": [
            "just happened", "suddenly", "all of a sudden", "quickly", "rapidly",
            "getting worse", "worsening", "deteriorating"
        ]
    }
    
    # Check for emergency language that might indicate red flags
    for indicator_type, patterns in clinical_indicators.items():
        for pattern in patterns:
            if pattern in input_lower:
                # If emergency language is present, be more conservative
                # Look for any concerning symptoms mentioned
                concerning_symptoms = [
                    "breathing", "feeding", "temperature", "color", "movement",
                    "consciousness", "crying", "sleeping", "eating", "drinking"
                ]
                
                for symptom in concerning_symptoms:
                    if symptom in input_lower:
                        detected_flags.append({
                            "type": f"emergency_language_{symptom}",
                            "trigger": f"Emergency language with {symptom} concern",
                            "severity": "medium"
                        })
                        break
    
    # If red flags detected, return emergency response
    if detected_flags:
        # Sort by severity (high first)
        detected_flags.sort(key=lambda x: 0 if x["severity"] == "high" else 1)
        trigger_phrase = detected_flags[0]["trigger"]
        
        return {
            "red_flag_detected": True,
            "trigger": trigger_phrase,
            "recommended_action": "Rush to emergency immediately"
        }
    
    # No red flags detected
    return {
        "red_flag_detected": False,
        "trigger": None,
        "recommended_action": None
    }

# Test the function with various scenarios
if __name__ == "__main__":
    test_cases = [
        "My baby is having convulsions",
        "Baby won't wake up and is very sleepy",
        "Fast breathing and blue lips",
        "Not feeding for the last 6 hours",
        "Very worried about my baby's breathing",
        "Suddenly started vomiting everything",
        "Normal feeding and sleeping",
        "Baby seems very tired and not eating much",
        "Emergency! My baby is not responding properly"
    ]
    
    for test_input in test_cases:
        result = detect_red_flags(test_input)
        print(f"Input: {test_input}")
        print(f"Result: {result}")
        print("-" * 50)

