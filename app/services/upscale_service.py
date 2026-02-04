"""
Upscale Service
Service untuk image upscaling dengan multiple model support via Kaggle/Ngrok
"""

import requests
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


class UpscaleService:
    """
    Service untuk image upscaling dengan multiple endpoint:
    - /upscale/auto  : Auto-detect mode
    - /upscale/photo : Photo enhancement
    - /upscale/face  : Face enhancement (GFPGAN)
    - /upscale/anime : Anime upscaling
    - /upscale/logo  : Logo/icon upscaling
    """
    
    @staticmethod
    def get_base_url():
        """Get base ngrok URL untuk upscale dari config"""
        return current_app.config.get('NGROK_UPSCALE_URL', '').rstrip('/')
    
    @staticmethod
    def get_endpoint_url(mode='auto'):
        """
        Get API endpoint URL based on mode
        
        Args:
            mode: 'auto', 'photo', 'face', 'anime', 'logo'
        """
        base_url = UpscaleService.get_base_url()
        
        if not base_url:
            raise ValueError("NGROK_UPSCALE_URL not configured in .env")
        
        # Note: 'auto' uses /upscale endpoint (not /upscale/auto)
        endpoints = {
            'auto': f"{base_url}/upscale",
            'photo': f"{base_url}/upscale/photo",
            'face': f"{base_url}/upscale/face",
            'anime': f"{base_url}/upscale/anime",
            'logo': f"{base_url}/upscale/logo",
        }
        
        return endpoints.get(mode, endpoints['auto'])
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
        return ext in allowed
    
    @staticmethod
    def process_upscale(file_storage, mode='auto', scale=2):
        """
        Process image upscale dengan Kaggle AI Server
        
        Args:
            file_storage: FileStorage object dari Flask request
            mode: 
                - 'auto'  : Auto-detect (recommended)
                - 'photo' : Photo enhancement dengan Real-ESRGAN
                - 'face'  : Face enhancement dengan GFPGAN
                - 'anime' : Anime upscaling dengan Real-ESRGAN Anime
                - 'logo'  : Logo/icon upscaling
            scale:
                - 2 : 2x upscale
                - 4 : 4x upscale
                - 8 : 8x upscale (optional)
        
        Returns:
            dict: {
                "original": original filename,
                "result": output filename,
                "path": full path to output file,
                "mode_used": mode yang digunakan,
                "scale_used": scale factor yang digunakan
            }
        """
        # Validate file
        if not file_storage or not file_storage.filename:
            raise ValueError("No file provided")
        
        # Validate scale
        scale = int(scale)
        if scale not in [2, 4, 8]:
            raise ValueError("Invalid scale value. Allowed: 2, 4, 8")
        
        # Validate mode
        valid_modes = ['auto', 'photo', 'face', 'anime', 'logo']
        if mode not in valid_modes:
            mode = 'auto'
        
        # Setup filenames
        original_filename = secure_filename(file_storage.filename)
        unique_id = uuid.uuid4().hex
        filename_output = f"{unique_id}_{mode}_{scale}x_upscaled"
        
        # Setup output folder
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        output_path = os.path.join(upload_folder, filename_output)
        
        # Get API URL
        api_url = UpscaleService.get_endpoint_url(mode)
        
        current_app.logger.info(f"🚀 Processing Upscale...")
        current_app.logger.info(f"   📁 File: {original_filename}")
        current_app.logger.info(f"   ⚙️ Config: {mode.upper()} | {scale}x")
        current_app.logger.info(f"   🌐 Endpoint: {api_url}")
        
        try:
            # Reset stream position
            file_storage.stream.seek(0)
            
            # Prepare request
            files = {
                'image': (original_filename, file_storage.stream, file_storage.mimetype)
            }
            
            data = {
                'scale': scale,
                'type': mode
            }
            
            headers = {
                'ngrok-skip-browser-warning': 'true',
                'User-Agent': 'UpscaleAPI/1.0'
            }
            
            # Send request (timeout 300s untuk gambar besar + upscaling)
            response = requests.post(
                api_url,
                files=files,
                data=data,
                headers=headers,
                timeout=300
            )
            
            # Handle response
            if response.status_code == 200:
                # Success - save result
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                current_app.logger.info(f"   ✅ Success! Saved to: {filename_output}")
                
                return {
                    "original": original_filename,
                    "result": filename_output,
                    "path": output_path,
                    "mode_used": mode,
                    "scale_used": scale
                }
            else:
                # Error from server
                error_msg = response.text
                current_app.logger.error(f"   ❌ Server Error (Status {response.status_code})")
                
                # Check specific errors
                if response.status_code == 502 or "ngrok" in error_msg.lower():
                    raise ValueError(
                        "Ngrok Upscale tunnel offline! Restart Kaggle notebook dan update NGROK_UPSCALE_URL."
                    )
                elif response.status_code == 500:
                    raise ValueError(f"AI Processing Error: {error_msg[:200]}")
                elif response.status_code == 400:
                    raise ValueError(f"Bad Request: {error_msg[:200]}")
                else:
                    raise ValueError(f"Server Error {response.status_code}: {error_msg[:200]}")
        
        except requests.exceptions.Timeout:
            current_app.logger.error("   ❌ Timeout!")
            raise ValueError(
                "Upscale timeout (>300s). "
                "Gambar terlalu besar atau GPU sedang sibuk. "
                "Coba dengan gambar lebih kecil atau scale factor lebih rendah."
            )
        
        except requests.exceptions.ConnectionError as e:
            current_app.logger.error(f"   ❌ Connection Error: {e}")
            raise ValueError(
                "Tidak bisa connect ke Kaggle upscale server. "
                "Pastikan:\n"
                "1. Kaggle notebook sedang running\n"
                "2. NGROK_UPSCALE_URL di .env sudah benar\n"
                "3. Ngrok tunnel masih aktif"
            )
        
        except ValueError:
            # Re-raise ValueError as is
            raise
        
        except Exception as e:
            current_app.logger.error(f"   ❌ Error: {e}")
            raise ValueError(f"Processing failed: {str(e)}")

    # =========================================
    # CONVENIENCE METHODS
    # =========================================
    
    @staticmethod
    def upscale_photo(file_storage, scale=2):
        """Shortcut untuk upscale foto"""
        return UpscaleService.process_upscale(file_storage, mode='photo', scale=scale)
    
    @staticmethod
    def upscale_face(file_storage, scale=2):
        """Shortcut untuk upscale face dengan GFPGAN"""
        return UpscaleService.process_upscale(file_storage, mode='face', scale=scale)
    
    @staticmethod
    def upscale_anime(file_storage, scale=2):
        """Shortcut untuk upscale anime"""
        return UpscaleService.process_upscale(file_storage, mode='anime', scale=scale)
    
    @staticmethod
    def upscale_logo(file_storage, scale=2):
        """Shortcut untuk upscale logo/icon"""
        return UpscaleService.process_upscale(file_storage, mode='logo', scale=scale)
    
    @staticmethod
    def upscale_auto(file_storage, scale=2):
        """Shortcut untuk auto-detect mode"""
        return UpscaleService.process_upscale(file_storage, mode='auto', scale=scale)


                    



