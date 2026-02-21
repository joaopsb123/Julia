from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import db
import os

# Configuração do Firebase (sem credenciais complexas)
FIREBASE_CONFIG = {
    "databaseURL": "https://bot-discord-4d74d-default-rtdb.firebaseio.com/",
    "projectId": "bot-discord-4d74d"
}

# Inicializar Firebase (uma vez só)
if not firebase_admin._apps:
    firebase_admin.initialize_app(options=FIREBASE_CONFIG)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            user_id = self.path.split('/')[-1]
            user_ref = db.reference(f'/users/{user_id}')
            user = user_ref.get()
            
            if user:
                self.wfile.write(json.dumps(user).encode())
            else:
                self.wfile.write(json.dumps({
                    'user_id': user_id,
                    'username': '',
                    'balance': 0,
                    'daily_streak': 0,
                    'total_earned': 0
                }).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
