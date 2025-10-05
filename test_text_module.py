from src.models.text_module import TextFactChecker


def test_text_fact_checking():
    print("🧪 Testing Text Fact-Checking Module\n")
    
    # Initialize checker
    checker = TextFactChecker()
    
    # Test 1: True facts
    print("\n" + "="*60)
    print("TEST 1: TRUE FACTS")
    print("="*60)
    true_text = """
    The capital of France is Paris. The Earth orbits around the Sun.
    Water boils at 100 degrees Celsius at sea level. The speed of light
    is approximately 300,000 kilometers per second.
    """
    
    result1 = checker.analyze_text(true_text)
    print("\n📊 RESULTS:")
    print(f"Text Score: {result1['text_score']}%")
    print(f"Confidence: {result1['confidence']}%")
    print(f"Details: {result1.get('details', {})}")
    
    # Test 2: False facts
    print("\n" + "="*60)
    print("TEST 2: FALSE FACTS")
    print("="*60)
    false_text = """
    The capital of France is London. Water boils at 50 degrees Celsius.
    The Moon is made of cheese. Humans have 300 bones in their body.
    """
    
    result2 = checker.analyze_text(false_text)
    print("\n📊 RESULTS:")
    print(f"Text Score: {result2['text_score']}%")
    print(f"Confidence: {result2['confidence']}%")
    print(f"Details: {result2.get('details', {})}")
    
    # Test 3: Mixed facts
    print("\n" + "="*60)
    print("TEST 3: MIXED FACTS")
    print("="*60)
    mixed_text = """
    The capital of France is Paris. The Moon is made of cheese.
    Python is a programming language. Water freezes at 200 degrees.
    """
    
    result3 = checker.analyze_text(mixed_text)
    print("\n📊 RESULTS:")
    print(f"Text Score: {result3['text_score']}%")
    print(f"Confidence: {result3['confidence']}%")
    print(f"Details: {result3.get('details', {})}")
    
    # Test 4: Spanish text
    print("\n" + "="*60)
    print("TEST 4: SPANISH LANGUAGE")
    print("="*60)
    spanish_text = """
    La capital de Francia es París. La Tierra orbita alrededor del Sol.
    El agua hierve a 100 grados Celsius al nivel del mar.
    """
    
    result4 = checker.analyze_text(spanish_text)
    print("\n📊 RESULTS:")
    print(f"Text Score: {result4['text_score']}%")
    print(f"Confidence: {result4['confidence']}%")
    print(f"Details: {result4.get('details', {})}")


if __name__ == "__main__":
    test_text_fact_checking()