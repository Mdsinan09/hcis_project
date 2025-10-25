import React, { useState } from 'react';
import { Sparkles, Download, FileVideo, Type, X, Image } from 'lucide-react';
import axios from '../utils/axios';

const GlassButton = ({ children, onClick, disabled, variant = 'primary', style = {} }) => {
  return (
    <button 
      onClick={onClick} 
      disabled={disabled}
      style={{ 
        padding: '12px 24px', 
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.18)',
        background: variant === 'secondary' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(59, 130, 246, 0.8)',
        color: variant === 'secondary' ? 'var(--text-color)' : 'white',
        cursor: disabled ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        fontWeight: '600',
        transition: 'all 0.3s',
        opacity: disabled ? 0.5 : 1,
        width: '100%',
        ...style 
      }}
    >
      {children}
    </button>
  );
};

const Generator = () => {
  const [type, setType] = useState('voice-clone');
  const [file, setFile] = useState(null);
  const [file2, setFile2] = useState(null);
  const [text, setText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedUrl, setGeneratedUrl] = useState('');
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  
  const resetForm = () => {
    setFile(null);
    setFile2(null);
    setText('');
    setGeneratedUrl('');
    setError(null);
    setProgress(0);
  };
  
  const generateVoiceClone = async () => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_text', text);
    
    const response = await axios.post('/generate/voice', formData, {
      onUploadProgress: (e) => setProgress(Math.round((e.loaded * 100) / e.total))
    });
    
    return response.data;
  };
  
  const generateFaceSwap = async () => {
    const formData = new FormData();
    formData.append('source_video', file);
    formData.append('target_video', file2);
    
    const response = await axios.post('/generate/faceswap', formData, {
      onUploadProgress: (e) => setProgress(Math.round((e.loaded * 100) / e.total))
    });
    
    return response.data;
  };
  
  const handleGenerate = async () => {
    if (!isFormValid()) {
      alert("Please ensure all necessary inputs are provided.");
      return;
    }
    
    setIsGenerating(true);
    setGeneratedUrl('');
    setError(null);
    setProgress(0);
    
    try {
      let result;
      
      if (type === 'voice-clone') {
        result = await generateVoiceClone();
      } else if (type === 'face-swap') {
        result = await generateFaceSwap();
      }
      
      if (result && result.generated_path) {
        // Get base URL without /api suffix
        const baseUrl = axios.defaults.baseURL.replace('/api', '') || 'http://localhost:8000';
        const fullUrl = baseUrl + result.generated_path;
        
        console.log('✅ Generated file URL:', fullUrl);
        setGeneratedUrl(fullUrl);
      } else {
        throw new Error(result?.error || 'Backend failed to return a file path.');
      }
          
    } catch (err) {
      console.error("Generation Error:", err);
      const errorMessage = err.response?.data?.error || err.message || 'Generation failed';
      setError(errorMessage);
      alert('Error: ' + errorMessage);
    } finally {
      setIsGenerating(false);
      setProgress(100);
    }
  };
  
  const getButtonText = () => {
    if (isGenerating) {
      if (type === 'voice-clone') return 'Synthesizing Voice...';
      if (type === 'face-swap') return 'Swapping Faces...';
    }
    if (type === 'voice-clone') return 'Generate Voice Clone';
    if (type === 'face-swap') return 'Generate Face Swap';
  };
  
  const isFormValid = () => {
    if (type === 'voice-clone') return file && text.trim();
    if (type === 'face-swap') return file && file2;
    return false;
  };
  
  const getMediaType = (url) => {
    if (!url) return null;
    const extension = url.split('.').pop().split('?')[0].toLowerCase();
    if (['mp4', 'mov', 'avi'].includes(extension)) return 'video';
    if (['mp3', 'wav'].includes(extension)) return 'audio';
    return null;
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ 
          fontSize: '48px', 
          fontWeight: '800', 
          marginBottom: '16px', 
          background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', 
          WebkitBackgroundClip: 'text', 
          WebkitTextFillColor: 'transparent' 
        }}>
          🎭 Deepfake Generator
        </h1>
        <p style={{ fontSize: '18px', opacity: 0.7 }}>
          Generate synthetic media for educational and research purposes
        </p>
      </div>
      
      <div style={{ 
        padding: '30px', 
        borderRadius: '20px', 
        background: 'rgba(255,255,255,0.05)', 
        boxShadow: '0 4px 30px rgba(0,0,0,0.1)', 
        marginBottom: '20px',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        
        {/* Generation Type Selector */}
        <div style={{ marginBottom: '30px' }}>
          <label style={{ 
            fontSize: '16px', 
            fontWeight: '600', 
            display: 'block', 
            marginBottom: '12px', 
            opacity: 0.9 
          }}>
            Generation Type
          </label>
          <select 
            value={type} 
            onChange={(e) => { setType(e.target.value); resetForm(); }}
            style={{ 
              width: '100%', 
              padding: '12px', 
              borderRadius: '8px', 
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(255,255,255,0.05)', 
              color: 'inherit',
              fontSize: '16px',
              cursor: 'pointer'
            }}
          >
            <option value="voice-clone">🎙️ Voice Clone (Video/Audio + Text → New Audio)</option>
            <option value="face-swap">🎭 Face Swap (2 Videos → Swapped Faces)</option>
          </select>
        </div>
        
        {/* Voice Clone Interface */}
        {type === 'voice-clone' && (
          <>
            <div style={{ marginBottom: '25px' }}>
              <label style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                display: 'block', 
                marginBottom: '8px', 
                opacity: 0.9 
              }}>
                <FileVideo size={18} style={{ verticalAlign: 'middle', marginRight: '5px' }} /> 
                Upload Video or Audio File
              </label>
              <input 
                type="file" 
                accept="video/*,audio/*" 
                onChange={(e) => setFile(e.target.files[0])} 
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  background: 'rgba(255,255,255,0.05)', 
                  border: '1px solid rgba(255,255,255,0.2)', 
                  borderRadius: '8px', 
                  color: 'inherit',
                  cursor: 'pointer'
                }}
              />
              {file && <p style={{ opacity: 0.7, marginTop: '8px', fontSize: '14px' }}>📎 {file.name}</p>}
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                display: 'block', 
                marginBottom: '8px', 
                opacity: 0.9 
              }}>
                <Type size={18} style={{ verticalAlign: 'middle', marginRight: '5px' }} /> 
                Target Text Script
              </label>
              <textarea 
                value={text} 
                onChange={(e) => setText(e.target.value)} 
                placeholder="Enter the text you want the synthesized voice to say..."
                rows={5}
                style={{ 
                  width: '100%', 
                  padding: '15px', 
                  borderRadius: '8px', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.05)', 
                  color: 'inherit', 
                  resize: 'vertical',
                  fontSize: '15px',
                  lineHeight: '1.5'
                }}
              />
            </div>
          </>
        )}
        
        {/* Face Swap Interface */}
        {type === 'face-swap' && (
          <>
            <div style={{ marginBottom: '25px' }}>
              <label style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                display: 'block', 
                marginBottom: '8px', 
                opacity: 0.9 
              }}>
                <Image size={18} style={{ verticalAlign: 'middle', marginRight: '5px' }} /> 
                Source Video (Face to Extract)
              </label>
              <input 
                type="file" 
                accept="video/*" 
                onChange={(e) => setFile(e.target.files[0])} 
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  background: 'rgba(255,255,255,0.05)', 
                  border: '1px solid rgba(255,255,255,0.2)', 
                  borderRadius: '8px', 
                  color: 'inherit',
                  cursor: 'pointer'
                }}
              />
              {file && <p style={{ opacity: 0.7, marginTop: '8px', fontSize: '14px' }}>📎 {file.name}</p>}
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                display: 'block', 
                marginBottom: '8px', 
                opacity: 0.9 
              }}>
                <FileVideo size={18} style={{ verticalAlign: 'middle', marginRight: '5px' }} /> 
                Target Video (Face to Replace)
              </label>
              <input 
                type="file" 
                accept="video/*" 
                onChange={(e) => setFile2(e.target.files[0])} 
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  background: 'rgba(255,255,255,0.05)', 
                  border: '1px solid rgba(255,255,255,0.2)', 
                  borderRadius: '8px', 
                  color: 'inherit',
                  cursor: 'pointer'
                }}
              />
              {file2 && <p style={{ opacity: 0.7, marginTop: '8px', fontSize: '14px' }}>📎 {file2.name}</p>}
            </div>
          </>
        )}
        
        {/* Progress Bar */}
        {isGenerating && (
          <div style={{ marginBottom: '25px' }}>
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
            <p style={{ textAlign: 'center', marginTop: '8px', opacity: 0.7, fontSize: '14px' }}>
              {progress}%
            </p>
          </div>
        )}
        
        {/* Generate Button */}
        <GlassButton 
          onClick={handleGenerate} 
          disabled={!isFormValid() || isGenerating}
        >
          <Sparkles size={20} />
          {getButtonText()}
        </GlassButton>
        
        {/* Error Display */}
        {error && (
          <div style={{ 
            color: '#ef4444', 
            padding: '15px', 
            border: '1px solid #ef4444', 
            borderRadius: '12px', 
            marginTop: '20px',
            background: 'rgba(239, 68, 68, 0.1)'
          }}>
            <strong>Generation Error:</strong> {error}
          </div>
        )}
        
        {/* Results/Download Area */}
        {generatedUrl && (
          <div style={{ 
            textAlign: 'center', 
            marginTop: '30px', 
            padding: '20px',
            background: 'rgba(16, 185, 129, 0.1)',
            borderRadius: '12px',
            border: '1px solid rgba(16, 185, 129, 0.3)'
          }}>
            <p style={{ marginBottom: '15px', fontWeight: '600', fontSize: '18px' }}>
              ✨ Generation Complete!
            </p>
                        
            {/* Media Preview */}
            {getMediaType(generatedUrl) === 'audio' && (
              <audio controls src={generatedUrl} style={{ width: '100%', marginBottom: '15px' }} />
            )}
            {getMediaType(generatedUrl) === 'video' && (
              <video controls src={generatedUrl} style={{ width: '100%', maxHeight: '400px', marginBottom: '15px', borderRadius: '8px' }} />
            )}
                        
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <a 
                href={generatedUrl} 
                download={`${type}_${Date.now()}.${getMediaType(generatedUrl) === 'audio' ? 'mp3' : 'mp4'}`} 
                style={{ textDecoration: 'none', flex: '1', minWidth: '200px' }}
              >
                <GlassButton style={{ background: 'rgba(16, 185, 129, 0.8)' }}>
                  <Download size={20} /> Download Generated File
                </GlassButton>
              </a>
                            
              <GlassButton 
                onClick={resetForm} 
                variant="secondary"
                style={{ flex: '1', minWidth: '200px' }}
              >
                <X size={20} /> Generate Another
              </GlassButton>
            </div>
          </div>
        )}
      </div>
            
      <div style={{ 
        textAlign: 'center', 
        padding: '20px',
        background: 'rgba(239, 68, 68, 0.1)',
        borderRadius: '12px',
        border: '1px solid rgba(239, 68, 68, 0.3)'
      }}>
        <p style={{ fontSize: '14px', opacity: 0.9, marginBottom: '8px' }}>
          ⚠️ <strong>Educational Use Only</strong>
        </p>
        <p style={{ fontSize: '12px', opacity: 0.7 }}>
          Generated content is for testing HCIS detection capabilities. Do not use for malicious purposes.
        </p>
      </div>
    </div>
  );
};

export default Generator;