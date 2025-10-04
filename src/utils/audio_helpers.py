import librosa
import numpy as np
import subprocess
import os
from scipy import signal
from scipy.stats import kurtosis, skew


def extract_audio_from_video(video_path, output_audio_path=None):
    """
    Extract audio track from video file
    
    Args:
        video_path: Path to video file
        output_audio_path: Where to save extracted audio (optional)
        
    Returns:
        Path to extracted audio file
    """
    try:
        if output_audio_path is None:
            # Create temp audio file name
            base_name = os.path.splitext(video_path)[0]
            output_audio_path = base_name + "_audio.wav"
        
        # Use ffmpeg to extract audio (needs ffmpeg installed)
        # Alternative: use moviepy if ffmpeg not available
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # Audio codec
                '-ar', '22050',  # Sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                output_audio_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Audio extracted to: {output_audio_path}")
            return output_audio_path
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: use moviepy if ffmpeg not available
            print("⚠️  ffmpeg not found, trying moviepy...")
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(output_audio_path, fps=22050)
            video.close()
            print(f"✅ Audio extracted to: {output_audio_path}")
            return output_audio_path
            
    except Exception as e:
        print(f"❌ Error extracting audio: {str(e)}")
        return None


def load_audio(audio_path, sr=22050, duration=None):
    """
    Load audio file using Librosa
    
    Args:
        audio_path: Path to audio file
        sr: Sample rate (default 22050 Hz)
        duration: Max duration to load (seconds)
        
    Returns:
        Audio time series and sample rate
    """
    try:
        y, sr = librosa.load(audio_path, sr=sr, duration=duration)
        print(f"✅ Loaded audio: {len(y)} samples at {sr} Hz")
        return y, sr
        
    except Exception as e:
        print(f"❌ Error loading audio: {str(e)}")
        return None, None


def extract_mfcc_features(y, sr, n_mfcc=13):
    """
    Extract MFCC (Mel-frequency cepstral coefficients) features
    These are the "fingerprint" of a voice
    
    Args:
        y: Audio time series
        sr: Sample rate
        n_mfcc: Number of MFCC coefficients
        
    Returns:
        Dictionary of MFCC statistics
    """
    try:
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        
        # Calculate statistics
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        mfcc_max = np.max(mfccs, axis=1)
        mfcc_min = np.min(mfccs, axis=1)
        
        return {
            'mfcc_mean': mfcc_mean,
            'mfcc_std': mfcc_std,
            'mfcc_max': mfcc_max,
            'mfcc_min': mfcc_min,
            'mfcc_range': mfcc_max - mfcc_min
        }
        
    except Exception as e:
        print(f"❌ Error extracting MFCC: {str(e)}")
        return None


def extract_spectral_features(y, sr):
    """
    Extract spectral features from audio
    
    Args:
        y: Audio time series
        sr: Sample rate
        
    Returns:
        Dictionary of spectral features
    """
    try:
        # Spectral centroid (brightness of sound)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        # Spectral rolloff (frequency below which 85% of energy is)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        
        # Zero crossing rate (sign changes in signal)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # Chroma features (pitch class)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        return {
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'spectral_centroid_std': np.std(spectral_centroids),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
            'zero_crossing_rate_mean': np.mean(zero_crossing_rate),
            'chroma_mean': np.mean(chroma, axis=1)
        }
        
    except Exception as e:
        print(f"❌ Error extracting spectral features: {str(e)}")
        return None


def calculate_audio_quality(y, sr):
    """
    Calculate audio quality metrics
    
    Args:
        y: Audio time series
        sr: Sample rate
        
    Returns:
        Dictionary with quality metrics
    """
    try:
        # RMS energy (loudness)
        rms = librosa.feature.rms(y=y)[0]
        
        # Signal-to-noise ratio estimate
        # High variance in RMS = good dynamic range
        dynamic_range = np.std(rms) / (np.mean(rms) + 1e-6)
        
        # Pitch/frequency analysis
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Count of voiced frames (frames with clear pitch)
        voiced_frames = np.sum(magnitudes > np.median(magnitudes))
        total_frames = magnitudes.shape[1]
        voiced_ratio = voiced_frames / total_frames
        
        # Statistical properties
        audio_kurtosis = kurtosis(y)
        audio_skew = skew(y)
        
        # Overall quality score (0-1)
        quality_score = (
            min(dynamic_range, 1.0) * 0.3 +
            voiced_ratio * 0.4 +
            min(abs(audio_kurtosis) / 10, 1.0) * 0.3
        )
        
        return {
            'rms_mean': np.mean(rms),
            'rms_std': np.std(rms),
            'dynamic_range': dynamic_range,
            'voiced_ratio': voiced_ratio,
            'kurtosis': audio_kurtosis,
            'skewness': audio_skew,
            'overall_quality': quality_score
        }
        
    except Exception as e:
        print(f"❌ Error calculating audio quality: {str(e)}")
        return None


def detect_audio_artifacts(y, sr):
    """
    Detect audio manipulation artifacts
    
    Args:
        y: Audio time series
        sr: Sample rate
        
    Returns:
        Artifact score (0-1, higher = more suspicious)
    """
    try:
        artifact_score = 0
        
        # 1. Check for unnatural frequency patterns
        spec = np.abs(librosa.stft(y))
        freq_variance = np.var(spec, axis=1)
        
        # Very uniform frequency distribution = suspicious
        if np.std(freq_variance) < 0.1:
            artifact_score += 0.2
        
        # 2. Check for audio splicing (sudden changes)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        sudden_changes = np.sum(onset_env > np.percentile(onset_env, 95))
        
        if sudden_changes > len(onset_env) * 0.1:  # More than 10% sudden changes
            artifact_score += 0.3
        
        # 3. Check for unnatural silence patterns
        rms = librosa.feature.rms(y=y)[0]
        silence_ratio = np.sum(rms < 0.01) / len(rms)
        
        if silence_ratio > 0.3 or silence_ratio < 0.01:  # Too much or too little silence
            artifact_score += 0.2
        
        # 4. Check for clipping (over-amplification)
        clipping_ratio = np.sum(np.abs(y) > 0.99) / len(y)
        
        if clipping_ratio > 0.01:
            artifact_score += 0.3
        
        return min(artifact_score, 1.0)
        
    except Exception as e:
        print(f"❌ Error detecting artifacts: {str(e)}")
        return 0.5  # Neutral score on error