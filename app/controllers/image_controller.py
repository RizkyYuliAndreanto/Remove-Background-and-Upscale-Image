from flask import request, jsonify, send_from_directory, current_app, g
from app.decorators.security import api_key_required
from app.services.image_service import ImageService
from app. extensions import db


@api_key_required
def remove_background():
    """
    Remove background from uploaded image
    
    Query/Form params:
        type:  'auto' (default), 'logo', 'photo'
    """
    
    # Check if user has remaining quota
    if not g.current_user. has_quota_remaining():
        return jsonify({
            "status": "error",
            "message": "Monthly quota exceeded. Please upgrade to premium.",
            "quota_info": {
                "used":  g.current_user.usage_count,
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
    if not ImageService. allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "File type not allowed. Allowed: jpg, jpeg, png, gif, webp"
        }), 400
    
    # Get image type from request (query param or form data)
    # Options: 'auto', 'logo', 'photo'
    image_type = request.args.get('type') or request.form.get('type', 'auto')
    
    # Validate image_type
    valid_types = ['auto', 'logo', 'photo', 'human', 'portrait']
    if image_type not in valid_types: 
        image_type = 'auto'
    
    try:
        # Process image with specified type
        result = ImageService. process_image(file, image_type=image_type)
        
        # Increment usage count (quota management)
        g.current_user.increment_usage()
        db.session.commit()
        
        current_app.logger.info(
            f"Background removed for user:  {g.current_user.email}, "
            f"type: {image_type}, file: {result['original']}"
        )
        
        return jsonify({
            "status": "success",
            "message": "Background removed successfully",
            "data": {
                "result_url": f"/api/v1/images/download/{result['result']}",
                "original_file": result['original'],
                "type_used": result. get('type_used', image_type),
                "quota_info": {
                    "used": g.current_user.usage_count,
                    "remaining": g.current_user.monthly_quota - g.current_user.usage_count,
                    "limit": g.current_user.monthly_quota
                }
            }
        }), 200
        
    except ValueError as e:
        current_app.logger.warning(f"Image processing ValueError: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e: 
        current_app.logger. error(f"Image processing error:  {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Internal server error.  Please try again."
        }), 500


@api_key_required
def remove_background_logo():
    """Shortcut endpoint untuk logo processing"""
    
    if not g.current_user.has_quota_remaining():
        return jsonify({
            "status":  "error",
            "message":  "Monthly quota exceeded."
        }), 429
    
    if 'image' not in request. files:
        return jsonify({
            "status": "error",
            "message": "No image file provided"
        }), 400
    
    file = request.files['image']
    
    if not ImageService.allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "File type not allowed"
        }), 400
    
    try:
        result = ImageService.process_logo(file)
        g.current_user.increment_usage()
        db.session.commit()
        
        return jsonify({
            "status":  "success",
            "message":  "Logo background removed successfully",
            "data":  {
                "result_url":  f"/api/v1/images/download/{result['result']}",
                "original_file":  result['original']
            }
        }), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e: 
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_key_required
def remove_background_photo():
    """Shortcut endpoint untuk photo processing"""
    
    if not g.current_user.has_quota_remaining():
        return jsonify({
            "status":  "error",
            "message":  "Monthly quota exceeded."
        }), 429
    
    if 'image' not in request. files:
        return jsonify({
            "status": "error",
            "message": "No image file provided"
        }), 400
    
    file = request.files['image']
    
    if not ImageService.allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "File type not allowed"
        }), 400
    
    try:
        result = ImageService.process_photo(file)
        g.current_user. increment_usage()
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Photo background removed successfully",
            "data": {
                "result_url": f"/api/v1/images/download/{result['result']}",
                "original_file": result['original']
            }
        }), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e: 
        return jsonify({"status":  "error", "message": "Internal server error"}), 500


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