import os
import cv2
import numpy as np
from gtts import gTTS
import json
from datetime import datetime
import subprocess


class EducationalDeepfakeGenerator:
    """
    Generate synthetic content for testing HCIS detection capabilities
    Educational and research purposes only
    
    Features:
    1. Voice Cloning (Text-to-Speech)
    2. Face Swap (2 videos -> swap faces)
    3. Image-to-Video (Image + text prompt -> animated video)
    """
    
    def __init__(self):
        self.output_dir = "data/generated"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/video", exist_ok=True)
        os.makedirs(f"{self.output_dir}/audio", exist_ok=True)
        os.makedirs(f"{self.output_dir}/text", exist_ok=True)
        
        self.generation_log = []
        
        print("✅ Educational Deepfake Generator initialized")
        print("⚠️  Generated content is for testing purposes only")
    
    # ========== FEATURE 1: VOICE CLONING ==========
    def generate_synthetic_speech(self, reference_video_path, text_script, output_path=None):
        """
        Generate synthetic speech and ALWAYS create VIDEO output
    
    Args:
        reference_video_path: Path to video/audio file
        text_script: Text to synthesize
        output_path: Where to save OUTPUT VIDEO (always .mp4)
        
    Returns:
        Result dictionary with output_path (always .mp4 video)
    """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
            print(f"🎙️  Generating voice clone from text: '{text_script[:50]}...'")
        
        # Generate synthetic speech first
            temp_audio = f"{self.output_dir}/audio/temp_speech_{timestamp}.mp3"
            tts = gTTS(text=text_script, lang='en', slow=False)
            tts.save(temp_audio)
            print(f"   ✅ Synthetic speech audio created")
        
        # ALWAYS output as VIDEO (.mp4)
            if output_path is None:
                output_path = f"{self.output_dir}/video/voice_clone_{timestamp}.mp4"
        
        # Ensure output is .mp4
            if not output_path.endswith('.mp4'):
                output_path = output_path.replace(os.path.splitext(output_path)[1], '.mp4')
        
        # Check if input is video or audio
            file_ext = os.path.splitext(reference_video_path)[1].lower()
        
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            # Input is VIDEO - replace audio track
                print("   📹 Input is video - replacing audio track...")
            
                try:
                    import subprocess
                
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-i', reference_video_path,  # Input video
                        '-i', temp_audio,            # Input audio
                        '-c:v', 'copy',              # Copy video stream
                        '-map', '0:v:0',             # Use video from first input
                        '-map', '1:a:0',             # Use audio from second input
                        '-shortest',                 # Stop at shortest stream
                        output_path
                    ], check=True, capture_output=True, text=True)
                
                    print(f"   ✅ Video with synthetic audio created: {output_path}")
                
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  FFmpeg error: {e.stderr}")
                    raise ValueError(f"FFmpeg failed: {e.stderr}")
                
            else:
            # Input is AUDIO - create black screen video with audio
                print("   🎵 Input is audio - creating video with audio...")
            
                try:
                    import subprocess
                
                # Get audio duration
                    result = subprocess.run([
                        'ffprobe', '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        temp_audio
                    ], capture_output=True, text=True, check=True)
                
                    duration = float(result.stdout.strip())
                
                # Create video with black screen and audio
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-f', 'lavfi', '-i', f'color=c=black:s=1280x720:d={duration}',
                        '-i', temp_audio,
                        '-c:v', 'libx264', '-c:a', 'aac',
                        '-shortest',
                        output_path
                    ], check=True, capture_output=True, text=True)
                
                    print(f"   ✅ Video with synthetic audio created: {output_path}")
                
                except Exception as e:
                    print(f"   ⚠️  Could not create video: {e}")
                    raise ValueError(f"Failed to create video from audio: {e}")
        
        # Clean up temp audio
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        
        # Log generation
            self._log_generation('voice_clone', {
                'reference': reference_video_path,
                'text': text_script,
                'output': output_path
            })
        
            print(f"✅ Voice clone VIDEO generated: {output_path}")
        
            return {
                'success': True,
                'output_path': output_path,
                'type': 'voice_clone_video',
                'method': 'google_tts_with_video',
                'warning': '⚠️  This is synthetic audio for testing only'
            }
        
        except Exception as e:
            print(f"❌ Voice clone error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    # ========== FEATURE 2: FACE SWAP ==========
    def face_swap(self, source_video_path, target_video_path, output_path=None):
        """
        Swap faces between two videos
        Extracts face from source and replaces faces in FULL target video
        
        Args:
            source_video_path: Video with face to extract
            target_video_path: Video to put the face into (FULL LENGTH preserved)
            output_path: Where to save result
            
        Returns:
            Result dictionary
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{self.output_dir}/video/face_swap_{timestamp}.mp4"
            
            print(f"🎭 Starting face swap...")
            print(f"   Source: {source_video_path}")
            print(f"   Target: {target_video_path}")
            
            # Load face detector
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Open both videos
            cap_source = cv2.VideoCapture(source_video_path)
            cap_target = cv2.VideoCapture(target_video_path)
            
            # Get video properties from TARGET (preserve target video length)
            fps = int(cap_target.get(cv2.CAP_PROP_FPS))
            width = int(cap_target.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap_target.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_target_frames = int(cap_target.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"   Target video: {total_target_frames} frames at {fps} FPS")
            print(f"   Duration: {total_target_frames/fps:.2f} seconds")
            
            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Extract a reference face from source video (use first detected face)
            print("   📸 Extracting reference face from source...")
            source_face_template = None
            source_frame_idx = 0
            
            while source_frame_idx < 30:  # Check first 30 frames of source
                ret_source, frame_source = cap_source.read()
                if not ret_source:
                    break
                    
                gray_source = cv2.cvtColor(frame_source, cv2.COLOR_BGR2GRAY)
                faces_source = face_cascade.detectMultiScale(gray_source, 1.3, 5)
                
                if len(faces_source) > 0:
                    (x_s, y_s, w_s, h_s) = faces_source[0]
                    source_face_template = frame_source[y_s:y_s+h_s, x_s:x_s+w_s].copy()
                    print(f"   ✅ Reference face extracted from source frame {source_frame_idx}")
                    break
                    
                source_frame_idx += 1
            
            if source_face_template is None:
                raise ValueError("No face detected in source video")
            
            # Now process the ENTIRE target video
            print("   🔄 Processing target video frames...")
            frame_count = 0
            
            while True:
                ret_target, frame_target = cap_target.read()
                
                if not ret_target:
                    break
                
                # Detect faces in target frame
                gray_target = cv2.cvtColor(frame_target, cv2.COLOR_BGR2GRAY)
                faces_target = face_cascade.detectMultiScale(gray_target, 1.3, 5)
                
                # Replace face in target with source face
                if len(faces_target) > 0:
                    (x_t, y_t, w_t, h_t) = faces_target[0]
                    
                    # Resize source face to match target face size
                    source_face_resized = cv2.resize(source_face_template, (w_t, h_t))
                    
                    # Blending for smoother transition
                    alpha = 0.85  # Source face weight
                    target_face = frame_target[y_t:y_t+h_t, x_t:x_t+w_t]
                    
                    try:
                        blended = cv2.addWeighted(source_face_resized, alpha, target_face, 1-alpha, 0)
                        frame_target[y_t:y_t+h_t, x_t:x_t+w_t] = blended
                    except:
                        # If blending fails, just paste the face directly
                        frame_target[y_t:y_t+h_t, x_t:x_t+w_t] = source_face_resized
                
                out.write(frame_target)
                frame_count += 1
                
                # Progress indicator
                if frame_count % 30 == 0:
                    print(f"   Processed {frame_count}/{total_target_frames} frames ({frame_count/total_target_frames*100:.1f}%)")
            
            cap_source.release()
            cap_target.release()
            out.release()
            
            print(f"   ✅ Processed {frame_count} frames total")
            
            # CRITICAL FIX: Use libx264 codec for better compatibility
            print("   🔊 Adding audio from target video...")
            try:
                import subprocess
                temp_video = output_path.replace('.mp4', '_no_audio.mp4')
                os.rename(output_path, temp_video)
                
                # Re-encode with proper codecs for web compatibility
                subprocess.run([
                    'ffmpeg', '-y',
                    '-i', temp_video,           # Video without audio
                    '-i', target_video_path,    # Original target with audio
                    '-c:v', 'libx264',          # Re-encode video with h264
                    '-preset', 'fast',          # Faster encoding
                    '-crf', '23',               # Quality (lower = better)
                    '-c:a', 'aac',              # AAC audio codec
                    '-b:a', '128k',             # Audio bitrate
                    '-map', '0:v:0',            # Video from processed
                    '-map', '1:a:0?',           # Audio from target (optional)
                    '-shortest',                # Match shortest stream
                    output_path
                ], check=True, capture_output=True, text=True)
                
                os.remove(temp_video)
                print("   ✅ Audio added successfully")
                
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  FFmpeg error: {e.stderr}")
                print(f"   ⚠️  Continuing without audio...")
                # If ffmpeg fails, use video without audio
                if os.path.exists(temp_video):
                    os.rename(temp_video, output_path)
            except Exception as e:
                print(f"   ⚠️  Could not add audio: {e}")
                if os.path.exists(temp_video):
                    os.rename(temp_video, output_path)
            
            self._log_generation('face_swap', {
                'source_video': source_video_path,
                'target_video': target_video_path,
                'output': output_path,
                'frames_processed': frame_count,
                'duration_seconds': frame_count / fps
            })
            
            print(f"✅ Face swap completed: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'type': 'face_swap',
                'frames_processed': frame_count,
                'duration': f"{frame_count/fps:.2f}s",
                'warning': '⚠️  This is manipulated video for testing only'
            }
            
        except Exception as e:
            print(f"❌ Face swap error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    # ========== FEATURE 3: IMAGE TO VIDEO ==========
    def image_to_video(self, image_path, text_prompt, output_path=None, duration=5):
        """
        Animate a static image into a video
        Creates zoom/pan effects based on text prompt
        
        Args:
            image_path: Path to input image
            text_prompt: Description of desired animation
            output_path: Where to save video
            duration: Video duration in seconds
            
        Returns:
            Result dictionary
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{self.output_dir}/video/image_to_video_{timestamp}.mp4"
            
            print(f"🖼️  Animating image to video...")
            print(f"   Image: {image_path}")
            print(f"   Prompt: {text_prompt}")
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")
            
            height, width = img.shape[:2]
            fps = 30
            total_frames = duration * fps
            
            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Determine animation type from prompt
            prompt_lower = text_prompt.lower()
            
            if 'zoom' in prompt_lower or 'closer' in prompt_lower:
                animation_type = 'zoom_in'
            elif 'pan' in prompt_lower or 'move' in prompt_lower:
                animation_type = 'pan'
            elif 'rotate' in prompt_lower or 'spin' in prompt_lower:
                animation_type = 'rotate'
            else:
                animation_type = 'zoom_in'  # Default
            
            print(f"   Animation type: {animation_type}")
            
            # Generate frames with animation
            for i in range(total_frames):
                progress = i / total_frames
                
                if animation_type == 'zoom_in':
                    # Zoom in effect
                    scale = 1.0 + progress * 0.3  # Zoom to 1.3x
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    
                    # Resize and center crop
                    resized = cv2.resize(img, (new_width, new_height))
                    x_offset = (new_width - width) // 2
                    y_offset = (new_height - height) // 2
                    frame = resized[y_offset:y_offset+height, x_offset:x_offset+width]
                
                elif animation_type == 'pan':
                    # Pan from left to right
                    # Create larger canvas
                    canvas_width = int(width * 1.2)
                    canvas = cv2.resize(img, (canvas_width, height))
                    
                    # Pan offset
                    pan_offset = int((canvas_width - width) * progress)
                    frame = canvas[:, pan_offset:pan_offset+width]
                
                elif animation_type == 'rotate':
                    # Rotate effect
                    angle = progress * 10  # Rotate 10 degrees
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    frame = cv2.warpAffine(img, rotation_matrix, (width, height))
                
                else:
                    frame = img.copy()
                
                out.write(frame)
            
            out.release()
            
            # Add audio narration using the text prompt
            audio_path = f"{self.output_dir}/audio/temp_narration.mp3"
            tts = gTTS(text=text_prompt, lang='en')
            tts.save(audio_path)
            
            # Combine video with audio using ffmpeg
            temp_output = output_path.replace('.mp4', '_temp.mp4')
            os.rename(output_path, temp_output)
            
            try:
                subprocess.run([
                    'ffmpeg', '-i', temp_output, '-i', audio_path,
                    '-c:v', 'copy', '-c:a', 'aac', '-shortest',
                    output_path
                ], check=True, capture_output=True)
                
                os.remove(temp_output)
                os.remove(audio_path)
            except:
                # If ffmpeg fails, just use video without audio
                os.rename(temp_output, output_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            
            self._log_generation('image_to_video', {
                'image': image_path,
                'prompt': text_prompt,
                'animation': animation_type,
                'output': output_path,
                'duration': duration
            })
            
            print(f"✅ Image-to-video completed: {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'type': 'image_to_video',
                'animation': animation_type,
                'duration': duration,
                'warning': '⚠️  This is generated video for testing only'
            }
            
        except Exception as e:
            print(f"❌ Image-to-video error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _log_generation(self, generation_type, details):
        """Log all generations"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': generation_type,
            'details': details,
            'purpose': 'educational_testing'
        }
        
        self.generation_log.append(log_entry)
        
        log_file = f"{self.output_dir}/generation_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.generation_log, f, indent=2)
    
    def get_generation_stats(self):
        """Get generation statistics"""
        return {
            'total_generated': len(self.generation_log),
            'by_type': {
                'voice_clone': sum(1 for x in self.generation_log if x['type'] == 'voice_clone'),
                'face_swap': sum(1 for x in self.generation_log if x['type'] == 'face_swap'),
                'image_to_video': sum(1 for x in self.generation_log if x['type'] == 'image_to_video'),
            },
            'output_directory': self.output_dir
        }


# Test module
if __name__ == "__main__":
    generator = EducationalDeepfakeGenerator()
    
    print("\n" + "="*60)
    print("TEST 1: Voice Clone")
    print("="*60)
    result1 = generator.generate_synthetic_speech(
        "dummy_audio.mp3",  # Reference (not actually used with gTTS)
        "Hello, this is a test of voice cloning technology."
    )
    print(f"Result: {result1}")
    
    print("\n" + "="*60)
    print("Generation Stats:")
    print("="*60)
    stats = generator.get_generation_stats()
    print(json.dumps(stats, indent=2))