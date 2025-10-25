import React, { useState, useEffect, useMemo } from 'react';
import { getHistory, deleteReport } from '../utils/history';
import { Trash2, Download, ArrowLeft, Sparkles, FileVideo, FileAudio, FileText } from 'lucide-react';

// --- Helper Functions ---
const getStatus = (value) => {
  const score = parseFloat(value);
  // Ensure we handle non-numeric or zero scores gracefully for the UI
  if (isNaN(score) || score === null || score === 0) {
      return { label: 'N/A', color: '#6b7280' };
  }
  if (score < 40) return { label: 'Fabricated', color: '#ef4444' };
  if (score < 70) return { label: 'Suspicious', color: '#f59e0b' };
  return { label: 'Authentic', color: '#10b981' };
};

// 📢 Dummy GlassButton placeholder for correct component rendering
const GlassButton = ({ children, onClick, disabled, variant = 'primary', style = {} }) => {
    return (
        <button 
            onClick={onClick} 
            disabled={disabled}
            style={{ 
                padding: '10px 20px', 
                borderRadius: '16px',
                border: '1px solid rgba(255, 255, 255, 0.18)',
                background: variant === 'danger' ? '#ef4444' : (variant === 'secondary' ? 'rgba(255, 255, 255, 0.1)' : '#3b82f6'),
                color: variant === 'secondary' ? 'var(--text-color)' : 'white',
                cursor: disabled ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                ...style 
            }}
        >
            {children}
        </button>
    );
};

// --- ScoreCircle Component ---
const ScoreCircle = ({ score, label, icon: Icon, size = 'md' }) => {
  const statusInfo = getStatus(score);
  const sizes = {
    sm: { width: '120px', fontSize: '14px', iconSize: 24 },
    md: { width: '160px', fontSize: '18px', iconSize: 32 },
    lg: { width: '240px', fontSize: '28px', iconSize: 48 }
  };
  const currentSize = sizes[size] || sizes.md;
  
  // Display logic
  const displayScore = statusInfo.label === 'N/A' ? 'N/A' : `${score}%`;
  const isActive = statusInfo.label !== 'N/A';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div 
        className="score-circle-inner"
        style={{
          width: currentSize.width,
          height: currentSize.width,
          fontSize: currentSize.fontSize,
          // Use statusInfo.color for background
          background: isActive
            ? `linear-gradient(135deg, ${statusInfo.color} 0%, ${statusInfo.color}dd 100%)`
            : 'linear-gradient(135deg, #4b5563 0%, #6b7280 100%)',
          boxShadow: isActive ? `0 20px 60px ${statusInfo.color}40` : '0 20px 60px rgba(107, 114, 128, 0.2)',
          borderRadius: '50%',
          color: 'white',
          fontWeight: '700',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          marginBottom: '10px',
          opacity: isActive ? 1 : 0.6,
        }}
      >
        <Icon size={currentSize.iconSize} style={{ position: 'relative', zIndex: 1 }} />
        <div style={{ position: 'relative', zIndex: 1, marginTop: '8px' }}>{displayScore}</div>
      </div>
      <div style={{ fontSize: '16px', fontWeight: '600', color: statusInfo.color }}>
        {label} - {statusInfo.label}
      </div>
    </div>
  );
};

