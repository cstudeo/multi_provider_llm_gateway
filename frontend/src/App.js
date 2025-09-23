import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [userId, setUserId] = useState('');
  const [model, setModel] = useState('');
  const [maxTokens, setMaxTokens] = useState('');
  const [temperature, setTemperature] = useState('');
  const [rateLimits, setRateLimits] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const messagesEndRef = useRef(null);

  // Load providers and rate limits on component mount
  useEffect(() => {
    loadProviders();
    loadRateLimits();
  }, []);

  // Load rate limits when provider changes
  useEffect(() => {
    if (selectedProvider) {
      loadRateLimits();
    }
  }, [selectedProvider, userId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadProviders = async () => {
    try {
      const response = await axios.get('/providers');
      setProviders(response.data.providers);
      if (response.data.providers.length > 0) {
        setSelectedProvider(response.data.providers[0]);
      }
    } catch (err) {
      setError('Failed to load providers: ' + err.message);
    }
  };

  const loadRateLimits = async () => {
    if (!selectedProvider) return;
    
    try {
      const params = userId ? { user_id: userId } : {};
      const response = await axios.get(`/rate-limit/${selectedProvider}`, { params });
      setRateLimits(response.data.rate_limits);
    } catch (err) {
      console.error('Failed to load rate limits:', err.message);
    }
  };

  const generateResponse = async (useFailover = false) => {
    if (!selectedProvider || !currentMessage.trim()) {
      setError('Please select a provider and enter a message');
      return;
    }

    const userMessage = currentMessage.trim();
    
    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newUserMessage]);

    setLoading(true);
    setError(null);
    setCurrentMessage('');

    try {
      const requestData = {
        prompt: userMessage,
        user_id: userId || undefined,
        model: model || undefined,
        max_tokens: maxTokens ? parseInt(maxTokens) : undefined,
        temperature: temperature ? parseFloat(temperature) : undefined,
      };

      // Remove undefined values
      Object.keys(requestData).forEach(key => {
        if (requestData[key] === undefined) {
          delete requestData[key];
        }
      });

      const endpoint = useFailover ? '/generate/failover' : '/generate';
      const data = useFailover 
        ? { preferred_provider: selectedProvider, ...requestData }
        : { provider: selectedProvider, ...requestData };

      const response = await axios.post(endpoint, data);
      
      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.data.response.content,
        provider: response.data.response.provider,
        model: response.data.response.model,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Refresh rate limits after successful generation
      loadRateLimits();
    } catch (err) {
      if (err.response?.status === 429) {
        setError(`Rate limit exceeded: ${err.response.data.message}`);
        setRateLimits(err.response.data.rate_limit_info);
      } else {
        setError(err.response?.data?.message || err.message || 'Generation failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = () => generateResponse(false);
  const handleFailover = () => generateResponse(true);
  
  const clearChat = () => {
    setMessages([]);
    setError(null);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const getRateLimitPercentage = (current, limit) => {
    return Math.min((current / limit) * 100, 100);
  };

  return (
    <div className="container">
      <header className="header">
        <h1><i className="fas fa-robot"></i> Multi-Provider AI Chat</h1>
        <p>Chat with OpenAI, Anthropic, and Google Gemini - with automatic failover</p>
      </header>

      <div className="main-content">
        {/* Configuration Panel */}
        <div className="card config-panel">
          <div className="config-row">
            <div className="form-group">
              <label htmlFor="provider">Provider:</label>
              <select 
                id="provider"
                className="form-control"
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
              >
                {providers.map(provider => (
                  <option key={provider} value={provider}>
                    {provider.charAt(0).toUpperCase() + provider.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="userId">User ID:</label>
              <input
                type="text"
                id="userId"
                className="form-control"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="Optional"
              />
            </div>
            <div className="form-group">
              <label htmlFor="model">Model:</label>
              <input
                type="text"
                id="model"
                className="form-control"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="Default"
              />
            </div>
            <button 
              className="btn btn-secondary clear-btn"
              onClick={clearChat}
              title="Clear Chat History"
            >
              <i className="fas fa-trash"></i>
              Clear Chat
            </button>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="card chat-container">
          <div className="chat-header">
            <h2><i className="fas fa-comments"></i> Chat with AI</h2>
            <div className="chat-controls">
              <div className="form-group inline">
                <label htmlFor="maxTokens">Max Tokens:</label>
                <input
                  type="number"
                  id="maxTokens"
                  className="form-control small"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(e.target.value)}
                  placeholder="100"
                  min="1"
                  max="4000"
                />
              </div>
              <div className="form-group inline">
                <label htmlFor="temperature">Temperature:</label>
                <input
                  type="number"
                  id="temperature"
                  className="form-control small"
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                  placeholder="0.7"
                  min="0"
                  max="2"
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          <div className="chat-messages" id="chatMessages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <div className="welcome-icon">
                  <i className="fas fa-robot"></i>
                </div>
                <h3>Welcome to Multi-Provider AI Chat!</h3>
                <p>Start a conversation by typing a message below. You can switch between different AI providers and use failover for maximum reliability.</p>
                <div className="features">
                  <div className="feature">
                    <i className="fas fa-sync-alt"></i>
                    <span>Automatic Failover</span>
                  </div>
                  <div className="feature">
                    <i className="fas fa-cogs"></i>
                    <span>Multiple Providers</span>
                  </div>
                  <div className="feature">
                    <i className="fas fa-history"></i>
                    <span>Chat History</span>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className={`message ${message.type}`}>
                  <div className="message-avatar">
                    {message.type === 'user' ? (
                      <i className="fas fa-user"></i>
                    ) : (
                      <i className="fas fa-robot"></i>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="message-sender">
                        {message.type === 'user' ? 'You' : `${message.provider} (${message.model})`}
                      </span>
                      <span className="message-time">{message.timestamp}</span>
                    </div>
                    <div className="message-text">{message.content}</div>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="message ai">
                <div className="message-avatar">
                  <i className="fas fa-robot"></i>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span>AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input">
            <div className="input-container">
              <textarea
                className="message-input"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                rows="1"
                disabled={loading}
              />
              <div className="input-buttons">
                <button 
                  className="btn btn-primary send-btn"
                  onClick={handleGenerate}
                  disabled={loading || !currentMessage.trim()}
                  title="Send Message"
                >
                  <i className="fas fa-paper-plane"></i>
                </button>
                <button 
                  className="btn btn-secondary failover-btn"
                  onClick={handleFailover}
                  disabled={loading || !currentMessage.trim()}
                  title="Send with Failover"
                >
                  <i className="fas fa-sync-alt"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Rate Limits */}
        {Object.keys(rateLimits).length > 0 && (
          <div className="card">
            <div className="rate-limit-section">
              <h3><i className="fas fa-tachometer-alt"></i> Rate Limit Status</h3>
              {Object.entries(rateLimits).map(([key, limit]) => (
                <div key={key} className="rate-limit-item">
                  <div className="rate-limit-label">
                    <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                    <span>{limit.current_count || 0} / {limit.limit}</span>
                  </div>
                  <div className="rate-limit-bar">
                    <div 
                      className={`rate-limit-fill ${
                        getRateLimitPercentage(limit.current_count || 0, limit.limit) > 80 ? 'high' :
                        getRateLimitPercentage(limit.current_count || 0, limit.limit) > 60 ? 'medium' : 'low'
                      }`}
                      style={{ width: `${getRateLimitPercentage(limit.current_count || 0, limit.limit)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Modal */}
      {error && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-exclamation-triangle"></i> Error</h3>
              <button 
                className="modal-close"
                onClick={() => setError(null)}
              >
                &times;
              </button>
            </div>
            <div className="modal-body">
              <div className="error-message">{error}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;