import requests
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class ImageService:
    """
    Service untuk background removal dengan multiple endpoint: 
    - /process      : Auto-detect (logo vs photo)
    - /process/logo : Force logo mode (color-based removal)
    - /process/photo:  Force photo mode (BiRefNet AI)
    """
    
    @staticmethod
    def get_base_url():
        """Get base ngrok URL from config"""
        return current_app. config. get('NGROK_URL', '').rstrip('/')
    
    @staticmethod
    def get_endpoint_url(image_type='auto'):
        """
        Get API endpoint URL based on image type
        
        Args:
            image_type: 'auto', 'logo', 'photo', 'human'
        """
        base_url = ImageService.get_base_url()
        
        endpoints = {
            'auto': f"{base_url}/process",
            'logo': f"{base_url}/process/logo",
            'photo': f"{base_url}/process/photo",
            'human': f"{base_url}/process/photo",  # human = photo
            'portrait': f"{base_url}/process/photo",
        }
        
        return endpoints. get(image_type, endpoints['auto'])
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        return ext in allowed

    @staticmethod
    def process_image(file_storage, image_type='auto'):
        """
        Process image dengan Kaggle AI Server
        
        Args:
            file_storage: FileStorage object dari Flask request
            image_type: 
                - 'auto'  : Auto-detect (recommended)
                - 'logo'  : Force logo mode - untuk logo, icon, grafik dengan BG solid
                - 'photo' :  Force photo mode - untuk foto manusia/objek
                - 'human' :  Alias untuk photo
        
        Returns:
            dict: {
                "original": original filename,
                "result": output filename,
                "path": full path to output file,
                "type_used": image_type yang digunakan
            }
        """
        # Validate
        if not file_storage or not file_storage.filename:
            raise ValueError("No file provided")
        
        # Setup filenames
        original_filename = secure_filename(file_storage.filename)
        unique_id = uuid.uuid4().hex
        filename_output = f"{unique_id}_no_bg.png"
        
        # Setup output folder
        upload_folder = current_app.config. get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        output_path = os.path. join(upload_folder, filename_output)
        
        # Get API URL based on type
        api_url = ImageService.get_endpoint_url(image_type)
        
        print(f"🚀 Processing image...")
        print(f"   📁 Original: {original_filename}")
        print(f"   🎯 Type: {image_type}")
        print(f"   🌐 Endpoint: {api_url}")
        
        try:
            # Reset stream position
            file_storage.stream.seek(0)
            
            # Prepare request
            files = {
                'image': (original_filename, file_storage.stream, file_storage.mimetype)
            }
            
            headers = {
                'ngrok-skip-browser-warning': 'true',
                'User-Agent': 'BackgroundRemoverAPI/2.0'
            }
            
            # Send request (timeout 120s untuk gambar besar)
            response = requests.post(
                api_url, 
                files=files, 
                headers=headers, 
                timeout=120
            )
            
            # Handle response
            if response.status_code == 200:
                # Success - save result
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ Success!  Saved to: {filename_output}")
                
                return {
                    "original": original_filename,
                    "result": filename_output,
                    "path": output_path,
                    "type_used":  image_type
                }
            else:
                # Error from server
                error_msg = response. text
                print(f"   ❌ Server Error (Status {response.status_code})")
                
                # Check specific errors
                if response.status_code == 502 or "ngrok" in error_msg. lower():
                    raise ValueError(
                        "Ngrok tunnel offline!  Restart Kaggle notebook dan update NGROK_URL."
                    )
                elif response.status_code == 500:
                    raise ValueError(f"AI Processing Error: {error_msg[: 200]}")
                else:
                    raise ValueError(f"Server Error {response.status_code}: {error_msg[: 200]}")

        except requests.exceptions.Timeout:
            print("   ❌ Timeout!")
            raise ValueError(
                "Processing timeout (>120s). "
                "Coba dengan gambar lebih kecil atau gunakan endpoint /process/logo untuk logo."
            )
        
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection Error:  {e}")
            raise ValueError(
                "Tidak bisa connect ke Kaggle server. "
                "Pastikan:\n"
                "1. Kaggle notebook sedang running\n"
                "2. NGROK_URL di . env sudah benar\n"
                "3. Ngrok tunnel masih aktif"
            )
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise ValueError(f"Processing failed: {str(e)}")

    # =========================================
    # CONVENIENCE METHODS
    # =========================================
    
    @staticmethod
    def process_logo(file_storage):
        """
        Shortcut untuk process logo
        Gunakan untuk:  logo, icon, grafik dengan background solid
        """
        return ImageService.process_image(file_storage, image_type='logo')
    
    @staticmethod
    def process_photo(file_storage):
        """
        Shortcut untuk process foto
        Gunakan untuk: foto manusia, portrait, foto produk
        """
        return ImageService.process_image(file_storage, image_type='photo')
    
    @staticmethod
    def process_auto(file_storage):
        """
        Shortcut untuk auto-detect
        Server akan otomatis mendeteksi apakah logo atau foto
        """
        return ImageService.process_image(file_storage, image_type='auto')