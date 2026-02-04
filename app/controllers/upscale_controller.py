"""
Upscale Controller
Handles HTTP requests for image upscaling operations
"""

from flask import request, jsonify, send_from_directory, current_app, g
from app.services.upscale_service import UpscaleService
from app.decorators import api_key_required


@api_key_required
def upscale_image():
    """
    Endpoint untuk upscale image
    
    POST /api/v1/upscale/process
    Headers: X-API-KEY atau x-api-key
    Body (multipart/form-data):
        - image: File gambar (required)
        - scale: 2, 4, atau 8 (default: 2)
        - mode: auto, photo, face, anime, logo (default: auto)
    """
    # 1. Validasi File
    if 'image' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image uploaded"
        }), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No selected file"
        }), 400

    if not UpscaleService.allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "File type not allowed. Allowed: png, jpg, jpeg"
        }), 400

    # 2. Ambil Parameter
    try:
        scale = int(request.form.get('scale', 2))
        mode = request.form.get('mode', 'auto').lower()
        
        # Validate mode
        valid_modes = ['auto', 'photo', 'face', 'anime', 'logo']
        if mode not in valid_modes:
            mode = 'auto'
            
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid scale parameter. Allowed: 2, 4, 8"
        }), 400

    # 3. Log request info
    user = g.get('user')
    if user:
        current_app.logger.info(f"Upscale request from user: {user.email}")
    
    # 4. Process Upscale
    try:
        result = UpscaleService.process_upscale(
            file_storage=file,
            mode=mode,
            scale=scale
        )
        
        return jsonify({
            "status": "success",
            "message": "Image upscaled successfully",
            "data": {
                "result_url": f"/api/v1/upscale/download/{result['result']}",
                "original_file": result['original'],
                "meta": {
                    "scale": result['scale_used'],
                    "mode": result['mode_used']
                }
            }
        }), 200
        
    except ValueError as e:
        current_app.logger.warning(f"Upscale validation error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Upscale error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


@api_key_required
def download_upscaled_file(filename):
    """
    Download file hasil upscale
    
    GET /api/v1/upscale/download/<filename>
    Headers: X-API-KEY atau x-api-key
    """
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(upload_folder, filename)
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "File not found"
        }), 404


def get_upscale_models():
    """
    Get available upscale models/modes (public endpoint)
    
    GET /api/v1/upscale/models
    """
    models = [
        {
            "id": "auto",
            "name": "Auto Detect",
            "description": "Otomatis mendeteksi tipe gambar",
            "recommended": True
        },
        {
            "id": "photo",
            "name": "Photo Enhancement",
            "description": "Untuk foto real-world dengan Real-ESRGAN",
            "recommended": True
        },
        {
            "id": "face",
            "name": "Face Enhancement",
            "description": "Untuk foto wajah dengan GFPGAN",
            "recommended": False
        },
        {
            "id": "anime",
            "name": "Anime Upscale",
            "description": "Untuk gambar anime/ilustrasi",
            "recommended": False
        },
        {
            "id": "logo",
            "name": "Logo/Icon Upscale",
            "description": "Untuk logo dan icon",
            "recommended": False
        }
    ]
    
    scales = [
        {"value": 2, "label": "2x", "description": "Double resolution"},
        {"value": 4, "label": "4x", "description": "Quadruple resolution"},
        {"value": 8, "label": "8x", "description": "8x resolution (slow)"}
    ]
    
    return jsonify({
        "status": "success",
        "data": {
            "models": models,
            "scales": scales
        }
    }), 200