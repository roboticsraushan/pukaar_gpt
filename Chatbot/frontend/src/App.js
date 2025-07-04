import React, { useState } from 'react';
import './App.css';

// Tree View Component for JSON display
const JsonTreeView = ({ data, level = 0 }) => {
  const [expanded, setExpanded] = useState(level < 2); // Auto-expand first 2 levels
  
  if (typeof data === 'object' && data !== null) {
    const isArray = Array.isArray(data);
    const items = isArray ? data : Object.entries(data);
    
    return (
      <div style={{ marginLeft: level * 20 }}>
        <div 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer',
            fontWeight: 'bold',
            color: '#2b7a78'
          }}
          onClick={() => setExpanded(!expanded)}
        >
          <span style={{ marginRight: '8px', fontSize: '14px' }}>
            {expanded ? '▼' : '▶'}
          </span>
          <span style={{ color: isArray ? '#d63384' : '#0d6efd' }}>
            {isArray ? '[' : '{'}
          </span>
        </div>
        
        {expanded && (
          <div style={{ marginLeft: '20px' }}>
            {items.map((item, index) => {
              const key = isArray ? index : item[0];
              const value = isArray ? item : item[1];
              const isLast = index === items.length - 1;
              
              return (
                <div key={index}>
                  <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <span style={{ color: '#6c757d', marginRight: '8px' }}>
                      "{key}":
                    </span>
                    {typeof value === 'object' && value !== null ? (
                      <JsonTreeView data={value} level={level + 1} />
                    ) : (
                      <span style={{ 
                        color: typeof value === 'string' ? '#198754' : 
                               typeof value === 'number' ? '#fd7e14' : 
                               typeof value === 'boolean' ? '#6f42c1' : '#6c757d'
                      }}>
                        {typeof value === 'string' ? `"${value}"` : String(value)}
                      </span>
                    )}
                    {!isLast && <span style={{ color: '#6c757d' }}>,</span>}
                  </div>
                </div>
              );
            })}
            <div style={{ color: isArray ? '#d63384' : '#0d6efd' }}>
              {isArray ? ']' : '}'}
            </div>
          </div>
        )}
        
        {!expanded && (
          <span style={{ color: '#6c757d', marginLeft: '8px' }}>
            ...
          </span>
        )}
      </div>
    );
  }
  
  return (
    <span style={{ 
      color: typeof data === 'string' ? '#198754' : 
             typeof data === 'number' ? '#fd7e14' : 
             typeof data === 'boolean' ? '#6f42c1' : '#6c757d'
    }}>
      {typeof data === 'string' ? `"${data}"` : String(data)}
    </span>
  );
};

// Status Badge Component
const StatusBadge = ({ label, value, color }) => (
  <div style={{ 
    display: 'inline-block',
    padding: '4px 8px',
    margin: '0 5px',
    backgroundColor: color,
    color: 'white',
    borderRadius: '4px',
    fontWeight: 'bold',
    fontSize: '0.85rem'
  }}>
    {label}: {value}
  </div>
);

