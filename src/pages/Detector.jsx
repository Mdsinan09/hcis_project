import React, { useState } from 'react';
import { Camera, Upload, FileVideo, FileAudio, FileText, Download, X, Sparkles, Send, Plus, Minus } from 'lucide-react';
import { addReportToHistory } from '../utils/history'; // Utility to add to local history/list
import jsPDF from 'jspdf'; // For local PDF generation
import axios from '../utils/axios'; // Configured Axios instance

// --- Utility Functions ---
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 📢 FIX: Corrected getStatus logic for N/A (0 or null scores)
const getStatus = (value, isActive = true) => {
  const score = parseFloat(value); 
  
  // If explicitly 0, or not active, treat as Not Analyzed (N/A)
  if (!isActive || isNaN(score) || score === null || score === 0) {
    return { label: 'N/A', color: '#6b7280' }; 
  }
  if (score < 40) return { label: 'Fabricated', color: '#ef4444' };
  if (score < 70) return { label: 'Suspicious', color: '#f59e0b' };
  return { label: 'Authentic', color: '#10b981' };
};

// --- Components ---
const GlassButton = ({ children, onClick, disabled, variant = 'primary', style = {} }) => {
  return (
    <button 
      onClick={onClick} 
      disabled={disabled}
      style={{ 
        padding: '10px 20px', 
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.18)',
        background: variant === 'danger' ? 'rgba(239, 68, 68, 0.8)' : (variant === 'secondary' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(59, 130, 246, 0.8)'),
        color: variant === 'secondary' ? 'var(--text-color)' : 'white',
        cursor: disabled ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontWeight: '600',
        transition: 'all 0.3s',
        opacity: disabled ? 0.5 : 1,
        ...style 
      }}
    >
      {children}
    </button>
  );
};

const ScoreCircle = ({ score, label, icon: Icon, size = 'md', isActive = true }) => {
  const statusInfo = getStatus(score, isActive);
  const sizes = {
    sm: { width: '120px', fontSize: '14px', iconSize: 24 },
    md: { width: '160px', fontSize: '18px', iconSize: 32 },
    lg: { width: '240px', fontSize: '28px', iconSize: 48 }
  };
  const currentSize = sizes[size] || sizes.md;
  const displayScore = statusInfo.label === 'N/A' ? 'N/A' : `${score}%`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div 
        style={{
          width: currentSize.width,
          height: currentSize.width,
          fontSize: currentSize.fontSize,
          background: isActive && score > 0
            ? `linear-gradient(135deg, ${statusInfo.color} 0%, ${statusInfo.color}dd 100%)` 
            : 'linear-gradient(135deg, #4b5563 0%, #6b7280 100%)', // Always grey gradient if not analyzed
          boxShadow: isActive && score > 0
            ? `0 20px 60px ${statusInfo.color}40` 
            : '0 20px 60px rgba(107, 114, 128, 0.2)',
          borderRadius: '50%',
          color: 'white',
          fontWeight: '700',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          marginBottom: '10px',
          opacity: isActive && score > 0 ? 1 : 0.6,
        }}
      >
        <Icon size={currentSize.iconSize} style={{ position: 'relative', zIndex: 1 }} />
        <div style={{ position: 'relative', zIndex: 1, marginTop: '8px' }}>
          {displayScore}
        </div>
      </div>
      <div style={{ fontSize: '16px', fontWeight: '600', color: statusInfo.color }}>
        {label} - {statusInfo.label}
      </div>
    </div>
  );
};