const History = () => {
  const [historyList, setHistoryList] = useState([]);
  const [selectedReportId, setSelectedReportId] = useState(null);

  // Load history from the utility file
  useEffect(() => { loadHistory(); }, []);

  const loadHistory = async () => {
    const data = await getHistory(); 
    setHistoryList(data);
  };

  const selectedReport = useMemo(() => {
    if (!selectedReportId) return null;
    // CRITICAL FIX: Find the report from the state list
    return historyList.find(report => report.id === selectedReportId); 
  }, [selectedReportId, historyList]);

  // Handles deletion and refreshes the list
  const handleDelete = async (id, e) => {
    if (e) e.stopPropagation(); 
    if (!window.confirm('Are you sure you want to permanently delete this report?')) return;
    
    await deleteReport(id);
    setSelectedReportId(null); 
    loadHistory(); 
  };

  // 📢 CRITICAL FIX: Restructure data passed to pdfGenerator to use camelCase keys
  const handleDownloadPDF = async (report, e) => {
    if (e) e.stopPropagation();

    const dataForPDF = {
        fusionScore: report.fusion_score || 0,
        videoScore: report.video_score || 0,
        audioScore: report.audio_score || 0,
        textScore: report.text_score || 0,
        explanation: report.chatbot_explanation || 'No explanation available.',
        fileName: report.fileName || 'report.pdf',
        timestamp: report.timestamp,
        // fileSize is needed by the original pdfGenerator logic but is not stored in history, 
        // passing a placeholder of 0 here to prevent crashes, but this needs to be fixed 
        // if the original PDF logic is in a separate file. 
        // For robustness, assuming the PDF generator only needs the scores and text.
    };

    try {
      // Assuming pdfGenerator exports a function that accepts this camelCase structure
      const { generatePDF } = await import('../utils/pdfGenerator'); 
      generatePDF(dataForPDF);
    } catch (error) {
      console.error("PDF Generation Error:", error);
      alert("Failed to generate PDF. Check the browser console for details.");
    }
  };


  const renderReportDetail = (report) => {
    // 📢 CRITICAL FIX: Map snake_case API keys to camelCase local variables
    const fusionScore = report.fusion_score || 0;
    const videoScore = report.video_score || 0;
    const audioScore = report.audio_score || 0;
    const textScore = report.text_score || 0;
    
    const { fileName, timestamp, chatbot_explanation } = report;

    const { color: fusionColor } = getStatus(fusionScore);
    
    return (
      <div className="analysis-result-card" style={{ padding: '40px', background: 'var(--card-background)', borderRadius: '16px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)' }}>
        
        <GlassButton variant="secondary" onClick={() => setSelectedReportId(null)} style={{ marginBottom: '30px', color: 'var(--text-color)' }}>
          <ArrowLeft size={20} /> Back to History
        </GlassButton>

        <h1 style={{ textAlign: 'center', marginBottom: '10px', color: fusionColor, fontSize: '2rem' }}>{fileName}</h1>
        <p style={{ textAlign: 'center', color: 'var(--text-color)', opacity: 0.7, marginBottom: '30px' }}>
          Analyzed on: {new Date(timestamp).toLocaleString()}
        </p>
        <hr style={{ borderColor: fusionColor, opacity: 0.3, marginBottom: '50px' }} />

        {/* --- Fusion Result --- */}
        <h2 style={{ textAlign: 'center', fontSize: '1.8rem', marginBottom: '30px', color: 'var(--text-color)' }}>Overall Content Integrity</h2>
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '60px' }}>
          <ScoreCircle score={fusionScore} label="Fusion Score" icon={Sparkles} size="lg" />
        </div>

        {/* --- Component Scores --- */}
        <h2 style={{ textAlign: 'center', fontSize: '1.5rem', marginBottom: '30px', color: 'var(--text-color)' }}>Component Analysis</h2>
        <div style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '40px', marginBottom: '50px', flexWrap: 'wrap' }}>
          {/* Only render if score is present, use score > 0 logic for isActive */}
          <ScoreCircle score={videoScore} label="Video" icon={FileVideo} size="md" isActive={videoScore > 0} />
          <ScoreCircle score={audioScore} label="Audio" icon={FileAudio} size="md" isActive={audioScore > 0} />
          <ScoreCircle score={textScore} label="Text" icon={FileText} size="md" isActive={textScore > 0} />
        </div>
        
        {/* --- Diagnostic Summary --- */}
        <h2 style={{ fontSize: '1.5rem', marginTop: '40px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '10px', marginBottom: '20px', color: 'var(--text-color)' }}>Diagnostic Summary</h2>
        <div style={{ padding: '20px', background: 'var(--background-light)', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.1)', marginBottom: '30px' }}>
          <p style={{ color: 'var(--text-color)', lineHeight: '1.6' }} dangerouslySetInnerHTML={{ __html: `🤖: ${chatbot_explanation || 'No explanation available from AI assistant.'}` }}/>
        </div>

        {/* --- Actions --- */}
        <div style={{ textAlign: 'center', marginBottom: '20px', display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <GlassButton variant="primary" onClick={() => handleDownloadPDF(report)} style={{ padding: '15px 30px', fontSize: '16px' }}>
            <Download size={20} /> Download Report
          </GlassButton>
          <GlassButton variant="danger" onClick={(e) => handleDelete(report.id, e)} style={{ padding: '15px 30px', fontSize: '16px' }}>
            <Trash2 size={20} /> Delete Report
          </GlassButton>
        </div>
      </div>
    );
  };

  const renderHistoryList = () => {
    if (historyList.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '50px', background: 'var(--card-background)', borderRadius: '16px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)' }}>
          <h2 style={{ color: 'var(--primary-color)' }}>No Analysis History Found</h2>
          <p style={{ color: 'var(--text-color)' }}>Upload a file in the Detector page to save your first report!</p>
        </div>
      );
    }

    return (
      <div style={{ paddingBottom: '50px' }}>
        {historyList.map(report => {
          // 📢 CRITICAL FIX: Use snake_case key from API response
          const score = report.fusion_score || 0; 
          const { label: statusLabel, color } = getStatus(score);
          
          return (
            <div 
              key={report.id} 
              style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                padding: '15px 25px', 
                margin: '15px 0', 
                borderRadius: '12px',
                background: 'var(--card-background)',
                borderLeft: `5px solid ${color}`,
                boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                transition: 'transform 0.2s',
                cursor: 'pointer'
              }}
              onClick={() => setSelectedReportId(report.id)}
            >
              <div style={{ flexGrow: 1 }}>
                <p style={{ fontWeight: '600', margin: '0', fontSize: '1.1rem', color: color }}>
                  {report.fileName}
                </p>
                <small style={{ color: 'var(--text-color)', opacity: 0.8 }}>
                  {new Date(report.timestamp).toLocaleString()} | Score: {score > 0 ? `${score}%` : 'N/A'} | Status: {statusLabel}
                </small>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <GlassButton variant="secondary" onClick={(e) => handleDownloadPDF(report, e)} style={{ padding: '8px 16px', fontSize: '14px', color: 'var(--text-color)' }}>
                  <Download size={16} />
                </GlassButton>
                <GlassButton variant="danger" onClick={(e) => handleDelete(report.id, e)} style={{ padding: '8px 16px', fontSize: '14px' }}>
                  <Trash2 size={16} />
                </GlassButton>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '10px', background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        📊 HCIS — Analysis History
      </h1>
      <p style={{ textAlign: 'center', color: 'var(--text-color)', opacity: 0.7, marginBottom: '40px' }}>
        {selectedReportId ? 'Detailed Diagnostic Report' : 'Review past analyses and download full reports.'}
      </p>

      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {selectedReport ? renderReportDetail(selectedReport) : renderHistoryList()}
      </div>
    </div>
  );
};

export default History;