function App() {
  console.log('App component loaded');
  const [inputText, setInputText] = useState('');
  const [screeningResult, setScreeningResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [flowType, setFlowType] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);

  const handleSubmit = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setErrorMsg('');

    // Add user message to conversation history
    const userMessage = { role: 'user', content: inputText };
    setConversationHistory(prev => [...prev, userMessage]);

    // Use Docker service name in container, fallback to localhost for development
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    try {
      // Always use /api/screen for all messages
      const response = await fetch(`${apiUrl}/api/screen`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputText,
          session_id: sessionId // null/undefined for first message, set for follow-ups
        }),
      });

      const data = await response.json();
      if (response.ok) {
        if (data.session_id) setSessionId(data.session_id);
        if (data.flow_type) setFlowType(data.flow_type);
        if (data.current_step !== undefined) setCurrentStep(data.current_step);
        const systemResponse = { 
          role: 'system', 
          content: data.response || data.result || JSON.stringify(data)
        };
        setConversationHistory(prev => [...prev, systemResponse]);
        setScreeningResult(data);
      } else {
        setErrorMsg(data.error || 'Something went wrong.');
      }
    } catch (error) {
      setErrorMsg('Unable to connect to server.');
    }
    setLoading(false);
    setInputText(''); // Clear input field after sending
  };

  return (
    <div className="App" style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#2b7a78' }}>🧒 Pukaar Health Screening</h1>
      
      {/* Session and Flow Status Bar */}
      <div style={{ 
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '20px',
        padding: '10px',
        backgroundColor: '#f0f0f0',
        borderRadius: '8px'
      }}>
        {sessionId && (
          <StatusBadge 
            label="Session ID" 
            value={sessionId.substring(0, 8) + '...'} 
            color="#6c757d"
          />
        )}
        {flowType && (
          <StatusBadge 
            label="Flow Type" 
            value={flowType} 
            color="#0d6efd"
          />
        )}
        {currentStep !== null && currentStep !== undefined && (
          <StatusBadge 
            label="Current Step" 
            value={currentStep} 
            color="#198754"
          />
        )}
        {/* Show Follow-up badge if in follow_up mode */}
        {flowType === 'follow_up' && (
          <StatusBadge 
            label="Follow-up" 
            value="Active" 
            color="#f59e42"
          />
        )}
        {/* Show Red Flag badge if in red_flag mode */}
        {flowType === 'red_flag' && (
          <StatusBadge 
            label="URGENT" 
            value="Red Flag" 
            color="#d9534f"
          />
        )}
      </div>
      
      <p style={{ fontStyle: 'italic', color: '#444' }}>
        This is not a medical diagnosis. It is a screening tool based on WHO, IMNCI, and IAP guidelines to help identify potential warning signs. Please consult a pediatrician if unsure.
      </p>

      {/* Conversation History */}
      <div style={{
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '15px',
        marginBottom: '20px',
        maxHeight: '300px',
        overflowY: 'auto',
        backgroundColor: '#f9f9f9',
        textAlign: 'left'
      }}>
        {conversationHistory.length === 0 ? (
          <p style={{ color: '#6c757d', textAlign: 'center' }}>Your conversation will appear here...</p>
        ) : (
          conversationHistory.map((msg, index) => {
            // Highlight urgent responses
            const isUrgent = (flowType === 'red_flag' && msg.role === 'system') ||
              (msg.content && (msg.content.includes('URGENT') || msg.content.includes('⚠️')));
            let displayContent = msg.content;
            // For system messages, extract 'response' or 'message' if content is a JSON string or object
            if (msg.role === 'system') {
              try {
                let parsed = typeof msg.content === 'string' ? JSON.parse(msg.content) : msg.content;
                if (parsed && typeof parsed === 'object') {
                  displayContent = parsed.response || parsed.message || JSON.stringify(parsed);
                }
              } catch (e) {
                // Not JSON, use as is
              }
            }
            return (
              <div 
                key={index} 
                style={{
                  padding: '8px 12px',
                  margin: '8px 0',
                  borderRadius: '8px',
                  backgroundColor: isUrgent ? '#ffe5e5' : (msg.role === 'user' ? '#e2f0fb' : '#f0f7e6'),
                  border: isUrgent ? '2px solid #d9534f' : 'none',
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '80%',
                  marginLeft: msg.role === 'user' ? 'auto' : '0',
                  boxShadow: isUrgent ? '0 0 8px #d9534f55' : 'none'
                }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                  {msg.role === 'user' ? '👤 You:' : '🤖 Pukaar:'}
                </div>
                <div style={{ fontWeight: isUrgent ? 'bold' : 'normal', color: isUrgent ? '#d9534f' : undefined }}>
                  {displayContent}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div style={{ display: 'flex', marginBottom: '1rem' }}>
        <textarea
          rows="3"
          placeholder="Describe your baby's symptoms here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          style={{
            flex: 1,
            padding: '10px',
            fontSize: '16px',
            borderRadius: '8px 0 0 8px',
            border: '1px solid #ccc',
            borderRight: 'none'
          }}
        />
        <button
          onClick={() => {
            console.log('Button clicked!');
            handleSubmit();
          }}
          style={{
            backgroundColor: '#3aafa9',
            color: '#fff',
            border: 'none',
            padding: '10px 20px',
            fontSize: '16px',
            borderRadius: '0 6px 6px 0',
            cursor: 'pointer',
          }}
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>

      {errorMsg && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{errorMsg}</p>
      )}

      {screeningResult && (
        <div
          style={{
            marginTop: '2rem',
            padding: '1rem',
            border: '1px solid #ddd',
            borderRadius: '8px',
            backgroundColor: '#f9f9f9',
          }}
        >
          <h3>🔍 Screening Result</h3>

          {screeningResult.screenable === false ? (
            <p style={{ color: '#d9534f' }}>{screeningResult.response}</p>
          ) : (
            <div>
              {/* Display condition scores */}
              {Object.entries(screeningResult)
                .filter(([key]) => 
                  key !== "screenable" && 
                  key !== "response" && 
                  key !== "other_issue_detected" &&
                  typeof screeningResult[key] === 'number'
                )
                .sort(([, a], [, b]) => b - a)
                .map(([condition, score], index) => (
                  <div key={index} style={{ marginBottom: '10px' }}>
                    <strong style={{ textTransform: 'capitalize' }}>
                      {condition.replace(/_/g, ' ')}:
                    </strong> {score}%
                  </div>
                ))
              }
              
              {/* Display response if available */}
              {screeningResult.response && (
                <div style={{ 
                  marginTop: '15px', 
                  padding: '10px', 
                  backgroundColor: '#e7f3ff', 
                  borderRadius: '5px',
                  borderLeft: '4px solid #007bff'
                }}>
                  <strong>Explanation:</strong> {screeningResult.response}
                </div>
              )}
            </div>
          )}

          <div
            style={{
              marginTop: '1rem',
              backgroundColor: '#f8f9fa',
              padding: '1rem',
              borderRadius: '6px',
              border: '1px solid #dee2e6',
              fontFamily: 'monospace',
              fontSize: '13px',
              lineHeight: '1.5',
              maxHeight: '400px',
              overflowY: 'auto'
            }}
          >
            <div style={{ marginBottom: '10px', fontWeight: 'bold', color: '#495057' }}>
              📊 Detailed Results (Click to expand/collapse):
            </div>
            <JsonTreeView data={screeningResult} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
