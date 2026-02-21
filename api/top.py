from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import db
import os

FIREBASE_CONFIG = {
    "databaseURL": "https://bot-discord-4d74d-default-rtdb.firebaseio.com/",
    "projectId": "bot-discord-4d74d"
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
            users_ref = db.reference('/users').get()
            if not users_ref:
                self.wfile.write(json.dumps([]).encode())
                return
            
            users_list = []
            for user_id, user_data in users_ref.items():
                if user_data and user_data.get('username'):
                    users_list.append({
                        'username': user_data['username'],
                        'balance': user_data.get('balance', 0)
                    })
            
            # Ordenar e limitar
            users_list.sort(key=lambda x: x['balance'], reverse=True)
            self.wfile.write(json.dumps(users_list[:10]).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
