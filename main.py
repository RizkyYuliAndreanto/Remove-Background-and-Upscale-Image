from app import create_app
from config.config import Config

app = create_app()

if __name__ == '__main__':
    is_debug = str(Config.DEBUG).lower() in ['true', '1', 't']
    
    print(f"🚀 Server running at http://{Config.HOST}:{Config.PORT}")
    
    app.run(
        host=Config.HOST, 
        port=Config.PORT, 
        debug=is_debug
    )