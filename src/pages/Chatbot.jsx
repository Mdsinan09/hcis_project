import React, { useState, useEffect } from 'react';
import { MessageSquare, Send, Trash2, Loader } from 'lucide-react';
import axios from '../utils/axios';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false); 

  // Function to determine if there are recent results to use as context
  const getRecentAnalysisContext = async () => {
    try {
      // Fetch the latest analysis result from the history endpoint
      const { data: history } = await axios.get('/history');
      // Return the full report object of the most recent item, or null
      return history.length > 0 ? history[0] : null; 
    } catch {
      return null;
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userInput = input.trim();
    
    // 1. Add user message and placeholder to history
    setMessages(prev => [...prev, { role: 'user', content: userInput, timestamp: Date.now() }]);
    setMessages(prev => [...prev, { role: 'assistant', content: "thinking...", isPlaceholder: true, timestamp: Date.now() + 1 }]);
    setInput('');
    setIsLoading(true);

    try {
      // 2. Fetch context (most recent analysis)
      const context = await getRecentAnalysisContext();
      
      // 3. Prepare payload for general chat
      const payload = {
        question: userInput,
        // Pass the most recent full report object to the backend for context
        context: context || {} 
      };

      // 4. Wait for the API response
      const { data } = await axios.post('/chat', payload); 
      
      const botResponse = data.response || 'No response from assistant.';
      
      // 5. Replace placeholder with bot response
      setMessages(prev => {
          const newMessages = prev.filter(m => !m.isPlaceholder);
          return [...newMessages, { role: 'assistant', content: botResponse, timestamp: Date.now() + 2 }];
      });
      
    } catch (err) {
      console.error("Chat API Error:", err.response ? err.response.data : err.message);
      
      // Replace placeholder with error message
      setMessages(prev => {
        const newMessages = prev.filter(m => !m.isPlaceholder);
        return [...newMessages, { role: 'assistant', content: 'Sorry, I encountered an error. Please check the backend log for details.', timestamp: Date.now() + 2 }];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSend();
    }
  };

  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear the entire chat history?")) {
        setMessages([]);
    }
  };


  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px', height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '42px', fontWeight: '800', marginBottom: '12px', background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          🤖 AI Assistant
        </h1>
        <p style={{ fontSize: '16px', opacity: 0.7, color: 'var(--text-color)' }}>
          Ask anything about deepfake detection and AI-generated content
        </p>
      </div>

      <div style={{
        flex: 1,
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        padding: '24px',
        overflowY: 'auto',
        marginBottom: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
      }}>
        {messages.length === 0 && !isLoading ? (
          <div style={{ textAlign: 'center', opacity: 0.5, marginTop: '60px' }}>
            <MessageSquare size={64} style={{ marginBottom: '16px', opacity: 0.3 }} />
            <p style={{ color: 'var(--text-color)' }}>Start a conversation by asking a question</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{
              marginBottom: '16px',
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '16px 20px',
                borderRadius: '16px',
                background: msg.role === 'user' 
                  ? 'linear-gradient(135deg, #3b82f6, #8b5cf6)'
                  : 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: msg.role === 'user' ? 'white' : 'var(--text-color)'
              }}>
                {msg.isPlaceholder ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', opacity: 0.6 }}>
                        <Loader size={18} className="animate-spin" />
                        <p style={{ margin: 0 }}>Assistant is typing...</p>
                    </div>
                ) : (
                    <p style={{ margin: 0, lineHeight: '1.6' }}>{msg.content}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input and Buttons */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isLoading ? "Please wait for the response..." : "Type your question..."}
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '16px 20px',
            borderRadius: '16px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            fontSize: '16px',
            outline: 'none',
            color: 'var(--text-color)',
            transition: 'all 0.3s',
            opacity: isLoading ? 0.7 : 1,
          }}
        />
        <button 
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            padding: '16px',
            borderRadius: '16px',
            border: 'none',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            opacity: isLoading ? 0.5 : 1,
            transition: 'all 0.3s'
          }}
        >
          {isLoading ? <Loader size={20} className="animate-spin" /> : <Send size={20} />}
        </button>
        <button 
          onClick={handleClearChat}
          style={{
            padding: '16px',
            borderRadius: '16px',
            border: 'none',
            background: 'rgba(239, 68, 68, 0.8)',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            opacity: messages.length === 0 ? 0.5 : 1,
            transition: 'all 0.3s'
          }}
          disabled={messages.length === 0}
        >
          <Trash2 size={20} />
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
