from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import json
from datetime import datetime
import traceback 
from backend_pipeline import HCISPipeline
try:
    import torch
    import transformers
    import librosa
    import moviepy.editor as mp
    import cv2
except ImportError:
    print("⚠️ Heavy ML libraries not loaded (Render free mode).")

# ---------- INIT ----------
app = Flask(__name__)

# CORS configuration
CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:3000",
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
        json.dump(data, f, indent=2)

def get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.mp4', '.avi', '.mov', '.mkv']:
        return 'video'
    elif ext in ['.mp3', '.wav']:
        return 'audio'
    elif ext in ['.txt']:
        return 'text'
    return 'unsupported'

def read_text_file_robust(file_path):
    """Attempts to read text file using utf-8, falls back to latin-1 on error."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        print(f"⚠️ Warning: UTF-8 failed for {file_path}. Falling back to latin-1.")
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

# ---------------------------------------------------------------------
# ---------- ANALYSIS ROUTE -------------------------------------------
# ---------------------------------------------------------------------

@app.route('/api/analyze', methods=['POST'])
def unified_analyze():
    print("\n--- INCOMING ANALYSIS REQUEST ---")
    print(f"Files: {dict(request.files)}")
    print("---------------------------------\n")

    if 'file' not in request.files:
        return jsonify({"detail": "No file part found in the request."}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    file_type = get_file_type(filename)
    
    if file_type == 'unsupported':
        return jsonify({"detail": f"Unsupported file type: {os.path.splitext(filename)[1]}"}), 400

    primary_upload_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(primary_upload_path)
    
    optional_upload_path = None

    try:
        video_results, audio_results, text_results = None, None, None
        
        # Analyze primary file
        if file_type == 'video':
            video_results = pipeline.analyze_video(primary_upload_path) 
            audio_results = pipeline.analyze_audio(primary_upload_path, is_video=True)
            
        elif file_type == 'audio':
            audio_results = pipeline.analyze_audio(primary_upload_path, is_video=False) 
        
        elif file_type == 'text':
            text_content = read_text_file_robust(primary_upload_path)
            text_results = pipeline.analyze_text(text_content)
        
        # Analyze optional text file if present
        if 'optional_text_file' in request.files:
            optional_file = request.files['optional_text_file']
            optional_filename = secure_filename(optional_file.filename)
            optional_upload_path = os.path.join(UPLOAD_FOLDER, optional_filename)
            optional_file.save(optional_upload_path)
            text_content = read_text_file_robust(optional_upload_path)
            text_results = pipeline.analyze_text(text_content)
            
        # Fuse results
        fusion_results = pipeline.fusion_engine.fuse(video_results, audio_results, text_results)
        
        # Get chatbot explanation
        chatbot_response_text = pipeline.chatbot.explain_results(fusion_results)
        
        # Compile final report
        final_report = {
            "id": int(datetime.now().timestamp() * 1000), 
            "timestamp": datetime.now().isoformat(),
            "fileName": filename,
            "fileType": file_type,
            "fusion_score": fusion_results.get('fusion_score', 0),
            "video_score": fusion_results.get('video_score', 0),
            "audio_score": fusion_results.get('audio_score', 0),
            "text_score": fusion_results.get('text_score', 0),
            "active_modalities": fusion_results.get('active_modalities', []),
            "chatbot_explanation": chatbot_response_text,
            "message": "Analysis Complete",
        }

        # Save to history
        history = read_history()
        history.insert(0, final_report)
        write_history(history)
        
        return jsonify({"status": "success", "results": final_report}), 200

    except Exception as e:
        print(f"\n--- BACKEND ANALYSIS ERROR ---")
        traceback.print_exc()
        return jsonify({"detail": f"Internal server error: {str(e)}"}), 500
    
    finally:
        if os.path.exists(primary_upload_path): 
            os.remove(primary_upload_path)
        if optional_upload_path and os.path.exists(optional_upload_path): 
            os.remove(optional_upload_path)


# ---------------------------------------------------------------------
# ---------- CHAT ROUTE -----------------------------------------------
# ---------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Handles chat from Detector or Chatbot page"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        context = data.get('context', {})
        
        response = pipeline.chatbot.chat(question, context_results=context)
        
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        print(f"❌ CHAT ERROR: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------
# ---------- GENERATOR ROUTES -----------------------------------------
# ---------------------------------------------------------------------

@app.route("/api/generate/voice", methods=["POST"])
def api_generate_voice():
    """Voice cloning: ALWAYS outputs VIDEO with synthetic audio"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    reference_file = request.files['file']
    text_script = request.form.get('target_text', '') 

    if not text_script:
        return jsonify({"error": "No text script provided"}), 400

    filename = secure_filename(reference_file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    reference_file.save(upload_path)
    
    try:
        result = pipeline.generator.generate_synthetic_speech(upload_path, text_script)
        
        if result['success']:
            output_filename = os.path.basename(result['output_path'])
            # ALWAYS video output now
            web_path = f"/generated/video/{output_filename}"
            
            return jsonify({
                "success": True, 
                "message": "Voice clone video generated successfully",
                "generated_path": web_path,
                "type": "voice_clone_video"
            })
        else:
            return jsonify({"error": result.get('error', 'Generation failed')}), 500
            
    except Exception as e:
        print(f"❌ Voice generation error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)


@app.route("/api/generate/faceswap", methods=["POST"])
def api_generate_faceswap():
    """Face swap: ALWAYS outputs VIDEO with full target length"""
    if 'source_video' not in request.files or 'target_video' not in request.files:
        return jsonify({"error": "Both videos required"}), 400

    source_file = request.files['source_video']
    target_file = request.files['target_video']
    
    source_filename = secure_filename(source_file.filename)
    target_filename = secure_filename(target_file.filename)
    
    source_path = os.path.join(UPLOAD_FOLDER, source_filename)
    target_path = os.path.join(UPLOAD_FOLDER, target_filename)
    
    source_file.save(source_path)
    target_file.save(target_path)
    
    try:
        result = pipeline.generator.face_swap(source_path, target_path)
        
        if result['success']:
            output_filename = os.path.basename(result['output_path'])
            web_path = f"/generated/video/{output_filename}"
            
            return jsonify({
                "success": True,
                "message": "Face swap video completed successfully",
                "generated_path": web_path,
                "type": "face_swap_video",
                "frames_processed": result.get('frames_processed', 0),
                "duration": result.get('duration', 'unknown')
            })
        else:
            return jsonify({"error": result.get('error', 'Face swap failed')}), 500
            
    except Exception as e:
        print(f"❌ Face swap error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(source_path):
            os.remove(source_path)
        if os.path.exists(target_path):
            os.remove(target_path)


# ---------------------------------------------------------------------
# ---------- FILE SERVING ---------------------------------------------
# ---------------------------------------------------------------------

@app.route('/generated/<path:subdir>/<path:filename>', methods=['GET'])
def serve_generated_file(subdir, filename):
    """Serve generated video/audio files"""
    try:
        full_path = os.path.join('data', 'generated', subdir)
        print(f"📁 Serving: {full_path}/{filename}")
        return send_from_directory(full_path, filename)
    except Exception as e:
        print(f"❌ Error serving {subdir}/{filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404


@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------------------------------------------------------------
# ---------- HISTORY ROUTES -------------------------------------------
# ---------------------------------------------------------------------

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(read_history())

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history(item_id):
    history = [h for h in read_history() if h.get('id') != item_id]
    write_history(history)
    return jsonify({'msg': 'deleted'})


# ---------- MAIN ----------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)