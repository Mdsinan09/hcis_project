from src.models.audio_module import AudioDeepfakeDetector
import sys

def test_audio_detection():
    print("🧪 Testing Audio Detection Module\n")
    
    detector = AudioDeepfakeDetector()
    
    # Test with a sample video (audio will be extracted)
    test_video_path = "data/uploads/mytest.mov"
    
    print(f"Testing with: {test_video_path}\n")
    
    result = detector.analyze_audio(test_video_path, is_video=True)
    
    print("\n📊 RESULTS:")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Audio Score: {result['audio_score']}%")
        print(f"Confidence: {result['confidence']}%")
        
        if 'details' in result:
            print("\n📝 Details:")
            for key, value in result['details'].items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_audio_detection()