import os
import uuid
from PIL import Image
import numpy as np
from rembg import remove, new_session
from werkzeug.utils import secure_filename
from flask import current_app


class ImageService:
    # Use multiple sessions for different use cases
    _sessions = {}
    
    @staticmethod
    def get_session(model_name="isnet-general-use"):
        """Get or create rembg session with specified model
        
        Available models (best to use):
        - isnet-general-use: Best for logos, graphics, general objects (RECOMMENDED)
        - u2net: Good general purpose
        - birefnet-general: Newest, very accurate but slower
        - u2net_human_seg: Optimized for human portraits
        """
        if model_name not in ImageService._sessions:
            ImageService._sessions[model_name] = new_session(model_name)
        return ImageService._sessions[model_name]
    
    @staticmethod
    def optimize_image_size(image, max_dimension=2048):
        """Resize image if too large to prevent memory issues"""
        width, height = image.size
        
        # If image is small enough, return as-is
        if width <= max_dimension and height <= max_dimension:
            return image, False
        
        # Calculate resize ratio
        ratio = min(max_dimension / width, max_dimension / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        print(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
        
        # Use high-quality Lanczos resampling
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized, True
    
    @staticmethod
    def clean_alpha_edges(image, threshold=240):
        """Clean alpha channel edges - remove semi-transparent pixels for sharp edges"""
        img_array = np.array(image)
        
        if img_array.shape[2] == 4:
            alpha = img_array[:, :, 3]
            
            # Make alpha channel more binary - sharp edges like remove.bg
            # Pixels with alpha > threshold become fully opaque (255)
            # Pixels with alpha < (255 - threshold) become fully transparent (0)
            alpha = np.where(alpha > threshold, 255, alpha)
            alpha = np.where(alpha < (255 - threshold), 0, alpha)
            
            img_array[:, :, 3] = alpha
            
        return Image.fromarray(img_array)
    
    @staticmethod
    def remove_white_background(image, tolerance=250):
        """Remove white/near-white background pixels specifically"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            if img_array.shape[2] == 3:
                # RGB - add alpha channel
                alpha = np.ones((img_array.shape[0], img_array.shape[1]), dtype=np.uint8) * 255
                
                # Detect white pixels
                r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
                is_white = (r > tolerance) & (g > tolerance) & (b > tolerance)
                alpha[is_white] = 0
                
                # Create RGBA image
                rgba = np.dstack((img_array, alpha))
                return Image.fromarray(rgba)
            
            elif img_array.shape[2] == 4:
                # Already RGBA
                alpha = img_array[:, :, 3]
                r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
                
                # Detect white pixels and make them transparent
                is_white = (r > tolerance) & (g > tolerance) & (b > tolerance)
                alpha[is_white] = 0
                
                img_array[:, :, 3] = alpha
                return Image.fromarray(img_array)
        
        return image
    
    @staticmethod
    def allowed_file(filename):
        """Check if the file has an allowed extension"""
        return '.' in filename and \
                filename.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def process_image(file_storage):
        """Process image: remove background with professional quality"""

        #setup file name
        original_filename = secure_filename(file_storage.filename)
        ext = original_filename.rsplit('.',1)[1].lower()
        unique_id = uuid.uuid4().hex

        # name file input and output
        filename_input = f"{unique_id}_original.{ext}"
        filename_output = f"{unique_id}_no_bg.png"

        #folder setup
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        #complete path
        input_path = os.path.join(upload_folder, filename_input)
        output_path = os.path.join(upload_folder, filename_output)

        #save temporary original file
        file_storage.save(input_path)

        # Professional background removal (like remove.bg)
        try:
            print("Starting professional background removal...")

            # Load image
            input_image = Image.open(input_path)
            original_size = input_image.size
            print(f"Original image size: {original_size}, mode: {input_image.mode}")
            
            # Convert to RGB if necessary
            if input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
            
            # Step 1: Optimize image size to prevent memory issues
            input_image, was_resized = ImageService.optimize_image_size(input_image, max_dimension=2048)
            if was_resized:
                print(f"Image optimized to: {input_image.size}")
            
            # Step 2: Remove background using best model
            # Try birefnet first (newest, most accurate), fallback to u2net
            try:
                # birefnet-general is the newest and most accurate model
                session = ImageService.get_session("birefnet-general")
                print("Using BiRefNet model for highest quality removal")
                
                output_image = remove(
                    input_image,
                    session=session,
                    post_process_mask=True,
                    bgcolor=None
                )
                print("Background removal completed with BiRefNet")
                
            except Exception as e:
                print(f"BiRefNet failed: {str(e)}, trying u2net...")
                try:
                    session = ImageService.get_session("u2net")
                    output_image = remove(
                        input_image,
                        session=session,
                        post_process_mask=True,
                        bgcolor=None
                    )
                    print("Background removal with u2net completed")
                except Exception as e2:
                    print(f"U2Net also failed: {str(e2)}")
                    raise ValueError(f"Unable to process image: {str(e2)}")
            
            # Step 3: Save directly without additional processing
            # BiRefNet/U2Net already produces clean output
            
            # Step 4: Resize back to original size if it was resized
            if was_resized:
                try:
                    output_image = output_image.resize(original_size, Image.Resampling.LANCZOS)
                    print(f"Image resized back to original size: {original_size}")
                except Exception as e:
                    print(f"Resize back failed: {str(e)}")
            
            # Step 5: Save with high quality PNG
            output_image.save(output_path, 'PNG', optimize=True)

            print(f"Background removal completed. Saved to {output_path}")
            print(f"Final image size: {output_image.size}, mode: {output_image.mode}")
            
            return {
                "original": filename_input,
                "result": filename_output,
                "path": output_path
            }
            
        except Exception as e:
            print(f"Critical error in process_image: {str(e)}")
            import traceback
            traceback.print_exc()
            # Clean up input file in case of error
            if os.path.exists(input_path):
                os.remove(input_path)
            raise ValueError(f"Error processing image: {str(e)}")
