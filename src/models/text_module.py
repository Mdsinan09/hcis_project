import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_helpers import (
    load_truth_database,
    detect_language,
    extract_claims,
    preprocess_text,
    calculate_text_statistics,
    detect_hallucination_patterns
)


class TextFactChecker:
    """
    Enhanced text fact-checker with factual content detection
    """
    
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        print("🔤 Initializing Enhanced Text Fact Checker...")
        
        # Load multilingual sentence transformer
        self.model = SentenceTransformer(model_name)
        print(f"✅ Loaded model: {model_name}")
        
        # Load truth database
        self.truth_database = load_truth_database()
        
        # Pre-compute embeddings for truth database
        self.truth_embeddings = self._compute_truth_embeddings()
        
        # Known factual indicators that boost reliability
        self.factual_keywords = [
            # Scientific terms
            'degrees', 'celsius', 'fahrenheit', 'temperature', 'boils',
            'chemical', 'symbol', 'element', 'compound', 'molecule',
            'photosynthesis', 'process', 'energy', 'oxygen', 'carbon',
            
            # Geographic/factual
            'capital', 'city', 'country', 'ocean', 'mountain', 'river',
            'continent', 'planet', 'earth', 'sun', 'moon', 'solar system',
            'revolves', 'orbit', 'elliptical',
            
            # Measurable facts
            'bones', 'body', 'human', 'largest', 'highest', 'deepest',
            'year', 'century', 'distance', 'speed', 'light', 'sound',
            
            # Physical laws/facts
            'travels', 'faster', 'gravity', 'force', 'mass', 'velocity',
            'atmospheric', 'pressure', 'standard'
        ]
        
        print("✅ Enhanced Text Fact Checker initialized")
    
    def _compute_truth_embeddings(self):
        """
        Pre-compute embeddings for all facts in truth database
        """
        print("📊 Computing truth database embeddings...")
        embeddings = {}
        
        for language, facts in self.truth_database.items():
            if facts:
                embeddings[language] = self.model.encode(facts)
                print(f"   ✅ {language}: {len(facts)} facts encoded")
        
        return embeddings
    
    def calculate_factual_density(self, text):
        """
        Calculate how factual/informative the text appears
        Returns: 0.0 to 1.0
        """
        text_lower = text.lower()
        
        # Count factual keyword matches
        factual_count = sum(1 for keyword in self.factual_keywords if keyword in text_lower)
        
        # Count numbers (often indicate facts)
        number_count = len(re.findall(r'\b\d+(?:\.\d+)?\b', text))
        
        # Count proper nouns (capitalized words, often places/names)
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', text))
        
        # Calculate density score
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        # Normalize scores - more factual indicators = higher density
        factual_density = min(1.0, (factual_count * 1.5 + number_count * 0.8 + proper_nouns * 0.4) / (word_count * 0.2))
        
        return factual_density
    
    def check_sentence_quality(self, text):
        """
        Check if sentences are well-formed and coherent
        Returns: 0.0 to 1.0
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) == 0:
            return 0.0
        
        quality_score = 0
        
        for sentence in sentences:
            words = sentence.split()
            
            # Good sentences have 5-30 words
            if 5 <= len(words) <= 30:
                quality_score += 1
            elif len(words) > 3:
                quality_score += 0.5
        
        return min(1.0, quality_score / len(sentences))
    
    def check_claim_against_database(self, claim, language='english'):
        """
        Check a single claim against truth database
        """
        try:
            # Get embeddings for this language
            if language not in self.truth_embeddings:
                language = 'english'  # Fallback to English
            
            truth_emb = self.truth_embeddings.get(language)
            
            if truth_emb is None or len(truth_emb) == 0:
                return 0.5  # Neutral score if no database
            
            # Encode the claim
            claim_embedding = self.model.encode([claim])
            
            # Calculate similarity with all facts
            similarities = cosine_similarity(claim_embedding, truth_emb)[0]
            
            # Get best match
            max_similarity = np.max(similarities)
            
            return float(max_similarity)
        
        except Exception as e:
            print(f"❌ Error checking claim: {str(e)}")
            return 0.5
    
    def analyze_factual_accuracy(self, claims, language='english'):
        """
        Analyze factual accuracy with BALANCED scoring for factual content
        """
        if not claims:
            return 0.5
        
        similarity_scores = []
        
        for claim in claims:
            score = self.check_claim_against_database(claim, language)
            similarity_scores.append(score)
        
        avg_similarity = np.mean(similarity_scores)
        
        # IMPROVED BALANCED SCORING:
        # High similarity = very factual
        # Medium similarity = somewhat factual (don't penalize too much)
        # Low similarity = not factual
        
        if avg_similarity > 0.85:
            # Very high match - definitely true
            accuracy_score = avg_similarity * 0.95
        elif avg_similarity > 0.70:
            # Good match - probably true
            accuracy_score = avg_similarity * 0.85
        elif avg_similarity > 0.50:
            # Medium match - could be true (LESS HARSH)
            accuracy_score = avg_similarity * 0.70  # Changed from 0.40
        elif avg_similarity > 0.30:
            # Weak match - uncertain
            accuracy_score = avg_similarity * 0.50  # Changed from 0.20
        else:
            # Very weak match
            accuracy_score = avg_similarity * 0.30  # Changed from 0.10
        
        return accuracy_score
    
    def analyze_language_naturalness(self, text):
        """
        Analyze if text sounds natural vs AI-generated
        """
        try:
            stats = calculate_text_statistics(text)
            
            naturalness_score = 0
            
            # Check 1: Sentence length (natural: 15-25 words)
            avg_sent_length = stats['avg_sentence_length']
            if 10 < avg_sent_length < 30:
                naturalness_score += 0.3
            else:
                deviation = abs(avg_sent_length - 20) / 20
                naturalness_score += max(0, 0.3 - deviation * 0.3)
            
            # Check 2: Word length (natural: 4-6 characters)
            avg_word_length = stats['avg_word_length']
            if 3 < avg_word_length < 7:
                naturalness_score += 0.3
            else:
                deviation = abs(avg_word_length - 5) / 5
                naturalness_score += max(0, 0.3 - deviation * 0.3)
            
            # Check 3: Sentence count (should have multiple sentences)
            sentence_count = stats['sentence_count']
            if sentence_count >= 2:
                naturalness_score += 0.2
            else:
                naturalness_score += 0.1
            
            # Check 4: Text length (reasonable amount of content)
            word_count = stats['word_count']
            if 20 < word_count < 200:
                naturalness_score += 0.2
            else:
                naturalness_score += 0.1
            
            return naturalness_score
        
        except Exception as e:
            print(f"❌ Error analyzing language naturalness: {str(e)}")
            return 0.5
    
    def detect_contradictions(self, claims, language='english'):
        """
        Check if claims explicitly contradict known facts
        """
        if language not in self.truth_embeddings:
            language = 'english'
        
        truth_emb = self.truth_embeddings.get(language)
        if truth_emb is None:
            return 0
        
        contradiction_score = 0
        truth_facts = self.truth_database.get(language, [])
        
        for claim in claims:
            claim_lower = claim.lower()
            
            # Check for explicit contradictions with known facts
            for fact in truth_facts:
                fact_lower = fact.lower()
                
                # Extract key entities (simple approach)
                if any(word in claim_lower and word in fact_lower 
                       for word in ['capital', 'temperature', 'speed', 'year', 'number']):
                    
                    # If same topic but different values = contradiction
                    claim_embedding = self.model.encode([claim])
                    fact_embedding = self.model.encode([fact])
                    similarity = cosine_similarity(claim_embedding, fact_embedding)[0][0]
                    
                    # Low similarity on same topic = likely contradiction
                    if 0.4 < similarity < 0.7:
                        contradiction_score += 0.3
        
        return min(contradiction_score, 1.0)
    
    def analyze_text(self, text):
        """
        Complete ENHANCED text analysis pipeline
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n📝 Starting enhanced text analysis...")
        print(f"   Input length: {len(text)} characters")
        
        try:
            # Detect language
            language = detect_language(text)
            
            # Extract claims
            claims = extract_claims(text)
            
            if not claims:
                return {
                    'success': False,
                    'error': 'No claims could be extracted from text',
                    'text_score': 0,
                    'confidence': 0
                }
            
            print(f"📊 Analyzing {len(claims)} claims in {language}...")
            
            # === ENHANCED ANALYSIS ===
            
            # 1. NEW: Factual density (rewards fact-heavy text)
            factual_density = self.calculate_factual_density(text)
            print(f"   📊 Factual Density: {factual_density:.2f}")
            
            # 2. NEW: Sentence quality
            sentence_quality = self.check_sentence_quality(text)
            print(f"   ✍️  Sentence Quality: {sentence_quality:.2f}")
            
            # 3. Factual accuracy (improved scoring)
            factual_accuracy = self.analyze_factual_accuracy(claims, language)
            print(f"   ✅ Factual Accuracy: {factual_accuracy:.2f}")
            
            # 4. Language naturalness
            language_naturalness = self.analyze_language_naturalness(text)
            print(f"   💬 Language Naturalness: {language_naturalness:.2f}")
            
            # 5. Hallucination detection
            hallucination_score = detect_hallucination_patterns(text)
            print(f"   🔍 Hallucination Score: {hallucination_score:.2f}")
            
            # 6. Contradiction detection
            contradiction_penalty = self.detect_contradictions(claims, language)
            print(f"   ⚠️  Contradiction Penalty: {contradiction_penalty:.2f}")
            
            # Adjust factual accuracy based on contradictions
            factual_accuracy = factual_accuracy * (1 - contradiction_penalty * 0.5)
            
            # === IMPROVED SCORING FORMULA ===
            # Balance between database matching and factual density
            reliability_score = (
                factual_density * 0.25 +         # NEW: Reward factual keywords/numbers
                factual_accuracy * 0.35 +        # Slightly reduced from 0.50
                sentence_quality * 0.15 +        # NEW: Reward well-formed text
                language_naturalness * 0.20 +    # Reduced from 0.30
                (1 - hallucination_score) * 0.05 # Reduced from 0.20
            )
            
            # BONUS: If text is very factual (density > 0.6), boost score
            if factual_density > 0.6:
                boost = min(0.15, (factual_density - 0.6) * 0.3)
                reliability_score = min(1.0, reliability_score + boost)
                print(f"   ✨ Factual content bonus: +{boost:.2f}")
            
            # Convert to percentage
            text_score = min(reliability_score * 100, 100.0)
            
            # Calculate confidence based on text characteristics
            base_confidence = min(len(claims) / 5 * 100, 100)
            
            # Boost confidence if text has high factual density
            if factual_density > 0.6:
                base_confidence = min(90, base_confidence + 15)
            
            # Boost confidence if sentence quality is high
            if sentence_quality > 0.8:
                base_confidence = min(95, base_confidence + 10)
            
            confidence = base_confidence
            
            print(f"✅ Enhanced text analysis complete!")
            print(f"   📈 Text Score: {text_score:.1f}%")
            print(f"   🎯 Confidence: {confidence:.1f}%")
            
            return {
                'success': True,
                'text_score': round(text_score, 2),
                'confidence': round(confidence, 2),
                'details': {
                    'language_detected': language,
                    'factual_density': round(factual_density * 100, 2),
                    'factual_accuracy': round(factual_accuracy * 100, 2),
                    'sentence_quality': round(sentence_quality * 100, 2),
                    'language_naturalness': round(language_naturalness * 100, 2),
                    'hallucination_detection': round(hallucination_score * 100, 2),
                    'contradiction_penalty': round(contradiction_penalty * 100, 2),
                    'claims_analyzed': len(claims)
                }
            }
        
        except Exception as e:
            print(f"❌ Error in text analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'text_score': 0,
                'confidence': 0
            }


