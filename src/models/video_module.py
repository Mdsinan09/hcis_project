import cv2
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.video_helpers import extract_video_frames, preprocess_frame, calculate_frame_quality


class VideoDeepfakeDetector:
    """
    Main class for video deepfake detection
    """
    
    def __init__(self):
        # Load Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Error: Could not load face cascade")
        else:
            print("✅ Face detector loaded successfully")
    
    def detect_faces_in_frame(self, frame):
        """
        Detect faces in a single frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            List of face coordinates
        """
        try:
            # Convert to grayscale
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return faces
        
        except Exception as e:
            print(f"❌ Error detecting faces: {str(e)}")
            return []
    
    def analyze_face_consistency(self, frames):
        """
        Analyze face detection consistency across frames
        
        Args:
            frames: List of video frames
            
        Returns:
            Consistency score (0-1)
        """
        face_counts = []
        face_sizes = []
        
        for frame in frames:
            faces = self.detect_faces_in_frame(frame)
            face_counts.append(len(faces))
            
            if len(faces) > 0:
                # Get largest face
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                face_sizes.append(largest_face[2] * largest_face[3])
        
        if not face_counts:
            return 0.0
        
        # Calculate consistency metrics
        detection_rate = sum(1 for count in face_counts if count > 0) / len(face_counts)
        
        if face_sizes:
            size_variance = np.var(face_sizes) / (np.mean(face_sizes) + 1e-6)
            size_consistency = max(0, 1 - size_variance / 1000)
        else:
            size_consistency = 0
        
        # Combined consistency score
        consistency = (detection_rate * 0.7 + size_consistency * 0.3)
        
        return consistency
    
    def detect_artifacts(self, frames):
        """
        Detect deepfake artifacts in frames
        
        Args:
            frames: List of video frames
            
        Returns:
            Artifact score (0-1, higher = more artifacts/suspicious)
        """
        quality_scores = []
        edge_scores = []
        
        for frame in frames:
            # Calculate quality metrics
            quality = calculate_frame_quality(frame)
            quality_scores.append(quality['overall_quality'])
            
            # Edge detection analysis
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            edge_scores.append(edge_density)
        
        # Analyze patterns
        avg_quality = np.mean(quality_scores)
        quality_variance = np.var(quality_scores)
        avg_edges = np.mean(edge_scores)
        
        # Suspicious patterns:
        # - Very high quality variance (inconsistent processing)
        # - Unusually smooth (over-processed)
        # - Edge irregularities
        
        artifact_score = 0
        
        # High variance in quality = suspicious
        if quality_variance > 0.05:
            artifact_score += 0.3
        
        # Too smooth or too sharp = suspicious
        if avg_quality > 0.95 or avg_quality < 0.3:
            artifact_score += 0.2
        
        # Unnatural edge patterns
        if avg_edges < 0.05 or avg_edges > 0.3:
            artifact_score += 0.2
        
        return min(artifact_score, 1.0)
    
    def analyze_video(self, video_path):
        """
        Complete video analysis pipeline
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n🎥 Starting video analysis: {video_path}")
        
        # Extract frames
        frames = extract_video_frames(video_path, max_frames=50)
        
        if not frames:
            return {
                'success': False,
                'error': 'Could not extract frames from video',
                'video_score': 0,
                'confidence': 0
            }
        
        print(f"📊 Analyzing {len(frames)} frames...")
        
        # Preprocess frames
        processed_frames = []
        for frame in frames:
            processed = preprocess_frame(frame)
            if processed:
                processed_frames.append(processed['color'])
        
        # Run detection analyses
        face_consistency = self.analyze_face_consistency(processed_frames)
        artifact_score = self.detect_artifacts(processed_frames)
        
        # Calculate overall quality
        quality_scores = [calculate_frame_quality(f)['overall_quality'] for f in processed_frames]
        avg_quality = np.mean(quality_scores)
        
        # Calculate final video authenticity score
        # Higher score = more likely to be real
        authenticity_score = (
            face_consistency * 0.4 +           # 40% weight on face consistency
            avg_quality * 0.3 +                # 30% weight on quality
            (1 - artifact_score) * 0.3         # 30% weight on lack of artifacts
        )
        
        # Convert to percentage
        video_score = authenticity_score * 100
        
        # Determine confidence based on number of frames analyzed
        confidence = min(len(processed_frames) / 50 * 100, 100)
        
        print(f"✅ Analysis complete!")
        print(f"   Video Score: {video_score:.1f}%")
        print(f"   Confidence: {confidence:.1f}%")
        
        return {
            'success': True,
            'video_score': round(video_score, 2),
            'confidence': round(confidence, 2),
            'details': {
                'face_consistency': round(face_consistency * 100, 2),
                'artifact_detection': round(artifact_score * 100, 2),
                'average_quality': round(avg_quality * 100, 2),
                'frames_analyzed': len(processed_frames)
            }
        }


# Test the module
if __name__ == "__main__":
    detector = VideoDeepfakeDetector()
    print("✅ Video Deepfake Detector initialized successfully!")
    print("📝 Ready to analyze videos")