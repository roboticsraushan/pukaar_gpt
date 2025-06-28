// API Test Script for Frontend Developer
// Run this with Node.js: node test_api.js

const API_BASE_URL = 'http://34.131.151.166:5000';

// Test data
const testCases = [
  {
    name: "Respiratory Symptoms",
    message: "My baby has fast breathing and yellow skin"
  },
  {
    name: "Emergency Red Flag",
    message: "My baby is not breathing and has blue lips"
  },
  {
    name: "Non-Medical Concern",
    message: "My baby won't sleep through the night"
  },
  {
    name: "Medical Non-Screenable",
    message: "My baby is teething and crying a lot"
  }
];

// Helper function to make API calls
async function makeApiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    }
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${data.error || 'Unknown error'}`);
    }
    
    return data;
  } catch (error) {
    console.error(`Error calling ${endpoint}:`, error.message);
    throw error;
  }
}

// Test functions
async function testTriage(message) {
  console.log('\n🔍 Testing Triage...');
  const result = await makeApiCall('/api/triage', 'POST', { message });
  
  if (result.result) {
    const parsedResult = JSON.parse(result.result);
    console.log('✅ Triage Result:');
    console.log('  - Pneumonia/ARI:', parsedResult.pneumonia_ari + '%');
    console.log('  - Diarrhea:', parsedResult.diarrhea + '%');
    console.log('  - Malnutrition:', parsedResult.malnutrition + '%');
    console.log('  - Neonatal Sepsis:', parsedResult.neonatal_sepsis + '%');
    console.log('  - Neonatal Jaundice:', parsedResult.neonatal_jaundice + '%');
    console.log('  - Looks Normal:', parsedResult.looks_normal + '%');
    console.log('  - Screenable:', parsedResult.screenable);
    console.log('  - Response:', parsedResult.response);
  }
  
  return result;
}

async function testRedFlag(message) {
  console.log('\n🚨 Testing Red Flag Detection...');
  const result = await makeApiCall('/api/red-flag', 'POST', { message });
  
  console.log('✅ Red Flag Result:');
  console.log('  - Red Flag Detected:', result.red_flag_detected);
  if (result.red_flag_detected) {
    console.log('  - Trigger:', result.trigger);
    console.log('  - Recommended Action:', result.recommended_action);
  }
  
  return result;
}

async function testContextClassifier(message) {
  console.log('\n🏷️ Testing Context Classification...');
  const result = await makeApiCall('/api/context-classifier', 'POST', { message });
  
  console.log('✅ Context Classification Result:');
  console.log('  - Classified Context:', result.classified_context);
  console.log('  - Reasoning:', result.reasoning);
  console.log('  - Confidence:', result.confidence);
  console.log('  - Detected Conditions:', result.detected_conditions);
  console.log('  - Next Action:', result.next_action);
  console.log('  - Expert Type:', result.expert_type);
  
  return result;
}

async function testScreeningInfo(condition = 'pneumonia_ari') {
  console.log('\n📋 Testing Screening Information...');
  const result = await makeApiCall(`/api/screening/${condition}`);
  
  console.log('✅ Screening Info Result:');
  console.log('  - Condition:', result.condition);
  console.log('  - Description:', result.description);
  console.log('  - Importance:', result.importance);
  console.log('  - Questions Count:', result.questions.length);
  console.log('  - Disclaimer:', result.disclaimer);
  
  return result;
}

async function testRunScreening(condition = 'pneumonia_ari') {
  console.log('\n🔬 Testing Run Screening...');
  const responses = ['yes', 'no', 'yes', 'yes', '65', 'yes', 'yes'];
  const result = await makeApiCall(`/api/screening/${condition}/run`, 'POST', { responses });
  
  console.log('✅ Run Screening Result:');
  console.log('  - Condition Screened:', result.condition_screened);
  console.log('  - Confidence Score:', result.confidence_score);
  console.log('  - Likelihood:', result.likelihood);
  console.log('  - Recommended Action:', result.recommended_action);
  console.log('  - Red Flag Detected:', result.red_flag_detected);
  console.log('  - Disclaimer:', result.disclaimer);
  
  return result;
}

async function testConsultAdvice(message) {
  console.log('\n💡 Testing Consult Advice...');
  const result = await makeApiCall('/api/consult-advice', 'POST', { message });
  
  console.log('✅ Consult Advice Result:');
  console.log('  - Topic Identified:', result.topic_identified);
  console.log('  - Expert Type:', result.expert_type);
  console.log('  - Response:');
  console.log('    - Acknowledgment:', result.response.acknowledgment);
  console.log('    - Gentle Advice:', result.response.gentle_advice);
  console.log('    - Behavioral Tips:', result.response.behavioral_tips);
  console.log('    - Consultation Offer:', result.response.consultation_offer);
  console.log('    - Disclaimer:', result.response.disclaimer);
  
  return result;
}

async function testFollowupOptions() {
  console.log('\n📞 Testing Follow-up Options...');
  const result = await makeApiCall('/api/followup/options');
  
  console.log('✅ Follow-up Options Result:');
  console.log('  - Options:', result.options);
  
  return result;
}

// Main test function
async function runAllTests() {
  console.log('🚀 Starting Pukaar GPT API Tests...\n');
  
  try {
    // Test each case with all endpoints
    for (const testCase of testCases) {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`📝 Test Case: ${testCase.name}`);
      console.log(`💬 Message: "${testCase.message}"`);
      console.log(`${'='.repeat(60)}`);
      
      // Test triage
      await testTriage(testCase.message);
      
      // Test red flag detection
      await testRedFlag(testCase.message);
      
      // Test context classification
      await testContextClassifier(testCase.message);
      
      // Test consult advice (for non-medical cases)
      if (testCase.name === "Non-Medical Concern") {
        await testConsultAdvice(testCase.message);
      }
    }
    
    // Test screening endpoints
    console.log(`\n${'='.repeat(60)}`);
    console.log('🔬 Testing Screening Endpoints');
    console.log(`${'='.repeat(60)}`);
    
    await testScreeningInfo('pneumonia_ari');
    await testRunScreening('pneumonia_ari');
    
    // Test follow-up options
    console.log(`\n${'='.repeat(60)}`);
    console.log('📞 Testing Follow-up Options');
    console.log(`${'='.repeat(60)}`);
    
    await testFollowupOptions();
    
    console.log('\n🎉 All tests completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  }
}

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  // Node.js environment
  const fetch = require('node-fetch');
  runAllTests();
} else {
  // Browser environment
  window.runAllTests = runAllTests;
  console.log('🌐 Browser environment detected. Call runAllTests() to start testing.');
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testTriage,
    testRedFlag,
    testContextClassifier,
    testScreeningInfo,
    testRunScreening,
    testConsultAdvice,
    testFollowupOptions,
    runAllTests
  };
} 