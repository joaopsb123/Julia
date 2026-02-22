from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import db
import os

FIREBASE_CONFIG = {
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", "https://bot-discord-4d74d-default-rtdb.firebaseio.com"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", "bot-discord-4d74d")
}

if not firebase_admin._apps:
    firebase_admin.initialize_app(options=FIREBASE_CONFIG)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Buscar todos os usuários
            ref = db.reference('users')
            users_data = ref.get()
            
            if not users_data:
                self.wfile.write(json.dumps([]).encode())
                return
            
            # Converter para lista
            users_list = []
            for user_id, user in users_data.items():
                if user and user.get('username'):
                    users_list.append({
                        'username': user['username'],
                        'balance': user.get('balance', 0)
                    })
            
            # Ordenar e pegar top 10
            users_list.sort(key=lambda x: x['balance'], reverse=True)
            top10 = users_list[:10]
            
            self.wfile.write(json.dumps(top10).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
