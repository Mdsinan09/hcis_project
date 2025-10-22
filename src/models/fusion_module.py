import numpy as np


class HCISFusionEngine:
    """
    Adaptive fusion engine that combines video, audio, and text scores
    ONLY when those modalities are actually present in the content.
    """
    
    def __init__(self):
        # Default weights when all modalities present
        self.default_weights = {
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
        
        print("✅ Adaptive Fusion Engine initialized")
    
    def calculate_adaptive_weights(self, video_score, audio_score, text_score):
        """
        Calculate weights based on which modalities are actually present.
        A score of 0 means that modality is not present/not analyzed.
        
        Returns:
            Dict of normalized weights and list of active modalities
        """
        active_modalities = []
        weights = {}
        
        # Check which modalities are present (non-zero scores)
        if video_score > 0:
            active_modalities.append('video')
            weights['video'] = self.default_weights['video']
        
        if audio_score > 0:
            active_modalities.append('audio')
            weights['audio'] = self.default_weights['audio']
        
        if text_score > 0:
            active_modalities.append('text')
            weights['text'] = self.default_weights['text']
        
        # If no modalities detected, default to video only
        if not active_modalities:
            active_modalities = ['video']
            weights['video'] = 1.0
        else:
            # Normalize weights to sum to 1.0
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}
        
        return weights, active_modalities
    
    def calculate_weighted_score(self, video_score, audio_score, text_score, weights):
        """
        Calculate weighted average using adaptive weights
        """
        final_score = 0
        
        if 'video' in weights and video_score > 0:
            final_score += video_score * weights['video']
        
        if 'audio' in weights and audio_score > 0:
            final_score += audio_score * weights['audio']
        
        if 'text' in weights and text_score > 0:
            final_score += text_score * weights['text']
        
        return final_score
    
    def check_cross_modal_consistency(self, active_scores):
        """
        Check consistency only between ACTIVE modalities
        
        Args:
            active_scores: List of scores for active modalities only
            
        Returns:
            Consistency penalty (0-20 points)
        """
        if len(active_scores) < 2:
            # Can't check consistency with only one modality
            return 0
        
        score_variance = np.var(active_scores)
        
        # High variance = inconsistent = suspicious
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
        """
        if final_score >= self.thresholds['authentic']:
            return "AUTHENTIC"
        elif final_score >= self.thresholds['suspicious']:
            return "SUSPICIOUS"
        else:
            return "LIKELY FAKE"
    
    def calculate_confidence(self, video_conf, audio_conf, text_conf, weights):
        """
        Calculate overall system confidence using adaptive weights
        """
        overall_confidence = 0
        
        if 'video' in weights and video_conf > 0:
            overall_confidence += video_conf * weights['video']
        
        if 'audio' in weights and audio_conf > 0:
            overall_confidence += audio_conf * weights['audio']
        
        if 'text' in weights and text_conf > 0:
            overall_confidence += text_conf * weights['text']
        
        return overall_confidence
    
    def generate_explanation(self, video_score, audio_score, text_score, 
                            final_score, verdict, active_modalities):
        """
        Generate human-readable explanation based on active modalities
        """
        explanations = []
        
        # Only analyze components that are present
        if 'video' in active_modalities:
            if video_score < 40:
                explanations.append("Video shows signs of manipulation")
            elif video_score > 70:
                explanations.append("Video appears authentic")
            else:
                explanations.append("Video quality is inconclusive")
        
        if 'audio' in active_modalities:
            if audio_score < 40:
                explanations.append("Audio exhibits synthetic characteristics")
            elif audio_score > 70:
                explanations.append("Audio sounds natural")
            else:
                explanations.append("Audio analysis is inconclusive")
        
        if 'text' in active_modalities:
            if text_score < 40:
                explanations.append("Text contains unverifiable claims")
            elif text_score > 70:
                explanations.append("Text aligns with verified facts")
            else:
                explanations.append("Text verification is inconclusive")
        
        # Check for inconsistencies only between active modalities
        active_scores = []
        if 'video' in active_modalities:
            active_scores.append(video_score)
        if 'audio' in active_modalities:
            active_scores.append(audio_score)
        if 'text' in active_modalities:
            active_scores.append(text_score)
        
        if len(active_scores) > 1 and (max(active_scores) - min(active_scores) > 30):
            explanations.append("⚠️ Inconsistency detected between components")
        
        return " | ".join(explanations) if explanations else "Analysis complete"
    
    def fuse(self, video_result, audio_result, text_result):
        """
        Main adaptive fusion function - combines only PRESENT components
        
        Args:
            video_result: Dict from video detector
            audio_result: Dict from audio detector  
            text_result: Dict from text checker
            
        Returns:
            Complete fusion analysis results
        """
        print("\n🔄 Starting adaptive fusion analysis...")
        
        try:
            # Extract scores (default to 0 if not present)
            video_score = video_result.get('video_score', 0) if video_result else 0
            audio_score = audio_result.get('audio_score', 0) if audio_result else 0
            text_score = text_result.get('text_score', 0) if text_result else 0
            
            # Extract confidences
            video_conf = video_result.get('confidence', 0) if video_result else 0
            audio_conf = audio_result.get('confidence', 0) if audio_result else 0
            text_conf = text_result.get('confidence', 0) if text_result else 0
            
            # Calculate adaptive weights based on what's present
            weights, active_modalities = self.calculate_adaptive_weights(
                video_score, audio_score, text_score
            )
            
            print(f"   Active Modalities: {', '.join(active_modalities)}")
            print(f"   Adaptive Weights: {weights}")
            
            if video_score > 0:
                print(f"   📹 Video: {video_score:.1f}% (conf: {video_conf:.1f}%)")
            if audio_score > 0:
                print(f"   🔊 Audio: {audio_score:.1f}% (conf: {audio_conf:.1f}%)")
            if text_score > 0:
                print(f"   📝 Text: {text_score:.1f}% (conf: {text_conf:.1f}%)")
            
            # Calculate weighted score using adaptive weights
            weighted_score = self.calculate_weighted_score(
                video_score, audio_score, text_score, weights
            )
            
            # Check consistency only between active modalities
            active_scores = [s for s in [video_score, audio_score, text_score] if s > 0]
            consistency_penalty = self.check_cross_modal_consistency(active_scores)
            
            # Apply penalty
            final_score = max(0, weighted_score - consistency_penalty)
            
            # Determine verdict
            verdict = self.determine_verdict(final_score)
            
            # Calculate overall confidence
            overall_confidence = self.calculate_confidence(
                video_conf, audio_conf, text_conf, weights
            )
            
            # Generate explanation
            explanation = self.generate_explanation(
                video_score, audio_score, text_score,
                final_score, verdict, active_modalities
            )
            
            print(f"\n✅ Fusion complete!")
            print(f"   Final Score: {final_score:.1f}%")
            print(f"   Verdict: {verdict}")
            print(f"   Confidence: {overall_confidence:.1f}%")
            
            return {
                'success': True,
                'fusion_score': round(final_score, 2),  # Changed from 'final_score'
                'verdict': verdict,
                'confidence': round(overall_confidence, 2),
                'active_modalities': active_modalities,
                'adaptive_weights': {k: round(v, 3) for k, v in weights.items()},
                'video_score': round(video_score, 2),
                'audio_score': round(audio_score, 2),
                'text_score': round(text_score, 2),
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
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'fusion_score': 0,
                'video_score': 0,
                'audio_score': 0,
                'text_score': 0,
                'verdict': 'ERROR'
            }


# Test module
if __name__ == "__main__":
    fusion = HCISFusionEngine()
    
    print("\n" + "="*60)
    print("TEST 1: Video + Audio (no text)")
    print("="*60)
    test_video = {'video_score': 75, 'confidence': 90}
    test_audio = {'audio_score': 30, 'confidence': 100}
    test_text = {'text_score': 0, 'confidence': 0}  # No text
    
    result = fusion.fuse(test_video, test_audio, test_text)
    print(f"\nResult: Final={result['fusion_score']}%, Verdict={result['verdict']}")
    print(f"Active: {result['active_modalities']}")
    
    print("\n" + "="*60)
    print("TEST 2: Video only (no audio, no text)")
    print("="*60)
    test_video = {'video_score': 85, 'confidence': 80}
    test_audio = {'audio_score': 0, 'confidence': 0}
    test_text = {'text_score': 0, 'confidence': 0}
    
    result = fusion.fuse(test_video, test_audio, test_text)
    print(f"\nResult: Final={result['fusion_score']}%, Verdict={result['verdict']}")
    print(f"Active: {result['active_modalities']}")