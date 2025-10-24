import React, { useState, useRef, useEffect } from 'react';
import { chatWithRAG, queryWithoutRAG } from './api';
import './ChatWidget.css';

export default function ChatWidget() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "Hello! I\'m Nirbhay's personal RAG assistant. Ask me anything about your documents, or ask me anything else!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [topK, setTopK] = useState(5);
  const [showContext, setShowContext] = useState(false);
  const [lastContext, setLastContext] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      text: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      let response;
      if (useRag) {
        response = await chatWithRAG(input, true, topK);
      } else {
        response = await queryWithoutRAG(input);
      }

      // Store context for display
      if (response.context_used) {
        setLastContext(response.context_used);
      }

      const botMessage = {
        id: messages.length + 2,
        type: 'bot',
        text: response.response,
        timestamp: new Date(),
        model: response.model,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        type: 'error',
        text: `Error: ${error.message || 'Failed to get response from server'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearHistory = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        text: 'Hello! I\'m your personal RAG assistant. Ask me anything about your documents, or ask me anything else!',
        timestamp: new Date(),
      },
    ]);
    setLastContext(null);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>📚 Personal RAG Chatbot</h1>
        <p>Powered by Perplexity Sonar + Pinecone</p>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.type}`}>
            <div className="message-content">
              <div className="message-text">{msg.text}</div>
              {msg.model && <div className="message-model">Model: {msg.model}</div>}
              <div className="message-time">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message message-bot loading">
            <div className="message-content">
              <div className="spinner"></div>
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {lastContext && showContext && (
        <div className="context-panel">
          <div className="context-header">
            <h3>📌 Retrieved Context ({lastContext.length} chunks)</h3>
            <button onClick={() => setShowContext(false)}>Close</button>
          </div>
          <div className="context-list">
            {lastContext.map((doc, idx) => (
              <div key={idx} className="context-item">
                <div className="context-header-small">
                  <strong>Chunk {idx + 1}</strong> - {doc.metadata?.filename || 'unknown'}
                </div>
                <div className="context-score">Similarity: {(doc.score * 100).toFixed(1)}%</div>
                <div className="context-text">{doc.text.substring(0, 200)}...</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="chat-options">
        <label className="option-label">
          <input
            type="checkbox"
            checked={useRag}
            onChange={(e) => setUseRag(e.target.checked)}
          />
          Use RAG Context
        </label>
        <label className="option-label">
          Top K Results:
          <input
            type="number"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
            disabled={!useRag}
          />
        </label>
        {lastContext && (
          <button className="show-context-btn" onClick={() => setShowContext(!showContext)}>
            {showContext ? '📖 Hide' : '📖 Show'} Context
          </button>
        )}
        <button className="clear-btn" onClick={clearHistory}>
          🗑️ Clear
        </button>
      </div>

      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question... (Shift+Enter for new line, Enter to send)"
          rows="3"
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
        >
          {loading ? '⏳ Sending...' : '➤ Send'}
        </button>
      </div>
    </div>
  );
}
