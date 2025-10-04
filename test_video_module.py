from src.models.video_module import VideoDeepfakeDetector
import sys

def test_video_detection():
    print("🧪 Testing Video Detection Module\n")
    
    detector = VideoDeepfakeDetector()
    
    # Test with a sample video (you need to provide a test video)
    test_video_path = "data/uploads/test_video.mp4"
    
    print(f"Testing with: {test_video_path}\n")
    
    result = detector.analyze_video(test_video_path)
    
    print("\n📊 RESULTS:")
    print(f"Success: {result['success']}")
    print(f"Video Score: {result['video_score']}%")
    print(f"Confidence: {result['confidence']}%")
    
    if 'details' in result:
        print("\n📝 Details:")
        for key, value in result['details'].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_video_detection()