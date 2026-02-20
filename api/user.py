from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime
import sys
import os

# Adicionar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Headers CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Pegar user_id da URL
            parts = self.path.split('/')
            user_id = parts[-1] if parts else ''
            
            if not user_id:
                self.wfile.write(json.dumps({'error': 'ID não fornecido'}).encode())
                return
            
            # Conectar MongoDB
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            users = db['users']
            
            # Buscar usuário
            user = users.find_one({'user_id': user_id})
            
            if user:
                # Converter ObjectId para string
                user['_id'] = str(user['_id'])
                
                # Converter datetime para string ISO
                if user.get('last_daily') and isinstance(user['last_daily'], datetime):
                    user['last_daily'] = user['last_daily'].isoformat()
                if user.get('created_at') and isinstance(user['created_at'], datetime):
                    user['created_at'] = user['created_at'].isoformat()
                
                self.wfile.write(json.dumps(user).encode())
            else:
                self.wfile.write(json.dumps(None).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
