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

function App() {
  console.log('App component loaded');
  const [inputText, setInputText] = useState('');
  const [screeningResult, setScreeningResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setErrorMsg('');
    setScreeningResult(null);

    // Use Docker service name in container, fallback to localhost for development
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    console.log('API URL:', apiUrl);
    console.log('Sending message:', inputText);
    
    try {
      console.log('Making fetch request to:', `${apiUrl}/api/triage`);
      const response = await fetch(`${apiUrl}/api/triage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputText }),
      });

      console.log('Raw response:', response);
      const data = await response.json();
      console.log('Parsed response JSON:', data);
      if (response.ok) {
        // Handle the response structure where result is a JSON string
        if (data.result) {
          try {
            // Parse the result string back to JSON object
            console.log('Trying to parse data.result:', data.result);
            const parsedResult = JSON.parse(data.result);
            setScreeningResult(parsedResult);
            console.log('Parsed result object:', parsedResult);
          } catch (parseError) {
            console.error('Error parsing result:', parseError);
            setScreeningResult(data.result); // Fallback to raw string
          }
        } else {
          setScreeningResult(data);
        }
      } else {
        setErrorMsg(data.error || 'Something went wrong.');
      }
    } catch (error) {
      console.error('Error:', error);
      setErrorMsg('Unable to connect to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App" style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#2b7a78' }}>🧒 Pukaar Health Screening</h1>
      <p style={{ fontStyle: 'italic', color: '#444' }}>
        This is not a medical diagnosis. It is a screening tool based on WHO, IMNCI, and IAP guidelines to help identify potential warning signs. Please consult a pediatrician if unsure.
      </p>

      <textarea
        rows="4"
        cols="50"
        placeholder="Describe your baby's symptoms here..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        style={{
          width: '100%',
          padding: '10px',
          fontSize: '16px',
          borderRadius: '8px',
          border: '1px solid #ccc',
          marginBottom: '1rem',
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
          borderRadius: '6px',
          cursor: 'pointer',
        }}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Run Screening'}
      </button>

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
