from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from backend_pipeline import HCISPipeline # Assuming this import is correct

# ---------- INIT ----------
app = Flask(__name__)
# 📢 Ensure CORS allows POST requests to /api/* from the React port
CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:3000",
    # 📢 MUST explicitly allow the OPTIONS preflight method
    "methods": ["GET", "POST", "DELETE", "OPTIONS"], 
    "allow_headers": ["Content-Type"]
}})
pipeline = HCISPipeline()

UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- HISTORY HELPERS ----------
HISTORY_FILE = 'history.json'

def read_history():
    return json.load(open(HISTORY_FILE)) if os.path.exists(HISTORY_FILE) else []

def write_history(data):
    with open(HISTORY_FILE, 'w') as f:
        # Use ISO format for date/time strings when serializing
        json.dump(data, f, indent=2)

# Helper to determine file type
def get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.mp4', '.avi', '.mov', '.mkv']:
        return 'video'
    elif ext in ['.mp3', '.wav']:
        return 'audio'
    elif ext in ['.txt']:
        return 'text'
    return 'unsupported'

# ---------------------------------------------------------------------
# ---------- UNIFIED ANALYSIS & HISTORY ROUTES (CRITICAL FIX) ---------
# ---------------------------------------------------------------------

# --- ENHANCED UNIFIED ANALYSIS ROUTE FOR DEBUGGING ---
@app.route('/api/analyze', methods=['POST'])
def unified_analyze():
    # ADD THESE DEBUG LINES AT THE VERY TOP
    print("\n" + "="*50)
    print("🔍 REQUEST RECEIVED!")
    print(f"Content-Type: {request.content_type}")
    print(f"Method: {request.method}")
    print(f"Form data: {dict(request.form)}")
    print(f"Files: {dict(request.files)}")
    print(f"Headers: {dict(request.headers)}")
    print("="*50 + "\n")

    # --- START DEBUG LOGGING ---
    print("\n--- INCOMING ANALYSIS REQUEST ---")
    print(f"Request Form Keys: {list(request.form.keys())}")
    print(f"Request File Keys: {list(request.files.keys())}")
    print("---------------------------------\n")
    # --- END DEBUG LOGGING ---

    if 'file' not in request.files:
        # Check if the frontend accidentally used the 'video' key
        if 'video' in request.files:
             return jsonify({"error": "File uploaded with key 'video'. Please ensure frontend uses key 'file'."}), 400
        
        # If no file found, return the 400 error
        return jsonify({"error": "No file part found in the request. Check FormData key in React."}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_type = get_file_type(filename)
    
    if file_type == 'unsupported':
        return jsonify({"error": f"Unsupported file type: {os.path.splitext(filename)[1]}. Supported: mp4, mp3, txt"}), 400

    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(upload_path)

    try:
        # 1. Run Analysis based on file type
        if file_type == 'video':
            # For video files, analyze both video AND audio
            video_results = pipeline.analyze_video(upload_path) 
            audio_results = pipeline.analyze_audio(upload_path, is_video=True)
            text_results = None  # No text in video file
        
        elif file_type == 'audio':
            # For audio-only files
            video_results = None
            audio_results = pipeline.analyze_audio(upload_path, is_video=False) 
            text_results = None
        
        elif file_type == 'text':
        # For text files
            video_results = None
            audio_results = None
            with open(upload_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            text_results = pipeline.analyze_text(text_content)
    
    # 2. Fuse the results (fusion engine will ignore None/0 scores)
        fusion_results = pipeline.fusion_engine.fuse(video_results, audio_results, text_results)
    
    # 3. Get Chatbot Explanation
        chatbot_response = pipeline.chatbot.explain_results(fusion_results)
    
    # 4. Compile the final report object
        final_report = {
            "id": int(datetime.now().timestamp() * 1000), 
            "uploadDate": datetime.now().isoformat(),
            "fileName": filename,
            "fileType": file_type,
            "fusion_score": fusion_results.get('fusion_score', 0),
            "video_score": fusion_results.get('video_score', 0),
            "audio_score": fusion_results.get('audio_score', 0),
            "text_score": fusion_results.get('text_score', 0),
            "active_modalities": fusion_results.get('active_modalities', []),
            "chatbot_explanation": chatbot_response if isinstance(chatbot_response, str) else str(chatbot_response),
            "message": "Analysis Complete",
            "download_path": f"/uploads/{filename}" 
        }

        # 4. Save to history (Assuming history helpers are correctly defined)
        history = read_history()
        history.insert(0, final_report)
        write_history(history)
        
        # 5. Return the full report
        return jsonify({"status": "success", "results": final_report}), 200

    except Exception as e:
        print(f"\n--- BACKEND ANALYSIS ERROR (500) ---")
        import traceback
        traceback.print_exc()
        print(f"----------------------------------\n")
        return jsonify({"detail": f"Internal server error: {str(e)}"}), 500
    
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)

# ---------------------------------------------------------------------
# ---------- CHAT & GENERATOR ROUTES (Modified for Simplicity) --------
# ---------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """General chat endpoint, can be used after analysis or standalone."""
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context', {}) # Optional: Pass previous analysis results as context
        
        # Call chatbot without full analysis for general questions
        # Note: Depending on your pipeline, this may need adjustment.
        response = pipeline.chatbot.ask(question, context=context)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate/voice", methods=["POST"])
def api_generate_voice():
    """Handles the Generator page flow: Upload audio + target text."""
    if 'file' not in request.files:
        return jsonify({"error": "No reference audio file provided"}), 400

    reference_file = request.files['file']
    text_script = request.form.get('target_text', '') # Get text from form data

    if not text_script:
        return jsonify({"error": "No text script provided"}), 400

    filename = secure_filename(reference_file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    reference_file.save(upload_path)
    
    try:
        # This function generates new audio (result['audio_file_path'])
        result = pipeline.generator.generate_synthetic_speech(upload_path, text_script) 
        
        # Return a path or reference to the generated output
        return jsonify({
            "success": True, 
            "message": "Voice clone generated.",
            "generated_path": result.get('output_path') 
        })
    finally:
        # Clean up uploaded reference file
        if os.path.exists(upload_path):
            os.remove(upload_path)

# ---------------------------------------------------------------------
# ---------- HISTORY ROUTES (Cleaned up) ------------------------------
# ---------------------------------------------------------------------

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(read_history())

# Note: The add_history logic is now ONLY inside unified_analyze()

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history(item_id):
    history = [h for h in read_history() if h.get('id') != item_id]
    write_history(history)
    return jsonify({'msg': 'deleted'})

# ---------------------------------------------------------------------
# ---------- ASSET ROUTES (Unchanged) ---------------------------------
# ---------------------------------------------------------------------

@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------- MAIN ----------
if __name__ == '__main__':
    print("🚀 HCIS Backend Initialized. Running...")
    app.run(debug=True,port=8000, use_reloader=False)

# Serve React build (This section is for production deployment, keeping it separate)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join('build', path)):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')
