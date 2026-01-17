import os
import uuid
from PIL import Image
from rembg import remove
from werkzeug.utils import secure_filename
from flask import current_app


class ImageService:
    @staticmethod
    def allowed_file(filename):
        """Check if the file has an allowed extension"""
        return '.' in filename and \
                filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def process_image(file_storage):
        """Process image:remove background and save"""

        #setup file name
        original_filename = secure_filename(file_storage.filename)
        ext = original_filename.rsplit('.',1)[1].lower()
        unique_id = uuid.uuid4().hex

        # name file input and output
        filename_input = f"{unique_id}_original.{ext}"
        filename_output = f"{unique_id}_no_bg.png"

        #folde setup
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        #complete path
        input_path = os.path.join(upload_folder,filename_input)
        output_path = os.path.join(upload_folder,filename_output)

        #save temporary original file
        file_storage.save(input_path)

        #Ai remove background
        try:
            print("Starting background removal process...")

            input_image = Image.open(input_path)

            output_image = remove(input_image)

            output_image.save(output_path)

            print(f"Background removal completed. Saved to {output_path}")
            return {
                "original": filename_input,
                "result": filename_output,
                "path":output_path
            }
        except Exception as e:
            # Clean up input file in case of error
            if os.path.exists(input_path):
                os.remove(input_path)
            raise ValueError (f"Error processing image:{str(e)}")
