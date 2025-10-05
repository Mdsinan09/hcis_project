import numpy as np
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
    Main class for text fact-checking and authenticity detection
    """
    
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        print("🔤 Initializing Text Fact Checker...")
        
        # Load multilingual sentence transformer
        self.model = SentenceTransformer(model_name)
        print(f"✅ Loaded model: {model_name}")
        
        # Load truth database
        self.truth_database = load_truth_database()
        
        # Pre-compute embeddings for truth database
        self.truth_embeddings = self._compute_truth_embeddings()
        
        print("✅ Text Fact Checker initialized")
    
    def _compute_truth_embeddings(self):
        """
        Pre-compute embeddings for all facts in truth database
        
        Returns:
            Dictionary mapping language to embeddings
        """
        print("📊 Computing truth database embeddings...")
        embeddings = {}
        
        for language, facts in self.truth_database.items():
            if facts:
                embeddings[language] = self.model.encode(facts)
                print(f"   ✅ {language}: {len(facts)} facts encoded")
        
        return embeddings
    
    def check_claim_against_database(self, claim, language='english'):
        """
        Check a single claim against truth database
        
        Args:
            claim: Text claim to verify
            language: Language of the claim
            
        Returns:
            Similarity score (0-1)
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
        Analyze factual accuracy of all claims with stricter thresholds
        """
        if not claims:
            return 0.5
        
        similarity_scores = []
        
        for claim in claims:
            score = self.check_claim_against_database(claim, language)
            similarity_scores.append(score)
        
        avg_similarity = np.mean(similarity_scores)
        
        # VERY STRICT SCORING:
        # > 0.90 = Definitely true (exact match)
        # 0.75-0.90 = Probably true (close match)
        # 0.50-0.75 = Uncertain/vague (weak match)
        # 0.30-0.50 = Probably false (poor match)
        # < 0.30 = Definitely false (no match)
        
        if avg_similarity > 0.90:
            accuracy_score = avg_similarity
        elif avg_similarity > 0.75:
            accuracy_score = avg_similarity * 0.85
        elif avg_similarity > 0.50:
            accuracy_score = avg_similarity * 0.40
        elif avg_similarity > 0.30:
            accuracy_score = avg_similarity * 0.20
        else:
            accuracy_score = avg_similarity * 0.10
        
        return accuracy_score
    
    def analyze_language_naturalness(self, text):
        """
        Analyze if text sounds natural vs AI-generated
        
        Args:
            text: Input text
            
        Returns:
            Naturalness score (0-1)
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
        
        Returns:
            Contradiction penalty (0-1, higher = more contradictions)
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
        Complete text analysis pipeline
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n📝 Starting text analysis...")
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
            
            # Run all analyses
            factual_accuracy = self.analyze_factual_accuracy(claims, language)
            language_naturalness = self.analyze_language_naturalness(text)
            hallucination_score = detect_hallucination_patterns(text)
            contradiction_penalty = self.detect_contradictions(claims, language)
            
            # Adjust factual accuracy based on contradictions
            factual_accuracy = factual_accuracy * (1 - contradiction_penalty * 0.5)
            
            # Calculate final text reliability score
            reliability_score = (
                factual_accuracy * 0.5 +
                language_naturalness * 0.3 +
                (1 - hallucination_score) * 0.2
            )
            
            # Convert to percentage
            text_score = min(reliability_score * 100, 100.0)
            
            # Calculate confidence based on number of claims
            confidence = min(len(claims) / 5 * 100, 100)
            
            print(f"✅ Text analysis complete!")
            print(f"   Text Score: {text_score:.1f}%")
            print(f"   Confidence: {confidence:.1f}%")
            
            return {
                'success': True,
                'text_score': round(text_score, 2),
                'confidence': round(confidence, 2),
                'details': {
                    'language_detected': language,
                    'factual_accuracy': round(factual_accuracy * 100, 2),
                    'language_naturalness': round(language_naturalness * 100, 2),
                    'hallucination_detection': round(hallucination_score * 100, 2),
                    'contradiction_penalty': round(contradiction_penalty * 100, 2),
                    'claims_analyzed': len(claims)
                }
            }
        
        except Exception as e:
            print(f"❌ Error in text analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text_score': 0,
                'confidence': 0
            }


# Test the module
if __name__ == "__main__":
    checker = TextFactChecker()
    
    test_text = "The capital of France is Paris. Water boils at 100 degrees Celsius."
    print("\n🧪 Testing with sample text:")
    print(f"   '{test_text}'")
    
    result = checker.analyze_text(test_text)
    
    print("\n📊 RESULTS:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Text Score: {result['text_score']}%")
        print(f"Confidence: {result['confidence']}%")
        print(f"Details: {result['details']}")