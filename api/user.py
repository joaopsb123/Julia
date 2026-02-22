from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import credentials, db
import os

# Configuração do Firebase (via variáveis de ambiente)
FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API_KEY", "AIzaSyDJ_FRnNVJYOPbKUQZpx43WgYmqA-u-CB0"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", "bot-discord-4d74d.firebaseapp.com"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", "https://bot-discord-4d74d-default-rtdb.firebaseio.com"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", "bot-discord-4d74d")
}

# Inicializar Firebase
if not firebase_admin._apps:
    firebase_admin.initialize_app(options=FIREBASE_CONFIG)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Pegar ID da URL (ex: /api/user/123)
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            path_parts = parsed.path.split('/')
            user_id = path_parts[-1] if len(path_parts) > 1 else None
            
            if not user_id:
                self.wfile.write(json.dumps({"error": "ID não fornecido"}).encode())
                return
            
            # Buscar no Firebase
            ref = db.reference(f'users/{user_id}')
            user_data = ref.get()
            
            if user_data:
                self.wfile.write(json.dumps(user_data).encode())
            else:
                self.wfile.write(json.dumps({
                    "user_id": user_id,
                    "username": "",
                    "balance": 0,
                    "last_daily": None,
                    "total_earned": 0,
                    "daily_streak": 0
                }).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
