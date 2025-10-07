import os
import glob
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

from src.models.video_module import VideoDeepfakeDetector
from src.models.audio_module import AudioDeepfakeDetector

def extract_features():
    """Extract features from all training videos"""
    
    video_detector = VideoDeepfakeDetector()
    audio_detector = AudioDeepfakeDetector()
    
    X_video = []
    X_audio = []
    y = []
    
    print("Extracting REAL video features...")
    real_videos = glob.glob("data/training/real/*.mp4") + glob.glob("data/training/real/*.mov")
    
    for video_path in real_videos:
        print(f"  Processing: {video_path}")
        
        # Extract raw features (not scores)
        video_result = video_detector.analyze_video(video_path)
        audio_result = audio_detector.analyze_audio(video_path, is_video=True)
        
        if video_result['success'] and audio_result['success']:
            # Use detailed features, not final scores
            video_features = [
                video_result['details']['face_consistency'],
                video_result['details']['average_quality'],
                video_result['details']['artifact_detection'],
                video_result['confidence']
            ]
            
            audio_features = [
                audio_result['details']['voice_naturalness'],
                audio_result['details']['spectral_authenticity'],
                audio_result['details']['audio_quality'],
                audio_result['details']['artifact_detection']
            ]
            
            X_video.append(video_features)
            X_audio.append(audio_features)
            y.append(1)  # Real = 1
    
    print("Extracting FAKE video features...")
    fake_videos = glob.glob("data/training/fake/*.mp4") + glob.glob("data/training/fake/*.mov")
    
    for video_path in fake_videos:
        print(f"  Processing: {video_path}")
        
        video_result = video_detector.analyze_video(video_path)
        audio_result = audio_detector.analyze_audio(video_path, is_video=True)
        
        if video_result['success'] and audio_result['success']:
            video_features = [
                video_result['details']['face_consistency'],
                video_result['details']['average_quality'],
                video_result['details']['artifact_detection'],
                video_result['confidence']
            ]
            
            audio_features = [
                audio_result['details']['voice_naturalness'],
                audio_result['details']['spectral_authenticity'],
                audio_result['details']['audio_quality'],
                audio_result['details']['artifact_detection']
            ]
            
            X_video.append(video_features)
            X_audio.append(audio_features)
            y.append(0)  # Fake = 0
    
    return np.array(X_video), np.array(X_audio), np.array(y)


def train_models():
    """Train SVM classifiers on extracted features"""
    
    print("\n" + "="*60)
    print("EXTRACTING FEATURES FROM TRAINING DATA")
    print("="*60)
    
    X_video, X_audio, y = extract_features()
    
    print(f"\nDataset size: {len(y)} samples")
    print(f"  Real: {np.sum(y == 1)}")
    print(f"  Fake: {np.sum(y == 0)}")
    
    # Split data
    X_v_train, X_v_test, y_v_train, y_v_test = train_test_split(
        X_video, y, test_size=0.2, random_state=42
    )
    
    X_a_train, X_a_test, y_a_train, y_a_test = train_test_split(
        X_audio, y, test_size=0.2, random_state=42
    )
    
    print("\n" + "="*60)
    print("TRAINING VIDEO CLASSIFIER")
    print("="*60)
    
    video_clf = SVC(kernel='rbf', probability=True, C=1.0, gamma='scale')
    video_clf.fit(X_v_train, y_v_train)
    
    y_v_pred = video_clf.predict(X_v_test)
    print(f"\nVideo Accuracy: {accuracy_score(y_v_test, y_v_pred):.2%}")
    print(classification_report(y_v_test, y_v_pred, target_names=['Fake', 'Real']))
    
    joblib.dump(video_clf, 'models/video_classifier_trained.pkl')
    print("Saved: models/video_classifier_trained.pkl")
    
    print("\n" + "="*60)
    print("TRAINING AUDIO CLASSIFIER")
    print("="*60)
    
    audio_clf = SVC(kernel='rbf', probability=True, C=1.0, gamma='scale')
    audio_clf.fit(X_a_train, y_a_train)
    
    y_a_pred = audio_clf.predict(X_a_test)
    print(f"\nAudio Accuracy: {accuracy_score(y_a_test, y_a_pred):.2%}")
    print(classification_report(y_a_test, y_a_pred, target_names=['Fake', 'Real']))
    
    joblib.dump(audio_clf, 'models/audio_classifier_trained.pkl')
    print("Saved: models/audio_classifier_trained.pkl")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    train_models()