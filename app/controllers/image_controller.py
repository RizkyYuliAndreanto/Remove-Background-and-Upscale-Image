from flask import request, jsonify, send_from_directory, current_app, g
from app.decorators.security import api_key_required
from app.services.image_service import ImageService
from app.extensions import db

@api_key_required
def remove_background():
    """Remove background from uploaded image"""
    
    # Check if user has remaining quota
    if not g.current_user.has_quota_remaining():
        return jsonify({
            "status": "error",
            "message": "Monthly quota exceeded. Please upgrade to premium.",
            "quota_info": {
                "used": g.current_user.usage_count,
                "limit": g.current_user.monthly_quota
            }
        }), 429
    
    # Validate file presence
    if 'image' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No image file provided"
        }), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No selected file"
        }), 400
    
    # Check file type
    if not ImageService.allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "File type not allowed. Allowed: jpg, jpeg, png"
        }), 400
    
    try:
        # Process image
        result = ImageService.process_image(file)
        
        # Increment usage count (quota management)
        g.current_user.increment_usage()
        db.session.commit()
        
        current_app.logger.info(f"Background removed for user: {g.current_user.email}")
        
        return jsonify({
            "status": "success",
            "message": "Background removed successfully",
            "data": {
                "result_url": f"/api/v1/images/download/{result['result']}",
                "original_file": result['original'],
                "quota_info": {
                    "used": g.current_user.usage_count,
                    "remaining": g.current_user.monthly_quota - g.current_user.usage_count,
                    "limit": g.current_user.monthly_quota
                }
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Image processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


def download_file(filename):
    """Download processed image file"""
    try:
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'], 
            filename, 
            as_attachment=True
        )
    except FileNotFoundError:
        return jsonify({
            "status": "error",
            "message": "File not found"
        }), 404