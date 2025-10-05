from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from backend_pipeline import HCISPipeline 

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Initialize pipeline
pipeline = HCISPipeline() 

# Create upload folder
UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- ROUTES ---------- #

@app.route('/')
def home():
    return jsonify({"message": "HCIS Backend Running 🚀"}), 200


# --- Video Deepfake Detection ---
@app.route("/analyze/video", methods=["POST"])
def analyze_video():
    """Video deepfake detection endpoint"""
    try:
        # Check if file is present
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video']
        
        if video_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Save uploaded file
        upload_path = os.path.join("data", "uploads", video_file.filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        video_file.save(upload_path)
        
        # Analyze video
        result = pipeline.analyze_video(upload_path)
        
        # Clean up uploaded file (optional)
        # os.remove(upload_path)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Audio Deepfake Detection ---
@app.route("/analyze/audio", methods=["POST"])
def analyze_audio():
    """Audio deepfake detection endpoint"""
    try:
        # Check if file is present
        if 'audio' not in request.files and 'video' not in request.files:
            return jsonify({"error": "No audio or video file provided"}), 400
        
        # Accept either audio file or video file
        if 'video' in request.files:
            file = request.files['video']
            is_video = True
        else:
            file = request.files['audio']
            is_video = False
        
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Save uploaded file
        upload_path = os.path.join("data", "uploads", file.filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        
        # Analyze audio
        result = pipeline.analyze_audio(upload_path, is_video=is_video)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Text Fact-Checking ---
@app.route("/analyze/text", methods=["POST"])
def analyze_text():
    """Text fact-checking endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({"error": "No text provided"}), 400
        
        result = pipeline.analyze_text(text)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# --- Fusion Engine ---
@app.route("/analyze/complete", methods=["POST"])
def analyze_complete():
    """Complete HCIS analysis - all components + fusion"""
    try:
        # Check for video file and text
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        data = request.form
        transcript = data.get('transcript', '')
        
        if not transcript.strip():
            return jsonify({"error": "No transcript provided"}), 400
        
        video_file = request.files['video']
        
        # Save video
        upload_path = os.path.join("data", "uploads", video_file.filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        video_file.save(upload_path)
        
        # Complete analysis
        result = pipeline.analyze_complete(upload_path, transcript)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- CHATBOT------#
@app.route("/chat/explain", methods=["POST"])
def chat_explain():
    """Chatbot explains HCIS results"""
    try:
        data = request.get_json()
        
        # Get analysis results
        results = data.get('results', {})
        question = data.get('question', None)
        
        if not results:
            return jsonify({"error": "No analysis results provided"}), 400
        
        # Generate explanation
        explanation = pipeline.chatbot.explain_results(results, question)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

#----generator------#
@app.route("/generate/speech", methods=["POST"])
def generate_speech():
    """Generate synthetic speech for testing"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        result = pipeline.generator.generate_synthetic_speech(text, language)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate/false-claim", methods=["POST"])
def generate_false_claim():
    """Generate false text claim for testing"""
    try:
        data = request.get_json()
        claim_type = data.get('type', 'factual')
        
        result = pipeline.generator.generate_false_text(claim_type)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ---------- MAIN ---------- #
if __name__ == '__main__':
    app.run(debug=True)
