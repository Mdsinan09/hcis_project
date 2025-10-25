import numpy as np


class HCISFusionEngine:
    """
    Adaptive fusion engine with SMART CONFIDENCE-BASED weighting.
    Automatically trusts high-confidence components more.
    """
    
    def __init__(self):
        # Default base weights
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
        
        print("✅ Adaptive Fusion Engine with Smart Weighting initialized")
    
    def calculate_adaptive_weights(self, video_score, audio_score, text_score,
                                   video_conf, audio_conf, text_conf):
        """
        Calculate weights based on:
        1. Which modalities are present (non-zero scores)
        2. Confidence levels (high confidence = higher weight)
        
        Returns:
            Dict of normalized weights and list of active modalities
        """
        active_modalities = []
        weights = {}
        confidences = {}
        
        # Check which modalities are present (non-zero scores)
        if video_score > 0:
            active_modalities.append('video')
            weights['video'] = self.default_weights['video']
            confidences['video'] = video_conf
        
        if audio_score > 0:
            active_modalities.append('audio')
            weights['audio'] = self.default_weights['audio']
            confidences['audio'] = audio_conf
        
        if text_score > 0:
            active_modalities.append('text')
            weights['text'] = self.default_weights['text']
            confidences['text'] = text_conf
        
        # If no modalities detected, default to video only
        if not active_modalities:
            active_modalities = ['video']
            weights['video'] = 1.0
            return weights, active_modalities
        
        # === SMART WEIGHTING: Adjust by confidence ===
        if len(active_modalities) > 1:
            for modality in active_modalities:
                conf = confidences[modality]
                
                # Confidence-based multipliers
                if conf >= 80:
                    # Very high confidence: boost by 30%
                    weights[modality] *= 1.3
                elif conf >= 60:
                    # Good confidence: boost by 10%
                    weights[modality] *= 1.1
                elif conf < 40:
                    # Low confidence: reduce by 40%
                    weights[modality] *= 0.6
                elif conf < 50:
                    # Medium-low confidence: reduce by 20%
                    weights[modality] *= 0.8
                # 50-60 confidence: no adjustment (1.0x)
        
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
        DISABLED: Penalties removed for simpler, more intuitive scoring
        
        Args:
            active_scores: List of scores for active modalities only
            
        Returns:
            Consistency penalty (always 0 - disabled)
        """
        # SIMPLIFIED: No penalties - just trust the weighted average
        return 0
    
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
                            final_score, verdict, active_modalities, weights):
        """
        Generate human-readable explanation based on active modalities
        """
        explanations = []
        
        # Only analyze components that are present
        if 'video' in active_modalities:
            if video_score < 40:
                explanations.append(f"🎥 Video shows manipulation signs (weight: {weights['video']:.1%})")
            elif video_score > 70:
                explanations.append(f"✅ Video appears authentic (weight: {weights['video']:.1%})")
            else:
                explanations.append(f"⚠️ Video analysis inconclusive (weight: {weights['video']:.1%})")
        
        if 'audio' in active_modalities:
            if audio_score < 40:
                explanations.append(f"🔊 Audio exhibits synthetic traits (weight: {weights['audio']:.1%})")
            elif audio_score > 70:
                explanations.append(f"✅ Audio sounds natural (weight: {weights['audio']:.1%})")
            else:
                explanations.append(f"⚠️ Audio analysis inconclusive (weight: {weights['audio']:.1%})")
        
        if 'text' in active_modalities:
            if text_score < 40:
                explanations.append(f"📝 Text contains unverifiable claims (weight: {weights['text']:.1%})")
            elif text_score > 70:
                explanations.append(f"✅ Text aligns with facts (weight: {weights['text']:.1%})")
            else:
                explanations.append(f"⚠️ Text verification inconclusive (weight: {weights['text']:.1%})")
        
        # Check for inconsistencies only between active modalities
        active_scores = []
        if 'video' in active_modalities:
            active_scores.append(video_score)
        if 'audio' in active_modalities:
            active_scores.append(audio_score)
        if 'text' in active_modalities:
            active_scores.append(text_score)
        
        if len(active_scores) > 1:
            score_range = max(active_scores) - min(active_scores)
            if score_range > 40:  # Only warn if VERY different (40%+ gap)
                explanations.append(f"ℹ️ Score variance: {score_range:.0f}% across components")
        
        return " | ".join(explanations) if explanations else "Analysis complete"
    
    def fuse(self, video_result, audio_result, text_result):
        """
        Main adaptive fusion function with SMART confidence-based weighting
        
        Args:
            video_result: Dict from video detector
            audio_result: Dict from audio detector  
            text_result: Dict from text checker
            
        Returns:
            Complete fusion analysis results
        """
        print("\n🔄 Starting adaptive fusion with smart weighting...")
        
        try:
            # Extract scores (default to 0 if not present)
            video_score = video_result.get('video_score', 0) if video_result else 0
            audio_score = audio_result.get('audio_score', 0) if audio_result else 0
            text_score = text_result.get('text_score', 0) if text_result else 0
            
            # Extract confidences
            video_conf = video_result.get('confidence', 0) if video_result else 0
            audio_conf = audio_result.get('confidence', 0) if audio_result else 0
            text_conf = text_result.get('confidence', 0) if text_result else 0
            
            # Calculate adaptive weights based on presence AND confidence
            weights, active_modalities = self.calculate_adaptive_weights(
                video_score, audio_score, text_score,
                video_conf, audio_conf, text_conf
            )
            
            print(f"   Active Modalities: {', '.join(active_modalities)}")
            print(f"   Smart Adaptive Weights: {weights}")
            
            if video_score > 0:
                print(f"   📹 Video: {video_score:.1f}% (conf: {video_conf:.1f}%) → weight: {weights.get('video', 0):.1%}")
            if audio_score > 0:
                print(f"   🔊 Audio: {audio_score:.1f}% (conf: {audio_conf:.1f}%) → weight: {weights.get('audio', 0):.1%}")
            if text_score > 0:
                print(f"   📝 Text: {text_score:.1f}% (conf: {text_conf:.1f}%) → weight: {weights.get('text', 0):.1%}")
            
            # Calculate weighted score using adaptive weights
            weighted_score = self.calculate_weighted_score(
                video_score, audio_score, text_score, weights
            )
            
            # No consistency penalty - keep it simple
            consistency_penalty = 0
            
            # Final score is just the weighted average (no penalties)
            final_score = weighted_score
            
            # Determine verdict
            verdict = self.determine_verdict(final_score)
            
            # Calculate overall confidence
            overall_confidence = self.calculate_confidence(
                video_conf, audio_conf, text_conf, weights
            )
            
            # Generate explanation
            explanation = self.generate_explanation(
                video_score, audio_score, text_score,
                final_score, verdict, active_modalities, weights
            )
            
            print(f"\n✅ Fusion complete!")
            print(f"   Weighted Score: {weighted_score:.1f}% (No penalties applied)")
            print(f"   Final Score: {final_score:.1f}%")
            print(f"   Verdict: {verdict}")
            print(f"   Confidence: {overall_confidence:.1f}%")
            
            return {
                'success': True,
                'fusion_score': round(final_score, 2),
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
                'consistency_penalty': 0,  # Disabled for simplicity
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
    print("TEST 1: Video (high conf) + Audio (low conf) + Text (low conf)")
    print("="*60)
    test_video = {'video_score': 83.77, 'confidence': 90}
    test_audio = {'audio_score': 58, 'confidence': 45}
    test_text = {'text_score': 59.83, 'confidence': 40}
    
    result = fusion.fuse(test_video, test_audio, test_text)
    print(f"\nResult: Final={result['fusion_score']}%, Verdict={result['verdict']}")
    print(f"Weights: {result['adaptive_weights']}")
    
    print("\n" + "="*60)
    print("TEST 2: Video + Audio only (no text)")
    print("="*60)
    test_video = {'video_score': 83.77, 'confidence': 90}
    test_audio = {'audio_score': 58, 'confidence': 45}
    test_text = {'text_score': 0, 'confidence': 0}
    
    result = fusion.fuse(test_video, test_audio, test_text)
    print(f"\nResult: Final={result['fusion_score']}%, Verdict={result['verdict']}")
    print(f"Weights: {result['adaptive_weights']}")