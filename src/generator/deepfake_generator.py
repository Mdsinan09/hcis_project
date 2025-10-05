import os
import cv2
import numpy as np
from gtts import gTTS
import json
from datetime import datetime


class EducationalDeepfakeGenerator:
    """
    Generate synthetic content for testing HCIS detection capabilities
    Educational and research purposes only
    """
    
    def __init__(self):
        self.output_dir = "data/generated"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/video", exist_ok=True)
        os.makedirs(f"{self.output_dir}/audio", exist_ok=True)
        os.makedirs(f"{self.output_dir}/text", exist_ok=True)
        
        self.generation_log = []
        
        print("Educational Deepfake Generator initialized")
        print("⚠️  Generated content is for testing purposes only")
    
    def generate_synthetic_speech(self, text, language='en', output_path=None):
        """
        Generate synthetic speech using Google TTS
        
        Args:
            text: Text to synthesize
            language: Language code (en, es, fr, etc.)
            output_path: Where to save audio
            
        Returns:
            Result dictionary
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{self.output_dir}/audio/synthetic_speech_{timestamp}.mp3"
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)
            
            # Log generation
            self._log_generation('synthetic_speech', {
                'text': text,
                'language': language,
                'output': output_path
            })
            
            return {
                'success': True,
                'output_path': output_path,
                'type': 'synthetic_audio',
                'method': 'google_tts',
                'warning': '⚠️  This is synthetic audio for testing only'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_simple_face_blur(self, video_path, output_path=None):
        """
        Create simple face manipulation by adding blur artifacts
        
        Args:
            video_path: Original video
            output_path: Where to save modified video
            
        Returns:
            Result dictionary
        """
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{self.output_dir}/video/manipulated_video_{timestamp}.mp4"
            
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            frame_count = 0
            while cap.read()[0]:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                # Add blur to faces
                for (x, y, w, h) in faces:
                    face_region = frame[y:y+h, x:x+w]
                    blurred_face = cv2.GaussianBlur(face_region, (23, 23), 30)
                    frame[y:y+h, x:x+w] = blurred_face
                
                out.write(frame)
                frame_count += 1
                
                if frame_count >= 150:
                    break
            
            cap.release()
            out.release()
            
            self._log_generation('face_manipulation', {
                'original': video_path,
                'output': output_path,
                'frames_processed': frame_count
            })
            
            return {
                'success': True,
                'output_path': output_path,
                'type': 'manipulated_video',
                'warning': '⚠️  This is manipulated video for testing only'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_false_text(self, template_type='factual'):
        """
        Generate false text claims for testing
        
        Args:
            template_type: Type of false claim
            
        Returns:
            Result dictionary
        """
        false_claims = {
            'factual': [
                "The capital of France is Berlin",
                "Water boils at 50 degrees Celsius",
                "The Earth is flat",
                "Humans have 300 bones"
            ],
            'historical': [
                "World War II ended in 1950",
                "The Great Wall was built in 1800"
            ],
            'scientific': [
                "The speed of light is 100,000 km/s",
                "Gravity was discovered in 2000"
            ]
        }
        
        claims = false_claims.get(template_type, false_claims['factual'])
        selected_claim = np.random.choice(claims)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{self.output_dir}/text/false_claim_{timestamp}.txt"
        
        with open(output_path, 'w') as f:
            f.write(f"⚠️  SYNTHETIC FALSE CLAIM\n\n{selected_claim}")
        
        self._log_generation('false_text', {
            'claim': selected_claim,
            'type': template_type,
            'output': output_path
        })
        
        return {
            'success': True,
            'claim': selected_claim,
            'output_path': output_path,
            'type': 'false_claim',
            'warning': '⚠️  False claim for testing only'
        }
    
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
                'synthetic_speech': sum(1 for x in self.generation_log if x['type'] == 'synthetic_speech'),
                'face_manipulation': sum(1 for x in self.generation_log if x['type'] == 'face_manipulation'),
                'false_text': sum(1 for x in self.generation_log if x['type'] == 'false_text')
            },
            'output_directory': self.output_dir
        }


if __name__ == "__main__":
    generator = EducationalDeepfakeGenerator()
    
    # Test synthetic speech
    print("\nGenerating synthetic speech...")
    speech_result = generator.generate_synthetic_speech(
        "The capital of France is Berlin",
        language='en'
    )
    print(f"Speech result: {speech_result}")
    
    # Test false text
    print("\nGenerating false claim...")
    text_result = generator.generate_false_text('factual')
    print(f"Text result: {text_result}")
    
    # Stats
    stats = generator.get_generation_stats()
    print(f"\nGeneration stats: {stats}")