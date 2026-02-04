"""
Upscale Routes
Routes untuk image upscaling API
"""

from flask import Blueprint
from app.controllers.upscale_controller import (
    upscale_image,
    download_upscaled_file,
    get_upscale_models
)

upscale_bp = Blueprint('upscale', __name__)

# POST /api/v1/upscale/process
# Menerima: image (file), scale (int: 2,4,8), mode (str: auto,photo,face,anime,logo)
upscale_bp.route('/process', methods=['POST'])(upscale_image)

# GET /api/v1/upscale/download/<filename>
# Download hasil upscale
upscale_bp.route('/download/<filename>', methods=['GET'])(download_upscaled_file)

# GET /api/v1/upscale/models
# Get available models dan scales
upscale_bp.route('/models', methods=['GET'])(get_upscale_models)