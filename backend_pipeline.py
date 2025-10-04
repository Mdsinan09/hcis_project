import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.video_module import VideoDeepfakeDetector
from models.audio_module import AudioDeepfakeDetector


class HCISPipeline:
    """
    Main pipeline for HCIS content analysis
    """
    
    def __init__(self):
        print("🚀 Initializing HCIS Pipeline...")
        
        # Initialize video detector
        self.video_detector = VideoDeepfakeDetector()
        
        # Initialize audio detector
        self.audio_detector = AudioDeepfakeDetector()
        
        print("✅ Pipeline ready!")
    
    def analyze_video(self, video_path):
        """
        Analyze video for deepfakes
        
        Args:
            video_path: Path to video file
            
        Returns:
            Analysis results dictionary
        """
        return self.video_detector.analyze_video(video_path)
    
    def analyze_audio(self, audio_path, is_video=True):
        """
        Analyze audio for deepfakes
        
        Args:
            audio_path: Path to audio file (or video file if is_video=True)
            is_video: Whether input is video file
            
        Returns:
            Analysis results dictionary
        """
        return self.audio_detector.analyze_audio(audio_path, is_video=is_video)
    
    def analyze_text(self, text):
        """
        Placeholder for text analysis (Week 4)
        """
        return {
            'success': True,
            'text_score': 70.0,
            'confidence': 85.0,
            'message': 'Text analysis coming in Week 4!'
        }
    
    def fusion_analysis(self, video_score, audio_score, text_score):
        """
        Combine all scores into final verdict
        
        Args:
            video_score: Video authenticity score (0-100)
            audio_score: Audio authenticity score (0-100)
            text_score: Text reliability score (0-100)
            
        Returns:
            Combined analysis results
        """
        final_score = (video_score * 0.4 + audio_score * 0.4 + text_score * 0.2)
        
        if final_score >= 70:
            verdict = "AUTHENTIC"
        elif final_score >= 40:
            verdict = "SUSPICIOUS"
        else:
            verdict = "LIKELY FAKE"
        
        return {
            'success': True,
            'final_score': round(final_score, 2),
            'verdict': verdict,
            'components': {
                'video': video_score,
                'audio': audio_score,
                'text': text_score
            }
        }


# Test the pipeline
if __name__ == "__main__":
    pipeline = HCISPipeline()
    print("✅ HCIS Pipeline initialized successfully!")