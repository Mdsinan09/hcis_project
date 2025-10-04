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
@app.route('/api/detect/audio', methods=['POST'])
def detect_audio():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No audio uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = {
        "component": "audio",
        "confidence": 0.65,
        "verdict": "fake"
    }
    return jsonify(result)


# --- Text Fact Checking ---
@app.route('/api/detect/text', methods=['POST'])
def detect_text():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = {
        "component": "text",
        "confidence": 0.90,
        "verdict": "real"
    }
    return jsonify(result)


# --- Fusion Engine ---
@app.route('/api/fusion', methods=['POST'])
def fusion_engine():
    data = request.get_json()
    video = data.get('video_conf', 0)
    audio = data.get('audio_conf', 0)
    text = data.get('text_conf', 0)

    overall = (video + audio + text) / 3
    verdict = "real" if overall > 0.5 else "fake"

    return jsonify({
        "final_confidence": round(overall, 2),
        "final_verdict": verdict
    })


# ---------- MAIN ---------- #
if __name__ == '__main__':
    app.run(debug=True)
