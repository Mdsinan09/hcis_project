import cv2
import numpy as np
import os

def extract_video_frames(video_path, max_frames=50):
    """
    Extract frames from video file
    
    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of frames as numpy arrays
    """
    frames = []
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Cannot open video {video_path}")
            return frames
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate step to get evenly distributed frames
        step = max(1, total_frames // max_frames)
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Only keep every 'step' frame
            if frame_count % step == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        print(f"✅ Extracted {len(frames)} frames from video")
        
    except Exception as e:
        print(f"❌ Error extracting frames: {str(e)}")
    
    return frames


def preprocess_frame(frame, target_size=(224, 224)):
    """
    Preprocess frame for analysis
    
    Args:
        frame: Input frame (numpy array)
        target_size: Target dimensions (width, height)
        
    Returns:
        Preprocessed frame
    """
    try:
        # Resize frame
        resized = cv2.resize(frame, target_size)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        return {
            'color': resized,
            'gray': gray
        }
    
    except Exception as e:
        print(f"❌ Error preprocessing frame: {str(e)}")
        return None


def calculate_frame_quality(frame):
    """
    Calculate quality metrics for a frame
    
    Args:
        frame: Input frame (numpy array)
        
    Returns:
        Dictionary with quality metrics
    """
    try:
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500, 1.0)  # Normalize
        
        # 2. Brightness
        brightness = np.mean(gray) / 255.0
        
        # 3. Contrast
        contrast = np.std(gray) / 128.0
        
        # 4. Overall quality score
        quality_score = (sharpness_score * 0.5 + 
                        (1 - abs(brightness - 0.5) * 2) * 0.3 + 
                        min(contrast, 1.0) * 0.2)
        
        return {
            'sharpness': sharpness_score,
            'brightness': brightness,
            'contrast': contrast,
            'overall_quality': quality_score
        }
    
    except Exception as e:
        print(f"❌ Error calculating quality: {str(e)}")
        return {
            'sharpness': 0,
            'brightness': 0,
            'contrast': 0,
            'overall_quality': 0
        }


def save_debug_frame(frame, output_path, frame_number):
    """
    Save frame for debugging purposes
    
    Args:
        frame: Frame to save
        output_path: Directory to save frame
        frame_number: Frame identifier
    """
    try:
        os.makedirs(output_path, exist_ok=True)
        filename = os.path.join(output_path, f"frame_{frame_number:04d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"💾 Saved debug frame: {filename}")
    
    except Exception as e:
        print(f"❌ Error saving debug frame: {str(e)}")