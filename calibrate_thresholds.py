from src.models.video_module import VideoDeepfakeDetector
from src.models.audio_module import AudioDeepfakeDetector
from src.models.text_module import TextFactChecker
import numpy as np
import glob

# Test with known real/fake samples
real_videos = ["data/uploads/mytest.mov"]  # Add more
fake_videos = glob.glob("data/generated/video/synthetic_audio_video_*.mp4")
print(f"Found {len(fake_videos)} generated videos")

video_detector = VideoDeepfakeDetector()
audio_detector = AudioDeepfakeDetector()

print("Testing REAL content:")
for video in real_videos:
    v_result = video_detector.analyze_video(video)
    a_result = audio_detector.analyze_audio(video, is_video=True)
    print(f"  Video: {v_result['video_score']:.1f}%, Audio: {a_result['audio_score']:.1f}%")

print("\nTesting FAKE content:")
for video in fake_videos:
    v_result = video_detector.analyze_video(video)
    a_result = audio_detector.analyze_audio(video, is_video=True)
    print(f"  Video: {v_result['video_score']:.1f}%, Audio: {a_result['audio_score']:.1f}%")

print("\nRecommended adjustments based on results above")