// --- Main Detector Component ---
const Detector = () => {
  const [uploadedFile, setUploadedFile] = useState(null); 
  // 📢 NEW STATE FOR OPTIONAL TEXT FILE
  const [optionalTextFile, setOptionalTextFile] = useState(null); 
  const [showOptionalInput, setShowOptionalInput] = useState(false); // Toggle visibility
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]); // Chat history for the current analysis

  // Drag & Drop Handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setUploadedFile(e.dataTransfer.files[0]);
      setAnalysisResult(null);
      setChatHistory([]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0]);
      setAnalysisResult(null);
      setChatHistory([]);
    }
  };

  const handleOptionalFileInput = (e) => {
      if (e.target.files && e.target.files[0]) {
          setOptionalTextFile(e.target.files[0]);
      }
  };

  // PDF Download (no change)
  const downloadPDF = () => {
    if (!analysisResult) return;
    const doc = new jsPDF();
    const statusInfo = getStatus(analysisResult.fusionScore, true);
    doc.setFontSize(20);
    doc.text('HCIS Analysis Report', 20, 30);
    doc.setFontSize(12);
    doc.text(`File: ${analysisResult.fileName}`, 20, 50);
    doc.text(`Size: ${formatFileSize(analysisResult.fileSize)}`, 20, 60);
    doc.text(`Date: ${new Date(analysisResult.timestamp).toLocaleString()}`, 20, 70);
    doc.setFontSize(16);
    doc.text('Analysis Results:', 20, 90);
    doc.setFontSize(12);
    doc.text(`Fusion Score: ${analysisResult.fusionScore}% (${statusInfo.label})`, 20, 105);
    doc.text(`Video Score: ${analysisResult.videoScore}%`, 20, 115);
    doc.text(`Audio Score: ${analysisResult.audioScore}%`, 20, 125);
    doc.text(`Text Score: ${analysisResult.textScore}%`, 20, 135);
    doc.setFontSize(16);
    doc.text('Explanation:', 20, 155);
    doc.setFontSize(12);
    const splitExplanation = doc.splitTextToSize(analysisResult.explanation, 170);
    doc.text(splitExplanation, 20, 165);
    doc.setFontSize(10);
    doc.setTextColor(150);
    doc.text('Generated by HCIS - Human-Computer Interaction System', 105, 280, { align: 'center' });
    doc.save(`HCIS_Report_${analysisResult.fileName.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}.pdf`);
  };

  // Analysis Handler
  const handleAnalyze = async () => {
    if (!uploadedFile) {
      alert("Please upload a primary media/text file before starting analysis.");
      return;
    }
    
    setIsAnalyzing(true);
    setProgress(0);
    setAnalysisResult(null); // Clear previous results
    setChatHistory([]); // Clear chat history for new analysis

    const formData = new FormData();
    // 1. PRIMARY FILE (Media or Text)
    formData.append('file', uploadedFile, uploadedFile.name);

    // 2. OPTIONAL TEXT FILE (If uploaded, send it under a separate key)
    if (optionalTextFile) {
        // 📢 CRITICAL: Key must match backend's expectation ('optional_text_file')
        formData.append('optional_text_file', optionalTextFile, optionalTextFile.name);
    }


    try {
      const response = await axios.post('/analyze', formData, {
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });

      const apiResults = response.data.results;
      
      // Map API results to frontend format
      const result = {
        fusionScore: parseFloat(apiResults.fusion_score || 0),
        videoScore: parseFloat(apiResults.video_score || 0),
        audioScore: parseFloat(apiResults.audio_score || 0),
        textScore: parseFloat(apiResults.text_score || 0),
        
        // 📢 Using score > 0 to determine if modality was active
        activeModalities: [
            ...(parseFloat(apiResults.video_score) > 0 ? ['video'] : []),
            ...(parseFloat(apiResults.audio_score) > 0 ? ['audio'] : []),
            ...(parseFloat(apiResults.text_score) > 0 ? ['text'] : []),
        ],
        explanation: apiResults.chatbot_explanation || 'No explanation available',
        fileName: apiResults.fileName || uploadedFile.name,
        fileSize: uploadedFile.size,
        timestamp: new Date().toISOString(),
        fullReport: apiResults
      };
      
      setAnalysisResult(result);
      addReportToHistory(result); 
      
      setChatHistory([{ role: 'assistant', content: apiResults.chatbot_explanation, isInitial: true }]);

    } catch (error) {
      console.error("Analysis API Error:", error.response?.data?.detail || error.message);
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Analysis failed due to a server error.';
      alert(`Analysis failed: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
      setProgress(100);
    }
  };

  // Chat Handler (no change, relies on backend fix)
  const handleChatSend = async () => {
    if (!chatInput.trim() || !analysisResult) return;
    
    const userMessage = chatInput.trim();
    setChatInput('');
    
    // Add user message to chat history
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage, timestamp: Date.now() }]);
    setChatHistory(prev => [...prev, { role: 'assistant', content: 'thinking...', isPlaceholder: true, timestamp: Date.now() + 1 }]);

    try {
      const response = await axios.post('/chat', {
        question: userMessage,
        context: analysisResult.fullReport 
      });

      const botResponse = response.data.response || 'No response from assistant.';
      
      // Replace placeholder with bot response
      setChatHistory(prev => {
          const newMessages = prev.filter(m => !m.isPlaceholder);
          return [...newMessages, { role: 'assistant', content: botResponse, timestamp: Date.now() + 2 }];
      });
      
    } catch (error) {
      console.error("Chat API Error:", error.response?.data?.detail || error.message);
      setChatHistory(prev => {
        const newMessages = prev.filter(m => !m.isPlaceholder);
        return [...newMessages, { role: 'assistant', content: 'Sorry, I encountered an error. Please check the backend log for details.', timestamp: Date.now() + 2 }];
      });
    }
  };

  const getProgressMessage = () => {
    if (progress < 30) return "Extracting and preprocessing data...";
    if (progress < 60) return "Running deepfake detection...";
    if (progress < 90) return "Aggregating multimodal results...";
    return "Generating summary report...";
  };

  const isModalityActive = (modality) => {
    return analysisResult?.activeModalities?.includes(modality);
  };
  
  // Render
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <h1 style={{ fontSize: '48px', fontWeight: '800', marginBottom: '16px', background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Multimedia Content Integrity Detector
        </h1>
        <p style={{ fontSize: '18px', opacity: 0.7 }}>
          Upload a Video, Audio, or Text file to analyze for deepfake and AI-generated content
        </p>
      </div>

      {!uploadedFile && (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`dropzone-area ${dragActive ? 'drag-active' : ''}`}
          onClick={() => document.getElementById('fileInput').click()}
          style={{
            border: '2px dashed rgba(255, 255, 255, 0.3)',
            borderRadius: '16px',
            padding: '60px 40px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s',
            background: dragActive ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255, 255, 255, 0.05)'
          }}
        >
          <Upload size={80} style={{ opacity: 0.5, marginBottom: '24px' }} />
          <p style={{ fontSize: '28px', fontWeight: '600', marginBottom: '8px' }}>
            {dragActive ? 'Drop Primary File Here' : 'Drag & Drop Primary File (Media/Text)'}
          </p>
          <p style={{ opacity: 0.6, fontSize: '16px' }}>
            or click to select a file (MP4, MP3, TXT, etc.)
          </p>
          <input
            id="fileInput"
            type="file"
            style={{ display: 'none' }}
            onChange={handleFileInput}
            accept="video/*,audio/*,text/plain"
          />
        </div>
      )}

      {uploadedFile && !analysisResult && !isAnalyzing && (
        <div className="analysis-result-card" style={{ padding: '30px' }}>
          <h3 style={{ marginBottom: '24px', fontSize: '20px' }}>Files Ready for Analysis</h3>

          {/* --- Primary File Display --- */}
          <div style={{ paddingBottom: '15px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', marginBottom: '15px' }}>
              <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileVideo size={20} /> Primary File: {uploadedFile.name}
              </p>
              <p style={{ opacity: 0.6, fontSize: '14px' }}>
                Size: {formatFileSize(uploadedFile.size)}
              </p>
              <GlassButton 
                  onClick={() => { setUploadedFile(null); setOptionalTextFile(null); setShowOptionalInput(false); }} 
                  variant="danger" 
                  style={{ padding: '5px 10px', fontSize: '12px', marginTop: '10px' }}
              >
                <X size={16} /> Reset Primary File
              </GlassButton>
          </div>

          {/* --- Optional Text File Input/Display --- */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '30px' }}>
              
              {/* Toggle Button */}
              <GlassButton 
                  onClick={() => {
                      setShowOptionalInput(prev => !prev);
                      if (showOptionalInput) setOptionalTextFile(null); // Clear file if hiding input
                  }}
                  variant="secondary"
                  style={{ justifyContent: 'start', opacity: 0.9, color: 'var(--text-color)', border: '1px solid rgba(255, 255, 255, 0.2)' }}
              >
                  {showOptionalInput ? <Minus size={20} /> : <Plus size={20} />} 
                  {showOptionalInput ? 'Remove Optional Text Script' : 'Add Optional Text Script/Context (.txt)'}
              </GlassButton>

              {/* Input Area */}
              {showOptionalInput && (
                  <div style={{ 
                      padding: '15px', 
                      border: '1px solid rgba(255, 255, 255, 0.1)', 
                      borderRadius: '8px', 
                      background: 'rgba(59, 130, 246, 0.05)',
                      display: 'flex',
                      flexDirection: 'column'
                  }}>
                      <label style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px', opacity: 0.7 }}>
                          Text File: {optionalTextFile ? optionalTextFile.name : 'No file selected'}
                      </label>
                      <input
                          id="optionalFileInput"
                          type="file"
                          style={{ width: '100%', padding: '5px 0', border: 'none', background: 'transparent', color: 'var(--text-color)', marginBottom: '10px' }}
                          onChange={handleOptionalFileInput}
                          accept=".txt"
                      />
                      {optionalTextFile && (
                          <GlassButton 
                              onClick={() => setOptionalTextFile(null)} 
                              variant="danger" 
                              style={{ padding: '5px 10px', fontSize: '12px', justifyContent: 'center' }}
                          >
                            <X size={16} /> Clear Text File
                          </GlassButton>
                      )}
                  </div>
              )}
          </div>
          {/* --- Analysis Actions --- */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <GlassButton onClick={handleAnalyze} disabled={isAnalyzing} variant="primary" style={{ padding: '15px 30px', fontSize: '18px' }}>
              <Camera size={20} /> Analyze Unified Report
            </GlassButton>
          </div>
        </div>
      )}

      {isAnalyzing && (
        <div className="analysis-result-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '24px' }}>⚡</div>
          <h3 style={{ marginBottom: '16px', fontSize: '24px' }}>Analyzing Content...</h3>
          <p style={{ opacity: 0.7, marginBottom: '32px' }}>
            {getProgressMessage()}
          </p>
          <div style={{
            width: '100%',
            height: '8px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: progress + '%',
              height: '100%',
              background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
              transition: 'width 0.3s ease',
              borderRadius: '4px'
            }} />
          </div>
          <p style={{ marginTop: '16px', opacity: 0.6 }}>{progress}%</p>
        </div>
      )}

      {analysisResult && !isAnalyzing && (
        <div className="analysis-result-card">
          <h2 style={{ marginBottom: '40px', textAlign: 'center', fontSize: '32px' }}>
            Analysis Complete
          </h2>

          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '60px' }}>
            <ScoreCircle 
              score={analysisResult.fusionScore} 
              label="Fusion Score" 
              icon={Sparkles} 
              size="lg" 
              isActive={true}
            />
          </div>

          <h3 style={{ marginBottom: '32px', textAlign: 'center', fontSize: '24px', opacity: 0.8 }}>
            Component Analysis
          </h3>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '48px', marginBottom: '40px', flexWrap: 'wrap' }}>
            <ScoreCircle 
              score={analysisResult.videoScore} 
              label="Video" 
              icon={FileVideo} 
              size="md" 
              isActive={analysisResult.videoScore > 0}
            />
            <ScoreCircle 
              score={analysisResult.audioScore} 
              label="Audio" 
              icon={FileAudio} 
              size="md" 
              isActive={analysisResult.audioScore > 0}
            />
            <ScoreCircle 
              score={analysisResult.textScore} 
              label="Text" 
              icon={FileText} 
              size="md" 
              isActive={analysisResult.textScore > 0}
            />
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '24px',
            borderRadius: '16px',
            marginBottom: '32px'
          }}>
            <h4 style={{ marginBottom: '12px', fontSize: '18px' }}>AI Analysis Explanation</h4>
            <p style={{ opacity: 0.8, lineHeight: '1.6', whiteSpace: 'pre-wrap' }} dangerouslySetInnerHTML={{ __html: analysisResult.explanation }} />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '40px' }}>
            <GlassButton onClick={downloadPDF}>
              <Download size={20} /> Download Report
            </GlassButton>
            <GlassButton onClick={() => { 
              setUploadedFile(null); 
              setAnalysisResult(null); 
              setChatHistory([]);
            }} variant="secondary">
              Analyze Another File
            </GlassButton>
          </div>

          {/* Chat Interface */}
          <div style={{ padding: '20px 0', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <h4 style={{ marginBottom: '15px', fontSize: '18px' }}>Continue Conversation:</h4>
            
            {/* Chat History */}
            {chatHistory.length > 0 && (
              <div style={{ 
                maxHeight: '300px', 
                overflowY: 'auto', 
                marginBottom: '15px',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '8px',
                padding: '15px'
              }}>
                {chatHistory.map((msg, idx) => (
                  <div key={idx} style={{ 
                    marginBottom: '15px',
                    padding: '10px',
                    background: msg.role === 'user' ? 'rgba(59, 130, 246, 0.2)' : (msg.isPlaceholder ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.1)'),
                    borderRadius: '8px',
                    borderLeft: `3px solid ${msg.role === 'user' ? '#3b82f6' : '#8b5cf6'}`
                  }}>
                    <div style={{ fontWeight: '600', marginBottom: '5px', fontSize: '12px', opacity: 0.7 }}>
                      {msg.role === 'user' ? 'You' : 'AI Assistant'}
                    </div>
                    <div style={{ whiteSpace: 'pre-wrap' }}>
                        {msg.isPlaceholder ? 'AI Assistant is typing...' : msg.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Chat Input */}
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Ask about the analysis results..."
                style={{ 
                    flexGrow: 1, 
                    padding: '12px', 
                    borderRadius: '8px', 
                    border: '1px solid rgba(255, 255, 255, 0.2)', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    color: 'inherit' 
                }}
              />
              <GlassButton onClick={handleChatSend} style={{ padding: '12px 18px' }} variant="primary">
                <Send size={20} /> Ask
              </GlassButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Detector;
