import json
import os
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection
DetectorFactory.seed = 0


def load_truth_database(database_path='data/truth_database.json'):
    """
    Load truth database from JSON file
    
    Args:
        database_path: Path to truth database JSON
        
    Returns:
        Dictionary with language-specific facts
    """
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        print(f"✅ Loaded truth database with {sum(len(v) for v in database.values())} facts")
        return database
    
    except Exception as e:
        print(f"❌ Error loading truth database: {str(e)}")
        return {
            "english": [
                "The capital of France is Paris",
                "The Earth orbits the Sun",
                "Water boils at 100 degrees Celsius"
            ]
        }


def detect_language(text):
    """
    Detect language of input text
    
    Args:
        text: Input text string
        
    Returns:
        Language code (e.g., 'en', 'es', 'fr')
    """
    try:
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for very short text
        
        lang_code = detect(text)
        
        # Map to our database language names
        lang_map = {
            'en': 'english',
            'es': 'spanish',
            'fr': 'french',
            'de': 'german',
            'it': 'italian',
            'pt': 'portuguese'
        }
        
        detected_lang = lang_map.get(lang_code, 'english')
        print(f"🌍 Detected language: {detected_lang}")
        return detected_lang
    
    except LangDetectException:
        print("⚠️  Could not detect language, defaulting to English")
        return 'english'
    
    except Exception as e:
        print(f"❌ Error detecting language: {str(e)}")
        return 'english'


def extract_claims(text):
    """
    Extract individual claims/sentences from text
    
    Args:
        text: Input text string
        
    Returns:
        List of individual claims
    """
    try:
        # Clean the text
        text = text.strip()
        
        # Split by common sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip very short or empty sentences
            if len(sentence) > 10:
                claims.append(sentence)
        
        print(f"📝 Extracted {len(claims)} claims from text")
        return claims
    
    except Exception as e:
        print(f"❌ Error extracting claims: {str(e)}")
        return [text]  # Return original text as single claim


def preprocess_text(text):
    """
    Clean and normalize text for analysis
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text
    """
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s.!?,;:]', '', text)
        
        return text
    
    except Exception as e:
        print(f"❌ Error preprocessing text: {str(e)}")
        return text


def calculate_text_statistics(text):
    """
    Calculate basic text statistics
    
    Args:
        text: Input text string
        
    Returns:
        Dictionary with text statistics
    """
    try:
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        # Filter empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'character_count': len(text)
        }
    
    except Exception as e:
        print(f"❌ Error calculating text statistics: {str(e)}")
        return {
            'word_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'character_count': 0
        }


def detect_hallucination_patterns(text):
    """
    Detect patterns common in AI-generated hallucinations
    
    Args:
        text: Input text string
        
    Returns:
        Hallucination score (0-1, higher = more suspicious)
    """
    try:
        hallucination_score = 0
        text_lower = text.lower()
        
        # Pattern 1: Overly specific fake details
        specific_patterns = [
            r'\d{4} (january|february|march|april|may|june|july|august|september|october|november|december) \d{1,2}',
            r'exactly \d+',
            r'precisely \d+',
            r'specifically designed for'
        ]
        
        for pattern in specific_patterns:
            if re.search(pattern, text_lower):
                hallucination_score += 0.1
        
        # Pattern 2: Hedging language (common in AI uncertainty)
        hedging_words = ['possibly', 'perhaps', 'might be', 'could be', 'may have']
        hedge_count = sum(1 for word in hedging_words if word in text_lower)
        
        if hedge_count > 2:
            hallucination_score += 0.15
        
        # Pattern 3: Contradictory statements
        contradictions = [
            ('always', 'never'),
            ('all', 'none'),
            ('everyone', 'no one')
        ]
        
        for word1, word2 in contradictions:
            if word1 in text_lower and word2 in text_lower:
                hallucination_score += 0.2
        
        # Pattern 4: Suspiciously round numbers
        round_numbers = re.findall(r'\b(100|1000|10000|1000000)\b', text)
        if len(round_numbers) > 1:
            hallucination_score += 0.1
        
        return min(hallucination_score, 1.0)
    
    except Exception as e:
        print(f"❌ Error detecting hallucination patterns: {str(e)}")
        return 0.5  # Neutral score on error