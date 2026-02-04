from flask import Blueprint
from app.controllers.image_controller import (
    remove_background,
    remove_background_logo,
    remove_background_photo,
    download_file
)

image_bp = Blueprint('images', __name__)

# Main endpoint - auto-detect atau dengan ? type=logo/photo
image_bp.route('/remove-bg', methods=['POST'])(remove_background)

# Shortcut endpoints untuk force mode
image_bp.route('/remove-bg/logo', methods=['POST'])(remove_background_logo)
image_bp.route('/remove-bg/photo', methods=['POST'])(remove_background_photo)

# Download hasil
image_bp.route('/download/<filename>', methods=['GET'])(download_file)