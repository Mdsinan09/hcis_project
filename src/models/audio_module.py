import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.audio_helpers import (
    extract_audio_from_video,
    load_audio,
    extract_mfcc_features,
    extract_spectral_features,
    calculate_audio_quality,
    detect_audio_artifacts
)


class AudioDeepfakeDetector:
    """
    Main class for audio deepfake detection
    """
    
    def __init__(self, sr=22050):
        self.sr = sr  # Sample rate
        print("✅ Audio Deepfake Detector initialized")
    
    def analyze_voice_naturalness(self, y, sr):
        """
        Analyze if voice sounds natural vs synthetic
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Naturalness score (0-1, higher = more natural)
        """
        try:
            # Extract MFCC features
            mfcc_features = extract_mfcc_features(y, sr)
            
            if mfcc_features is None:
                return 0.5
            
            # Analyze MFCC patterns
            # Natural voices have specific MFCC characteristics
            mfcc_variance = np.var(mfcc_features['mfcc_std'])
            mfcc_range_avg = np.mean(mfcc_features['mfcc_range'])
            
            # Natural voice typically has:
            # - Moderate variance in MFCCs
            # - Good range of values
            naturalness_score = 0
            
            # Check MFCC variance (natural: 0.5-2.0)
            if 0.5 < mfcc_variance < 2.0:
                naturalness_score += 0.5
            else:
                # Penalize if too uniform or too chaotic
                naturalness_score += max(0, 0.5 - abs(mfcc_variance - 1.25) / 2)
            
            # Check MFCC range (natural: 20-80)
            if 20 < mfcc_range_avg < 80:
                naturalness_score += 0.5
            else:
                naturalness_score += max(0, 0.5 - abs(mfcc_range_avg - 50) / 100)
            
            return naturalness_score
            
        except Exception as e:
            print(f"❌ Error analyzing voice naturalness: {str(e)}")
            return 0.5
    
    def analyze_spectral_authenticity(self, y, sr):
        """
        Analyze spectral patterns for authenticity
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Authenticity score (0-1)
        """
        try:
            spectral_features = extract_spectral_features(y, sr)
            
            if spectral_features is None:
                return 0.5
            
            authenticity_score = 0
            
            # Check spectral centroid (natural human voice: 1000-4000 Hz)
            centroid = spectral_features['spectral_centroid_mean']
            if 1000 < centroid < 4000:
                authenticity_score += 0.4
            else:
                authenticity_score += max(0, 0.4 - abs(centroid - 2500) / 5000)
            
            # Check zero crossing rate (natural: 0.05-0.15)
            zcr = spectral_features['zero_crossing_rate_mean']
            if 0.05 < zcr < 0.15:
                authenticity_score += 0.3
            else:
                authenticity_score += max(0, 0.3 - abs(zcr - 0.1) / 0.2)
            
            # Check spectral bandwidth (natural voices have moderate bandwidth)
            bandwidth = spectral_features['spectral_bandwidth_mean']
            if 500 < bandwidth < 3000:
                authenticity_score += 0.3
            else:
                authenticity_score += max(0, 0.3 - abs(bandwidth - 1750) / 5000)
            
            return authenticity_score
            
        except Exception as e:
            print(f"❌ Error analyzing spectral authenticity: {str(e)}")
            return 0.5
    
    def analyze_audio(self, audio_path, is_video=False):
        """
        Complete audio analysis pipeline
        
        Args:
            audio_path: Path to audio file (or video file if is_video=True)
            is_video: Whether input is video file
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n🔊 Starting audio analysis: {audio_path}")
        
        try:
            # Extract audio if input is video
            if is_video:
                audio_path = extract_audio_from_video(audio_path)
                if audio_path is None:
                    return {
                        'success': False,
                        'error': 'Could not extract audio from video',
                        'audio_score': 0,
                        'confidence': 0
                    }
            
            # Load audio
            y, sr = load_audio(audio_path, sr=self.sr, duration=30)  # Max 30 seconds
            
            if y is None:
                return {
                    'success': False,
                    'error': 'Could not load audio file',
                    'audio_score': 0,
                    'confidence': 0
                }
            
            print(f"📊 Analyzing audio features...")
            
            # Run all analyses
            voice_naturalness = self.analyze_voice_naturalness(y, sr)
            spectral_authenticity = self.analyze_spectral_authenticity(y, sr)
            
            # Get quality metrics
            quality_metrics = calculate_audio_quality(y, sr)
            audio_quality = quality_metrics['overall_quality'] if quality_metrics else 0.5
            
            # Detect artifacts
            artifact_score = detect_audio_artifacts(y, sr)
            
            # Calculate final audio authenticity score
            # Higher score = more likely to be real
            authenticity_score = (
                min(voice_naturalness, 1.0) * 0.4 +           # 40% weight
                min(spectral_authenticity, 1.0) * 0.3 +       # 30% weight
                min(audio_quality, 1.0) * 0.2 +               # 20% weight
                min((1 - artifact_score), 1.0) * 0.1          # 10% weight
            )
            
            # Convert to percentage and cap at 100
            audio_score = min(authenticity_score * 100, 100.0)
            
            # Calculate confidence based on audio duration
            duration = len(y) / sr
            confidence = min(duration / 10 * 100, 100)  # Full confidence at 10+ seconds
            
            print(f"✅ Audio analysis complete!")
            print(f"   Audio Score: {audio_score:.1f}%")
            print(f"   Confidence: {confidence:.1f}%")
            
            return {
                'success': True,
                'audio_score': round(audio_score, 2),
                'confidence': round(confidence, 2),
                'details': {
                    'voice_naturalness': round(voice_naturalness * 100, 2),
                    'spectral_authenticity': round(spectral_authenticity * 100, 2),
                    'audio_quality': round(audio_quality * 100, 2),
                    'artifact_detection': round(artifact_score * 100, 2),
                    'duration_seconds': round(duration, 2)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in audio analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'audio_score': 0,
                'confidence': 0
            }


# Test the module
if __name__ == "__main__":
    detector = AudioDeepfakeDetector()
    print("✅ Audio Deepfake Detector initialized successfully!")
    print("📝 Ready to analyze audio")