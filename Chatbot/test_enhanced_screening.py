#!/usr/bin/env python3
"""
Test script for Enhanced Screening Model
Demonstrates the sophisticated, data-driven screening logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models.screening_model import run_screening
from backend.models.enhanced_screening_model import run_enhanced_screening
import json

def test_enhanced_screening():
    """Test the enhanced screening capabilities."""
    
    print("🚀 Testing Enhanced Screening Model")
    print("=" * 60)
    
    # Test cases with different scenarios
    test_cases = [
        {
            "condition": "pneumonia_ari",
            "responses": ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "poor feeding", "baby is 45 days old"],
            "description": "Moderate pneumonia symptoms in young infant"
        },
        {
            "condition": "pneumonia_ari",
            "responses": ["75 breaths per minute", "severe chest indrawing", "continuous grunting", "mild cyanosis", "refusing feeds", "baby is 7 days old"],
            "description": "Severe pneumonia symptoms in neonate"
        },
        {
            "condition": "pneumonia_ari",
            "responses": ["normal breathing", "no chest indrawing", "no grunting", "no cyanosis", "normal feeding", "baby is 90 days old"],
            "description": "Normal respiratory symptoms in older infant"
        },
        {
            "condition": "diarrhea",
            "responses": ["12 stools per day", "very watery stools", "moderate dehydration signs", "occasional vomiting", "baby is 30 days old"],
            "description": "Severe diarrhea with dehydration in young infant"
        },
        {
            "condition": "diarrhea",
            "responses": ["5 stools per day", "loose stools", "no dehydration signs", "no vomiting", "baby is 120 days old"],
            "description": "Mild diarrhea in older infant"
        },
        {
            "condition": "neonatal_sepsis",
            "responses": ["high fever", "refusing feeds", "lethargic", "very irritable", "baby is 7 days old"],
            "description": "Severe sepsis symptoms in neonate"
        },
        {
            "condition": "neonatal_jaundice",
            "responses": ["yellow below knees", "baby is 15 days old", "poor feeding", "white stool"],
            "description": "Severe jaundice with concerning signs"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print("-" * 50)
        print(f"Condition: {test_case['condition']}")
        print(f"Responses: {test_case['responses']}")
        
        # Run enhanced screening
        try:
            enhanced_result = run_enhanced_screening(
                test_case["condition"], 
                test_case["responses"]
            )
            
            print(f"\n🔬 Enhanced Screening Result:")
            print(f"  Risk Level: {enhanced_result.get('risk_level', 'N/A')}")
            print(f"  Urgency: {enhanced_result.get('urgency', 'N/A')}")
            print(f"  Score: {enhanced_result.get('percentage_score', 'N/A')}%")
            print(f"  Age Group: {enhanced_result.get('age_group', 'N/A')}")
            print(f"  Age Multiplier: {enhanced_result.get('age_multiplier', 'N/A')}")
            print(f"  Interaction Multiplier: {enhanced_result.get('interaction_multiplier', 'N/A')}")
            print(f"  Algorithm Version: {enhanced_result.get('algorithm_version', 'N/A')}")
            
            if 'symptom_scores' in enhanced_result:
                print(f"  Symptom Scores: {enhanced_result['symptom_scores']}")
            
            if 'recommendations' in enhanced_result:
                rec = enhanced_result['recommendations']
                print(f"  Action: {rec.get('action', 'N/A')}")
                print(f"  Timeframe: {rec.get('timeframe', 'N/A')}")
                print(f"  Priority: {rec.get('priority', 'N/A')}")
                if 'condition_specific' in rec:
                    cs = rec['condition_specific']
                    print(f"  Monitoring: {cs.get('monitoring', 'N/A')}")
                    print(f"  Warning Signs: {cs.get('warning_signs', 'N/A')}")
                    print(f"  Comfort Measures: {cs.get('comfort_measures', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Enhanced screening failed: {e}")
        
        print("\n" + "=" * 60)

def test_legacy_vs_enhanced():
    """Compare legacy and enhanced screening results."""
    
    print("\n🔄 Comparing Legacy vs Enhanced Screening")
    print("=" * 60)
    
    # Test case for comparison
    test_case = {
        "condition": "pneumonia_ari",
        "responses": ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "poor feeding", "baby is 45 days old"]
    }
    
    print(f"Test Case: {test_case['condition']}")
    print(f"Responses: {test_case['responses']}")
    
    # Run legacy screening (by temporarily disabling enhanced mode)
    from backend.models.screening_model import screening_agent
    original_mode = screening_agent.use_enhanced_screening
    screening_agent.use_enhanced_screening = False
    
    try:
        legacy_result = run_screening(test_case["condition"], test_case["responses"])
        print(f"\n📊 Legacy Screening Result:")
        print(f"  Confidence Score: {legacy_result.get('confidence_score', 'N/A')}%")
        print(f"  Likelihood: {legacy_result.get('likelihood', 'N/A')}")
        print(f"  Recommended Action: {legacy_result.get('recommended_action', 'N/A')}")
        print(f"  Algorithm Version: {legacy_result.get('algorithm_version', 'N/A')}")
    except Exception as e:
        print(f"❌ Legacy screening failed: {e}")
    
    # Restore enhanced mode
    screening_agent.use_enhanced_screening = original_mode
    
    # Run enhanced screening
    try:
        enhanced_result = run_enhanced_screening(test_case["condition"], test_case["responses"])
        print(f"\n🔬 Enhanced Screening Result:")
        print(f"  Risk Level: {enhanced_result.get('risk_level', 'N/A')}")
        print(f"  Urgency: {enhanced_result.get('urgency', 'N/A')}")
        print(f"  Score: {enhanced_result.get('percentage_score', 'N/A')}%")
        print(f"  Age Group: {enhanced_result.get('age_group', 'N/A')}")
        print(f"  Age Multiplier: {enhanced_result.get('age_multiplier', 'N/A')}")
        print(f"  Interaction Multiplier: {enhanced_result.get('interaction_multiplier', 'N/A')}")
        print(f"  Algorithm Version: {enhanced_result.get('algorithm_version', 'N/A')}")
        
        if 'recommendations' in enhanced_result:
            rec = enhanced_result['recommendations']
            print(f"  Action: {rec.get('action', 'N/A')}")
            print(f"  Timeframe: {rec.get('timeframe', 'N/A')}")
            print(f"  Priority: {rec.get('priority', 'N/A')}")
    except Exception as e:
        print(f"❌ Enhanced screening failed: {e}")

def test_age_specific_scenarios():
    """Test age-specific risk factors and thresholds."""
    
    print("\n👶 Testing Age-Specific Risk Factors")
    print("=" * 60)
    
    # Same symptoms, different ages
    base_responses = ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "poor feeding"]
    
    age_scenarios = [
        {"age": 7, "description": "Neonate (7 days)"},
        {"age": 45, "description": "Young infant (45 days)"},
        {"age": 120, "description": "Older infant (120 days)"}
    ]
    
    for scenario in age_scenarios:
        responses = base_responses + [f"baby is {scenario['age']} days old"]
        
        print(f"\n📋 {scenario['description']}")
        print(f"Responses: {responses}")
        
        try:
            result = run_enhanced_screening("pneumonia_ari", responses)
            
            print(f"  Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"  Score: {result.get('percentage_score', 'N/A')}%")
            print(f"  Age Group: {result.get('age_group', 'N/A')}")
            print(f"  Age Multiplier: {result.get('age_multiplier', 'N/A')}")
            print(f"  Thresholds Used: {result.get('thresholds_used', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")

def test_symptom_interactions():
    """Test symptom interaction multipliers."""
    
    print("\n🔗 Testing Symptom Interactions")
    print("=" * 60)
    
    # Test different symptom combinations
    interaction_tests = [
        {
            "responses": ["65 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "normal feeding"],
            "description": "High RR + Chest Indrawing (should trigger 1.3x multiplier)"
        },
        {
            "responses": ["75 breaths per minute", "moderate chest indrawing", "frequent grunting", "mild cyanosis", "normal feeding"],
            "description": "Very High RR + Cyanosis (should trigger 1.5x multiplier)"
        },
        {
            "responses": ["65 breaths per minute", "severe chest indrawing", "continuous grunting", "no cyanosis", "normal feeding"],
            "description": "Severe Chest Indrawing + Continuous Grunting (should trigger 1.4x multiplier)"
        },
        {
            "responses": ["75 breaths per minute", "moderate chest indrawing", "frequent grunting", "no cyanosis", "refusing feeds"],
            "description": "Very High RR + Refusing Feeds (should trigger 1.2x multiplier)"
        }
    ]
    
    for i, test in enumerate(interaction_tests, 1):
        responses = test["responses"] + ["baby is 45 days old"]
        
        print(f"\n📋 Test {i}: {test['description']}")
        print(f"Responses: {responses}")
        
        try:
            result = run_enhanced_screening("pneumonia_ari", responses)
            
            print(f"  Interaction Multiplier: {result.get('interaction_multiplier', 'N/A')}")
            print(f"  Final Score: {result.get('percentage_score', 'N/A')}%")
            print(f"  Risk Level: {result.get('risk_level', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")

def main():
    """Run all tests."""
    print("🏥 Pukaar-GPT Enhanced Screening Model Tests")
    print("=" * 60)
    
    # Run all test suites
    test_enhanced_screening()
    test_legacy_vs_enhanced()
    test_age_specific_scenarios()
    test_symptom_interactions()
    
    print("\n✅ All tests completed!")
    print("\n📈 Key Improvements in Enhanced Screening:")
    print("  • Age-specific risk factors and thresholds")
    print("  • Evidence-based symptom weighting")
    print("  • Symptom interaction multipliers")
    print("  • Dynamic threshold adjustment")
    print("  • Condition-specific recommendations")
    print("  • Backward compatibility with legacy system")

if __name__ == "__main__":
    main() 