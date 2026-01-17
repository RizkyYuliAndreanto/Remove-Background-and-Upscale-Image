from flask import Blueprint
from app.controllers.image_controller import remove_background, download_file


image_bp = Blueprint('images', __name__)


image_bp.route('/remove-bg', methods=['POST'])(remove_background)


image_bp.route('/download/<filename>', methods=['GET'])(download_file)