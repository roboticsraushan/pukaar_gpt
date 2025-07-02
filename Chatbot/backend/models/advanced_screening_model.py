"""
Advanced Screening Model for Infant Health Conditions
Incorporates sophisticated, data-driven logic with evidence-based scoring algorithms
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

class AdvancedScreeningModel:
    def __init__(self):
        # Age-specific risk factors and thresholds
        self.age_risk_factors = {
            "neonatal": {"min_days": 0, "max_days": 28, "risk_multiplier": 1.5},
            "young_infant": {"min_days": 29, "max_days": 90, "risk_multiplier": 1.3},
            "older_infant": {"min_days": 91, "max_days": 365, "risk_multiplier": 1.0}
        }
        
        # Evidence-based symptom weights for pneumonia/ARI
        self.pneumonia_weights = {
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
        }
        
        # Evidence-based symptom weights and interactions
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
        
        # Symptom interaction multipliers
        self.interaction_multipliers = {
            "pneumonia_ari": {
                "respiratory_rate_high + chest_indrawing_moderate": 1.3,
                "respiratory_rate_very_high + cyanosis_mild": 1.5,
                "chest_indrawing_severe + grunting_frequent": 1.4,
                "feeding_refusing + respiratory_rate_high": 1.2
            },
            "diarrhea": {
                "stool_frequency_very_high + dehydration_signs_moderate": 1.3,
                "stool_consistency_very_watery + vomiting_frequent": 1.4,
                "dehydration_signs_severe + feeding_refusing": 1.5
            },
            "malnutrition": {
                "feeding_refusing + weight_losing": 1.4,
                "activity_very_lethargic + visible_signs_severe": 1.3,
                "feeding_poor + weight_slow_gain": 1.2
            },
            "neonatal_sepsis": {
                "temperature_high_fever + consciousness_lethargic": 1.4,
                "feeding_refusing + irritability_inconsolable": 1.3,
                "consciousness_unconscious + temperature_hypothermia": 1.6
            },
            "neonatal_jaundice": {
                "jaundice_extent_below_knees + age_days_15_plus": 1.4,
                "feeding_refusing + stool_color_white": 1.5,
                "jaundice_extent_full_body + age_days_8_14": 1.3
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
    
    def classify_pneumonia_symptoms(self, responses: List[str], numerical_values: Dict[str, float]) -> Dict[str, str]:
        """Classify pneumonia symptoms based on responses."""
        symptom_scores = {}
        
        if len(responses) >= 5:
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
        
        return symptom_scores
    
    def calculate_age_risk_multiplier(self, age_days: float) -> float:
        """Calculate age-based risk multiplier."""
        for age_group, factors in self.age_risk_factors.items():
            if factors["min_days"] <= age_days <= factors["max_days"]:
                return factors["risk_multiplier"]
        return 1.0  # Default for older infants
    
    def calculate_interaction_multiplier(self, symptom_scores: Dict[str, str]) -> float:
        """Calculate interaction multiplier based on symptom combinations."""
        multiplier = 1.0
        
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
        
        # Refusing feeds + high respiratory rate
        if (symptom_scores.get("feeding_status") == "refusing" and 
            symptom_scores.get("respiratory_rate") in ["high", "very_high"]):
            multiplier *= 1.2
        
        return multiplier
    
    def calculate_advanced_pneumonia_score(self, responses: List[str], age_days: Optional[float] = None) -> Dict:
        """Calculate advanced pneumonia screening score."""
        numerical_values = {}
        for response in responses:
            numerical_values.update(self.extract_numerical_values(response))
        
        # Classify symptoms
        symptom_scores = self.classify_pneumonia_symptoms(responses, numerical_values)
        
        # Calculate base weight
        total_weight = 0
        max_possible_weight = 0
        
        for symptom, severity in symptom_scores.items():
            if symptom in self.pneumonia_weights:
                weight = self.pneumonia_weights[symptom].get(severity, {"weight": 0})["weight"]
                total_weight += weight
                max_possible_weight += max(
                    self.pneumonia_weights[symptom][s]["weight"] 
                    for s in self.pneumonia_weights[symptom]
                )
        
        # Apply age risk multiplier
        age_multiplier = self.calculate_age_risk_multiplier(age_days or 30)
        adjusted_weight = total_weight * age_multiplier
        
        # Apply interaction multiplier
        interaction_multiplier = self.calculate_interaction_multiplier(symptom_scores)
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
        thresholds = self.dynamic_thresholds["pneumonia_ari"][age_group]
        
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
            "condition": "pneumonia_ari",
            "percentage_score": round(percentage_score, 1),
            "risk_level": risk_level,
            "urgency": urgency,
            "age_multiplier": age_multiplier,
            "interaction_multiplier": interaction_multiplier,
            "symptom_scores": symptom_scores,
            "thresholds_used": thresholds,
            "age_group": age_group,
            "recommendations": self.get_pneumonia_recommendations(risk_level, urgency, age_days)
        }
    
    def get_pneumonia_recommendations(self, risk_level: str, urgency: str, age_days: Optional[float]) -> Dict:
        """Get pneumonia-specific recommendations."""
        recommendations = {
            "immediate": {
                "action": "Seek immediate medical attention",
                "timeframe": "Within 1-2 hours",
                "priority": "Emergency",
                "monitoring": "Monitor breathing rate and effort",
                "warning_signs": "Increased breathing difficulty, blue lips, refusal to feed",
                "comfort_measures": "Keep upright position, humidified air if available"
            },
            "soon": {
                "action": "Consult pediatrician soon",
                "timeframe": "Within 24 hours",
                "priority": "High",
                "monitoring": "Monitor breathing rate and effort",
                "warning_signs": "Increased breathing difficulty, blue lips, refusal to feed",
                "comfort_measures": "Keep upright position, humidified air if available"
            },
            "routine": {
                "action": "Schedule routine check-up",
                "timeframe": "Within 1 week",
                "priority": "Medium",
                "monitoring": "Monitor breathing rate and effort",
                "warning_signs": "Increased breathing difficulty, blue lips, refusal to feed",
                "comfort_measures": "Keep upright position, humidified air if available"
            },
            "monitor": {
                "action": "Monitor symptoms",
                "timeframe": "Continue monitoring",
                "priority": "Low",
                "monitoring": "Monitor breathing rate and effort",
                "warning_signs": "Increased breathing difficulty, blue lips, refusal to feed",
                "comfort_measures": "Keep upright position, humidified air if available"
            }
        }
        
        base_recommendation = recommendations[urgency]
        
        return {
            **base_recommendation,
            "evidence_based": True,
            "algorithm_version": "2.0"
        }

# Global instance
advanced_screening_model = AdvancedScreeningModel()

def run_advanced_pneumonia_screening(responses: List[str], age_days: Optional[float] = None) -> Dict:
    """Main function to run advanced pneumonia screening."""
    return advanced_screening_model.calculate_advanced_pneumonia_score(responses, age_days)

# Test the advanced screening model
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "responses": ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "poor feeding"],
            "age_days": 45
        },
        {
            "responses": ["75 breaths per minute", "severe chest indrawing", "continuous grunting", "mild cyanosis", "refusing feeds"],
            "age_days": 7
        },
        {
            "responses": ["normal breathing", "no chest indrawing", "no grunting", "no cyanosis", "normal feeding"],
            "age_days": 90
        }
    ]
    
    for test_case in test_cases:
        result = run_advanced_pneumonia_screening(
            test_case["responses"], 
            test_case["age_days"]
        )
        print(f"\n=== PNEUMONIA SCREENING ===")
        print(f"Age: {test_case['age_days']} days")
        print(f"Responses: {test_case['responses']}")
        print(json.dumps(result, indent=2)) 