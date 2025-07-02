"""
Enhanced Screening Model for Infant Health Conditions
Integrates with existing screening system and provides sophisticated, data-driven logic
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from .red_flag_model import detect_red_flags

class EnhancedScreeningModel:
    def __init__(self):
        # Age-specific risk factors and thresholds
        self.age_risk_factors = {
            "neonatal": {"min_days": 0, "max_days": 28, "risk_multiplier": 1.5},
            "young_infant": {"min_days": 29, "max_days": 90, "risk_multiplier": 1.3},
            "older_infant": {"min_days": 91, "max_days": 365, "risk_multiplier": 1.0}
        }
        
        # Evidence-based symptom weights for all conditions
        self.symptom_weights = {
            "pneumonia_ari": {
                "respiratory_rate": {
                    "normal": {"weight": 0, "description": "Normal respiratory rate"},
                    "elevated": {"weight": 15, "description": "Elevated respiratory rate"},
                    "high": {"weight": 25, "description": "High respiratory rate (>60/min)"},
                    "very_high": {"weight": 35, "description": "Very high respiratory rate (>70/min)"}
                },
                "chest_indrawing": {
                    "none": {"weight": 0, "description": "No chest indrawing"},
                    "mild": {"weight": 20, "description": "Mild chest indrawing"},
                    "moderate": {"weight": 30, "description": "Moderate chest indrawing"},
                    "severe": {"weight": 40, "description": "Severe chest indrawing"}
                },
                "grunting": {
                    "none": {"weight": 0, "description": "No grunting"},
                    "occasional": {"weight": 15, "description": "Occasional grunting"},
                    "frequent": {"weight": 25, "description": "Frequent grunting"},
                    "continuous": {"weight": 35, "description": "Continuous grunting"}
                },
                "cyanosis": {
                    "none": {"weight": 0, "description": "No cyanosis"},
                    "mild": {"weight": 30, "description": "Mild cyanosis"},
                    "severe": {"weight": 50, "description": "Severe cyanosis"}
                },
                "feeding_status": {
                    "normal": {"weight": 0, "description": "Normal feeding"},
                    "reduced": {"weight": 10, "description": "Reduced feeding"},
                    "poor": {"weight": 20, "description": "Poor feeding"},
                    "refusing": {"weight": 30, "description": "Refusing feeds"}
                }
            },
            "diarrhea": {
                "stool_frequency": {
                    "normal": {"weight": 0, "description": "Normal stool frequency"},
                    "increased": {"weight": 10, "description": "Increased stool frequency"},
                    "high": {"weight": 20, "description": "High stool frequency (>8/day)"},
                    "very_high": {"weight": 30, "description": "Very high stool frequency (>10/day)"}
                },
                "stool_consistency": {
                    "normal": {"weight": 0, "description": "Normal stool consistency"},
                    "loose": {"weight": 15, "description": "Loose stools"},
                    "watery": {"weight": 25, "description": "Watery stools"},
                    "very_watery": {"weight": 35, "description": "Very watery stools"}
                },
                "dehydration_signs": {
                    "none": {"weight": 0, "description": "No dehydration signs"},
                    "mild": {"weight": 20, "description": "Mild dehydration signs"},
                    "moderate": {"weight": 35, "description": "Moderate dehydration signs"},
                    "severe": {"weight": 50, "description": "Severe dehydration signs"}
                },
                "vomiting": {
                    "none": {"weight": 0, "description": "No vomiting"},
                    "occasional": {"weight": 10, "description": "Occasional vomiting"},
                    "frequent": {"weight": 20, "description": "Frequent vomiting"},
                    "continuous": {"weight": 30, "description": "Continuous vomiting"}
                }
            },
            "malnutrition": {
                "feeding_pattern": {
                    "normal": {"weight": 0, "description": "Normal feeding pattern"},
                    "reduced": {"weight": 15, "description": "Reduced feeding"},
                    "poor": {"weight": 25, "description": "Poor feeding"},
                    "refusing": {"weight": 35, "description": "Refusing feeds"}
                },
                "weight_change": {
                    "gaining": {"weight": 0, "description": "Normal weight gain"},
                    "stable": {"weight": 10, "description": "Stable weight"},
                    "slow_gain": {"weight": 20, "description": "Slow weight gain"},
                    "losing": {"weight": 30, "description": "Weight loss"}
                },
                "activity_level": {
                    "normal": {"weight": 0, "description": "Normal activity level"},
                    "reduced": {"weight": 10, "description": "Reduced activity"},
                    "lethargic": {"weight": 20, "description": "Lethargic"},
                    "very_lethargic": {"weight": 30, "description": "Very lethargic"}
                },
                "visible_signs": {
                    "none": {"weight": 0, "description": "No visible signs"},
                    "mild": {"weight": 15, "description": "Mild visible signs"},
                    "moderate": {"weight": 25, "description": "Moderate visible signs"},
                    "severe": {"weight": 35, "description": "Severe visible signs"}
                }
            },
            "neonatal_sepsis": {
                "temperature": {
                    "normal": {"weight": 0, "description": "Normal temperature"},
                    "elevated": {"weight": 20, "description": "Elevated temperature"},
                    "high_fever": {"weight": 35, "description": "High fever (>38.5°C)"},
                    "hypothermia": {"weight": 40, "description": "Hypothermia (<36°C)"}
                },
                "feeding_status": {
                    "normal": {"weight": 0, "description": "Normal feeding"},
                    "reduced": {"weight": 15, "description": "Reduced feeding"},
                    "poor": {"weight": 25, "description": "Poor feeding"},
                    "refusing": {"weight": 35, "description": "Refusing feeds"}
                },
                "consciousness": {
                    "alert": {"weight": 0, "description": "Alert and responsive"},
                    "drowsy": {"weight": 20, "description": "Drowsy"},
                    "lethargic": {"weight": 30, "description": "Lethargic"},
                    "unconscious": {"weight": 50, "description": "Unconscious"}
                },
                "irritability": {
                    "normal": {"weight": 0, "description": "Normal behavior"},
                    "irritable": {"weight": 15, "description": "Irritable"},
                    "very_irritable": {"weight": 25, "description": "Very irritable"},
                    "inconsolable": {"weight": 35, "description": "Inconsolable"}
                }
            },
            "neonatal_jaundice": {
                "jaundice_extent": {
                    "none": {"weight": 0, "description": "No jaundice"},
                    "face_only": {"weight": 10, "description": "Jaundice on face only"},
                    "upper_body": {"weight": 20, "description": "Jaundice on upper body"},
                    "full_body": {"weight": 30, "description": "Jaundice on full body"},
                    "below_knees": {"weight": 40, "description": "Jaundice below knees"}
                },
                "age_days": {
                    "0_3": {"weight": 0, "description": "0-3 days old"},
                    "4_7": {"weight": 10, "description": "4-7 days old"},
                    "8_14": {"weight": 20, "description": "8-14 days old"},
                    "15_plus": {"weight": 30, "description": "15+ days old"}
                },
                "feeding_status": {
                    "normal": {"weight": 0, "description": "Normal feeding"},
                    "reduced": {"weight": 15, "description": "Reduced feeding"},
                    "poor": {"weight": 25, "description": "Poor feeding"},
                    "refusing": {"weight": 35, "description": "Refusing feeds"}
                },
                "stool_color": {
                    "normal": {"weight": 0, "description": "Normal stool color"},
                    "pale": {"weight": 20, "description": "Pale stool"},
                    "white": {"weight": 30, "description": "White stool"},
                    "clay_colored": {"weight": 35, "description": "Clay colored stool"}
                }
            }
        }
        
        # Dynamic thresholds based on age and condition
        self.dynamic_thresholds = {
            "pneumonia_ari": {
                "neonatal": {"low": 30, "medium": 50, "high": 70},
                "young_infant": {"low": 25, "medium": 45, "high": 65},
                "older_infant": {"low": 20, "medium": 40, "high": 60}
            },
            "diarrhea": {
                "neonatal": {"low": 25, "medium": 45, "high": 65},
                "young_infant": {"low": 20, "medium": 40, "high": 60},
                "older_infant": {"low": 15, "medium": 35, "high": 55}
            },
            "malnutrition": {
                "neonatal": {"low": 20, "medium": 40, "high": 60},
                "young_infant": {"low": 25, "medium": 45, "high": 65},
                "older_infant": {"low": 30, "medium": 50, "high": 70}
            },
            "neonatal_sepsis": {
                "neonatal": {"low": 15, "medium": 35, "high": 55},
                "young_infant": {"low": 20, "medium": 40, "high": 60},
                "older_infant": {"low": 25, "medium": 45, "high": 65}
            },
            "neonatal_jaundice": {
                "neonatal": {"low": 20, "medium": 40, "high": 60},
                "young_infant": {"low": 25, "medium": 45, "high": 65},
                "older_infant": {"low": 30, "medium": 50, "high": 70}
            }
        }
    
    def extract_numerical_values(self, text: str) -> Dict[str, float]:
        """Extract numerical values from text responses."""
        values = {}
        
        # Extract respiratory rate
        rr_patterns = [
            r'(\d+)\s*breaths?\s*per\s*minute',
            r'(\d+)\s*bpm',
            r'breathing\s*(\d+)\s*times',
            r'(\d+)\s*breaths'
        ]
        for pattern in rr_patterns:
            match = re.search(pattern, text.lower())
            if match:
                values['respiratory_rate'] = float(match.group(1))
                break
        
        # Extract age in days
        age_patterns = [
            r'(\d+)\s*days?\s*old',
            r'age\s*(\d+)\s*days',
            r'(\d+)\s*days?\s*of\s*age'
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text.lower())
            if match:
                values['age_days'] = float(match.group(1))
                break
        
        # Extract stool frequency
        stool_patterns = [
            r'(\d+)\s*stools?\s*per\s*day',
            r'(\d+)\s*times\s*per\s*day',
            r'(\d+)\s*bowel\s*movements'
        ]
        for pattern in stool_patterns:
            match = re.search(pattern, text.lower())
            if match:
                values['stool_frequency'] = float(match.group(1))
                break
        
        return values
    
    def classify_symptom_severity(self, condition: str, responses: List[str], numerical_values: Dict[str, float]) -> Dict[str, str]:
        """Classify symptom severity based on responses and numerical values."""
        symptom_scores = {}
        
        if condition == "pneumonia_ari" and len(responses) >= 5:
            # Respiratory rate
            rr = numerical_values.get('respiratory_rate')
            if rr:
                if rr > 70:
                    symptom_scores["respiratory_rate"] = "very_high"
                elif rr > 60:
                    symptom_scores["respiratory_rate"] = "high"
                elif rr > 50:
                    symptom_scores["respiratory_rate"] = "elevated"
                else:
                    symptom_scores["respiratory_rate"] = "normal"
            else:
                response = responses[0].lower()
                if any(word in response for word in ["very fast", "extremely fast", ">70", "70+"]):
                    symptom_scores["respiratory_rate"] = "very_high"
                elif any(word in response for word in ["fast", "rapid", ">60", "60+"]):
                    symptom_scores["respiratory_rate"] = "high"
                elif any(word in response for word in ["slightly fast", "elevated"]):
                    symptom_scores["respiratory_rate"] = "elevated"
                else:
                    symptom_scores["respiratory_rate"] = "normal"
            
            # Chest indrawing
            response = responses[1].lower()
            if any(word in response for word in ["severe", "very bad", "extreme", "terrible"]):
                symptom_scores["chest_indrawing"] = "severe"
            elif any(word in response for word in ["moderate", "bad", "clearly visible"]):
                symptom_scores["chest_indrawing"] = "moderate"
            elif any(word in response for word in ["mild", "slight", "a little"]):
                symptom_scores["chest_indrawing"] = "mild"
            else:
                symptom_scores["chest_indrawing"] = "none"
            
            # Grunting
            response = responses[2].lower()
            if any(word in response for word in ["continuous", "all the time", "constantly"]):
                symptom_scores["grunting"] = "continuous"
            elif any(word in response for word in ["frequent", "often", "regularly"]):
                symptom_scores["grunting"] = "frequent"
            elif any(word in response for word in ["occasional", "sometimes", "now and then"]):
                symptom_scores["grunting"] = "occasional"
            else:
                symptom_scores["grunting"] = "none"
            
            # Cyanosis
            response = responses[3].lower()
            if any(word in response for word in ["severe", "very blue", "extremely blue", "purple"]):
                symptom_scores["cyanosis"] = "severe"
            elif any(word in response for word in ["mild", "slightly blue", "bluish"]):
                symptom_scores["cyanosis"] = "mild"
            else:
                symptom_scores["cyanosis"] = "none"
            
            # Feeding status
            response = responses[4].lower()
            if any(word in response for word in ["refusing", "won't eat", "not eating", "no feeding"]):
                symptom_scores["feeding_status"] = "refusing"
            elif any(word in response for word in ["poor", "bad", "very little"]):
                symptom_scores["feeding_status"] = "poor"
            elif any(word in response for word in ["reduced", "less", "decreased"]):
                symptom_scores["feeding_status"] = "reduced"
            else:
                symptom_scores["feeding_status"] = "normal"
        
        elif condition == "diarrhea" and len(responses) >= 4:
            # Stool frequency
            freq = numerical_values.get('stool_frequency')
            if freq:
                if freq > 10:
                    symptom_scores["stool_frequency"] = "very_high"
                elif freq > 8:
                    symptom_scores["stool_frequency"] = "high"
                elif freq > 5:
                    symptom_scores["stool_frequency"] = "increased"
                else:
                    symptom_scores["stool_frequency"] = "normal"
            else:
                response = responses[0].lower()
                if any(word in response for word in ["very frequent", ">10", "10+", "many times"]):
                    symptom_scores["stool_frequency"] = "very_high"
                elif any(word in response for word in ["frequent", ">8", "8+", "often"]):
                    symptom_scores["stool_frequency"] = "high"
                elif any(word in response for word in ["increased", "more than usual"]):
                    symptom_scores["stool_frequency"] = "increased"
                else:
                    symptom_scores["stool_frequency"] = "normal"
            
            # Stool consistency
            response = responses[1].lower()
            if any(word in response for word in ["very watery", "like water", "extremely runny"]):
                symptom_scores["stool_consistency"] = "very_watery"
            elif any(word in response for word in ["watery", "runny", "liquid"]):
                symptom_scores["stool_consistency"] = "watery"
            elif any(word in response for word in ["loose", "soft"]):
                symptom_scores["stool_consistency"] = "loose"
            else:
                symptom_scores["stool_consistency"] = "normal"
            
            # Dehydration signs
            response = responses[2].lower()
            if any(word in response for word in ["severe", "very bad", "extreme", "sunken eyes", "no tears", "no urine"]):
                symptom_scores["dehydration_signs"] = "severe"
            elif any(word in response for word in ["moderate", "bad", "dry mouth", "thirsty"]):
                symptom_scores["dehydration_signs"] = "moderate"
            elif any(word in response for word in ["mild", "slight", "a little"]):
                symptom_scores["dehydration_signs"] = "mild"
            else:
                symptom_scores["dehydration_signs"] = "none"
            
            # Vomiting
            response = responses[3].lower()
            if any(word in response for word in ["continuous", "all the time", "constantly", "everything"]):
                symptom_scores["vomiting"] = "continuous"
            elif any(word in response for word in ["frequent", "often", "regularly"]):
                symptom_scores["vomiting"] = "frequent"
            elif any(word in response for word in ["occasional", "sometimes", "now and then"]):
                symptom_scores["vomiting"] = "occasional"
            else:
                symptom_scores["vomiting"] = "none"
        
        # Add more conditions as needed...
        
        return symptom_scores
    
    def calculate_age_risk_multiplier(self, age_days: float) -> float:
        """Calculate age-based risk multiplier."""
        for age_group, factors in self.age_risk_factors.items():
            if factors["min_days"] <= age_days <= factors["max_days"]:
                return factors["risk_multiplier"]
        return 1.0  # Default for older infants
    
    def calculate_interaction_multiplier(self, condition: str, symptom_scores: Dict[str, str]) -> float:
        """Calculate interaction multiplier based on symptom combinations."""
        multiplier = 1.0
        
        if condition == "pneumonia_ari":
            # High respiratory rate + chest indrawing
            if (symptom_scores.get("respiratory_rate") in ["high", "very_high"] and 
                symptom_scores.get("chest_indrawing") in ["moderate", "severe"]):
                multiplier *= 1.3
            
            # Very high respiratory rate + cyanosis
            if (symptom_scores.get("respiratory_rate") == "very_high" and 
                symptom_scores.get("cyanosis") in ["mild", "severe"]):
                multiplier *= 1.5
            
            # Severe chest indrawing + frequent grunting
            if (symptom_scores.get("chest_indrawing") == "severe" and 
                symptom_scores.get("grunting") in ["frequent", "continuous"]):
                multiplier *= 1.4
        
        elif condition == "diarrhea":
            # Very high stool frequency + severe dehydration
            if (symptom_scores.get("stool_frequency") == "very_high" and 
                symptom_scores.get("dehydration_signs") in ["moderate", "severe"]):
                multiplier *= 1.3
            
            # Very watery stools + frequent vomiting
            if (symptom_scores.get("stool_consistency") == "very_watery" and 
                symptom_scores.get("vomiting") in ["frequent", "continuous"]):
                multiplier *= 1.4
        
        return multiplier
    
    def calculate_enhanced_score(self, condition: str, responses: List[str], age_days: Optional[float] = None) -> Dict:
        """Calculate enhanced screening score using sophisticated algorithms."""
        # First check for red flags
        red_flags_detected = []
        for response in responses:
            red_flag_result = detect_red_flags(response)
            if red_flag_result["red_flag_detected"]:
                red_flags_detected.append(red_flag_result)
        
        # If red flags detected, return emergency response
        if red_flags_detected:
            return {
                "red_flag_detected": True,
                "trigger": red_flags_detected[0]["trigger"],
                "recommended_action": "Rush to emergency immediately",
                "condition_screened": condition,
                "algorithm_version": "enhanced_2.0"
            }
        
        # Extract numerical values
        numerical_values = {}
        for response in responses:
            numerical_values.update(self.extract_numerical_values(response))
        
        # Classify symptoms
        symptom_scores = self.classify_symptom_severity(condition, responses, numerical_values)
        
        # Calculate base weight
        total_weight = 0
        max_possible_weight = 0
        
        if condition in self.symptom_weights:
            for symptom, severity in symptom_scores.items():
                if symptom in self.symptom_weights[condition]:
                    weight = self.symptom_weights[condition][symptom].get(severity, {"weight": 0})["weight"]
                    total_weight += weight
                    max_possible_weight += max(
                        self.symptom_weights[condition][symptom][s]["weight"] 
                        for s in self.symptom_weights[condition][symptom]
                    )
        
        # Apply age risk multiplier
        age_multiplier = self.calculate_age_risk_multiplier(age_days or 30)
        adjusted_weight = total_weight * age_multiplier
        
        # Apply interaction multiplier
        interaction_multiplier = self.calculate_interaction_multiplier(condition, symptom_scores)
        final_weight = adjusted_weight * interaction_multiplier
        
        # Calculate percentage score
        if max_possible_weight > 0:
            percentage_score = (final_weight / max_possible_weight) * 100
        else:
            percentage_score = 0
        
        # Determine age group for threshold comparison
        age_group = "older_infant"  # Default
        if age_days:
            for group, factors in self.age_risk_factors.items():
                if factors["min_days"] <= age_days <= factors["max_days"]:
                    age_group = group
                    break
        
        # Get thresholds
        thresholds = self.dynamic_thresholds[condition][age_group]
        
        # Determine risk level
        if percentage_score >= thresholds["high"]:
            risk_level = "high"
            urgency = "immediate"
        elif percentage_score >= thresholds["medium"]:
            risk_level = "medium"
            urgency = "soon"
        elif percentage_score >= thresholds["low"]:
            risk_level = "low"
            urgency = "routine"
        else:
            risk_level = "minimal"
            urgency = "monitor"
        
        return {
            "condition_screened": condition,
            "percentage_score": round(percentage_score, 1),
            "risk_level": risk_level,
            "urgency": urgency,
            "age_multiplier": age_multiplier,
            "interaction_multiplier": interaction_multiplier,
            "symptom_scores": symptom_scores,
            "thresholds_used": thresholds,
            "age_group": age_group,
            "recommendations": self.get_enhanced_recommendations(condition, risk_level, urgency, age_days),
            "red_flag_detected": False,
            "algorithm_version": "enhanced_2.0"
        }
    
    def get_enhanced_recommendations(self, condition: str, risk_level: str, urgency: str, age_days: Optional[float]) -> Dict:
        """Get enhanced, condition-specific recommendations."""
        recommendations = {
            "immediate": {
                "action": "Seek immediate medical attention",
                "timeframe": "Within 1-2 hours",
                "priority": "Emergency"
            },
            "soon": {
                "action": "Consult pediatrician soon",
                "timeframe": "Within 24 hours",
                "priority": "High"
            },
            "routine": {
                "action": "Schedule routine check-up",
                "timeframe": "Within 1 week",
                "priority": "Medium"
            },
            "monitor": {
                "action": "Monitor symptoms",
                "timeframe": "Continue monitoring",
                "priority": "Low"
            }
        }
        
        base_recommendation = recommendations[urgency]
        
        # Add condition-specific guidance
        condition_guidance = {
            "pneumonia_ari": {
                "monitoring": "Monitor breathing rate and effort",
                "warning_signs": "Increased breathing difficulty, blue lips, refusal to feed",
                "comfort_measures": "Keep upright position, humidified air if available"
            },
            "diarrhea": {
                "monitoring": "Monitor hydration status and stool frequency",
                "warning_signs": "Decreased urine output, sunken eyes, lethargy",
                "comfort_measures": "Continue feeding, offer oral rehydration if age-appropriate"
            },
            "malnutrition": {
                "monitoring": "Monitor feeding patterns and weight",
                "warning_signs": "Further feeding refusal, weight loss, lethargy",
                "comfort_measures": "Encourage frequent small feeds, maintain feeding schedule"
            },
            "neonatal_sepsis": {
                "monitoring": "Monitor temperature, feeding, and consciousness",
                "warning_signs": "High fever, poor feeding, lethargy, irritability",
                "comfort_measures": "Maintain normal temperature, continue feeding if possible"
            },
            "neonatal_jaundice": {
                "monitoring": "Monitor jaundice extent and feeding",
                "warning_signs": "Jaundice spreading to legs, poor feeding, pale stools",
                "comfort_measures": "Ensure adequate feeding, expose to natural light (not direct sun)"
            }
        }
        
        guidance = condition_guidance.get(condition, {})
        
        return {
            **base_recommendation,
            "condition_specific": guidance,
            "evidence_based": True,
            "algorithm_version": "enhanced_2.0"
        }

# Global instance
enhanced_screening_model = EnhancedScreeningModel()

def run_enhanced_screening(condition: str, responses: List[str], age_days: Optional[float] = None) -> Dict:
    """Main function to run enhanced screening."""
    return enhanced_screening_model.calculate_enhanced_score(condition, responses, age_days)

# Test the enhanced screening model
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "condition": "pneumonia_ari",
            "responses": ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "poor feeding"],
            "age_days": 45
        },
        {
            "condition": "diarrhea",
            "responses": ["12 stools per day", "very watery stools", "moderate dehydration signs", "occasional vomiting"],
            "age_days": 30
        },
        {
            "condition": "neonatal_sepsis",
            "responses": ["high fever", "refusing feeds", "lethargic", "very irritable"],
            "age_days": 7
        }
    ]
    
    for test_case in test_cases:
        result = run_enhanced_screening(
            test_case["condition"], 
            test_case["responses"], 
            test_case["age_days"]
        )
        print(f"\n=== {test_case['condition'].upper()} ===")
        print(json.dumps(result, indent=2)) 