# Test the module
if __name__ == "__main__":
    checker = TextFactChecker()
    
    # Test 1: Simple factual text
    test_text_1 = "The capital of France is Paris. Water boils at 100 degrees Celsius."
    print("\n🧪 TEST 1: Simple factual text:")
    print(f"   '{test_text_1}'")
    result_1 = checker.analyze_text(test_text_1)
    print(f"\n📊 RESULTS: Score={result_1['text_score']}%, Confidence={result_1['confidence']}%")
    
    # Test 2: Your comprehensive factual text
    test_text_2 = """The Sun is the star at the center of the Solar System. The Earth revolves around the Sun in an elliptical orbit. Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at standard atmospheric pressure. The capital city of France is Paris. Light travels faster than sound. Photosynthesis is the process used by plants to convert light energy into chemical energy. The current year is 2025. The human body has 206 bones in total. The largest ocean on Earth is the Pacific Ocean. Mount Everest is the highest mountain above sea level. Oxygen is denoted by the chemical symbol O."""
    
    print("\n\n🧪 TEST 2: Comprehensive factual text:")
    print(f"   Length: {len(test_text_2)} chars")
    result_2 = checker.analyze_text(test_text_2)
    print(f"\n📊 RESULTS: Score={result_2['text_score']}%, Confidence={result_2['confidence']}%")
    if result_2['success']:
        print(f"Details:")
        for key, value in result_2['details'].items():
            print(f"  - {key}: {value}")