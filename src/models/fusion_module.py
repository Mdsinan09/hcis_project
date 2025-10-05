import numpy as np


class HCISFusionEngine:
    """
    Fusion engine that combines video, audio, and text scores
    into final authenticity verdict
    """
    
    def __init__(self):
        # Default weights (can be adjusted)
        self.weights = {
            'video': 0.40,
            'audio': 0.40,
            'text': 0.20
        }
        
        # Verdict thresholds
        self.thresholds = {
            'authentic': 70,      # >= 70% is authentic
            'suspicious': 40,     # 40-70% is suspicious
            'likely_fake': 0      # < 40% is likely fake
        }
        
        print("Fusion Engine initialized")
    
    def calculate_weighted_score(self, video_score, audio_score, text_score):
        """
        Calculate weighted average of all scores
        
        Args:
            video_score: Video authenticity (0-100)
            audio_score: Audio authenticity (0-100)
            text_score: Text reliability (0-100)
            
        Returns:
            Weighted final score
        """
        final_score = (
            video_score * self.weights['video'] +
            audio_score * self.weights['audio'] +
            text_score * self.weights['text']
        )
        
        return final_score
    
    def check_cross_modal_consistency(self, video_score, audio_score, text_score):
        """
        Check if scores are consistent across modalities
        
        Returns:
            Consistency penalty (0-20 points)
        """
        scores = [video_score, audio_score, text_score]
        score_variance = np.var(scores)
        
        # High variance = inconsistent = suspicious
        # Variance > 400 indicates major disagreement
        if score_variance > 400:
            penalty = 20
        elif score_variance > 200:
            penalty = 10
        else:
            penalty = 0
        
        return penalty
    
    def determine_verdict(self, final_score):
        """
        Determine verdict based on final score
        
        Returns:
            Verdict string
        """
        if final_score >= self.thresholds['authentic']:
            return "AUTHENTIC"
        elif final_score >= self.thresholds['suspicious']:
            return "SUSPICIOUS"
        else:
            return "LIKELY FAKE"
    
    def calculate_confidence(self, video_conf, audio_conf, text_conf):
        """
        Calculate overall system confidence
        
        Args:
            video_conf: Video component confidence
            audio_conf: Audio component confidence
            text_conf: Text component confidence
            
        Returns:
            Overall confidence (0-100)
        """
        # Weighted average of component confidences
        overall_confidence = (
            video_conf * self.weights['video'] +
            audio_conf * self.weights['audio'] +
            text_conf * self.weights['text']
        )
        
        return overall_confidence
    
    def generate_explanation(self, video_score, audio_score, text_score, 
                            final_score, verdict):
        """
        Generate human-readable explanation of the decision
        
        Returns:
            Explanation string
        """
        explanations = []
        
        # Analyze each component
        if video_score < 40:
            explanations.append("Video shows signs of manipulation")
        elif video_score > 70:
            explanations.append("Video appears authentic")
        
        if audio_score < 40:
            explanations.append("Audio exhibits synthetic characteristics")
        elif audio_score > 70:
            explanations.append("Audio sounds natural")
        
        if text_score < 40:
            explanations.append("Text contains unverifiable claims")
        elif text_score > 70:
            explanations.append("Text aligns with verified facts")
        
        # Check for inconsistencies
        scores = [video_score, audio_score, text_score]
        if max(scores) - min(scores) > 30:
            explanations.append("Warning: Inconsistency detected between components")
        
        return " | ".join(explanations) if explanations else "Analysis complete"
    
    def fuse(self, video_result, audio_result, text_result):
        """
        Main fusion function - combines all component results
        
        Args:
            video_result: Dict from video detector
            audio_result: Dict from audio detector
            text_result: Dict from text checker
            
        Returns:
            Complete fusion analysis results
        """
        print("\n🔄 Starting fusion analysis...")
        
        try:
            # Extract scores
            video_score = video_result.get('video_score', 0)
            audio_score = audio_result.get('audio_score', 0)
            text_score = text_result.get('text_score', 0)
            
            # Extract confidences
            video_conf = video_result.get('confidence', 0)
            audio_conf = audio_result.get('confidence', 0)
            text_conf = text_result.get('confidence', 0)
            
            print(f"   Video: {video_score:.1f}% (conf: {video_conf:.1f}%)")
            print(f"   Audio: {audio_score:.1f}% (conf: {audio_conf:.1f}%)")
            print(f"   Text: {text_score:.1f}% (conf: {text_conf:.1f}%)")
            
            # Calculate weighted score
            weighted_score = self.calculate_weighted_score(
                video_score, audio_score, text_score
            )
            
            # Check cross-modal consistency
            consistency_penalty = self.check_cross_modal_consistency(
                video_score, audio_score, text_score
            )
            
            # Apply penalty
            final_score = max(0, weighted_score - consistency_penalty)
            
            # Determine verdict
            verdict = self.determine_verdict(final_score)
            
            # Calculate overall confidence
            overall_confidence = self.calculate_confidence(
                video_conf, audio_conf, text_conf
            )
            
            # Generate explanation
            explanation = self.generate_explanation(
                video_score, audio_score, text_score,
                final_score, verdict
            )
            
            print(f"\n✅ Fusion complete!")
            print(f"   Final Score: {final_score:.1f}%")
            print(f"   Verdict: {verdict}")
            print(f"   Confidence: {overall_confidence:.1f}%")
            
            return {
                'success': True,
                'final_score': round(final_score, 2),
                'verdict': verdict,
                'confidence': round(overall_confidence, 2),
                'component_scores': {
                    'video': round(video_score, 2),
                    'audio': round(audio_score, 2),
                    'text': round(text_score, 2)
                },
                'component_confidences': {
                    'video': round(video_conf, 2),
                    'audio': round(audio_conf, 2),
                    'text': round(text_conf, 2)
                },
                'consistency_penalty': consistency_penalty,
                'explanation': explanation
            }
            
        except Exception as e:
            print(f"❌ Error in fusion: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'final_score': 0,
                'verdict': 'ERROR'
            }


# Test module
if __name__ == "__main__":
    fusion = HCISFusionEngine()
    
    # Test case: suspicious audio
    test_video = {'video_score': 75, 'confidence': 90}
    test_audio = {'audio_score': 30, 'confidence': 100}
    test_text = {'text_score': 85, 'confidence': 80}
    
    result = fusion.fuse(test_video, test_audio, test_text)
    print(f"\nTest Result: {result}")