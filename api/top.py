from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
import sys

sys.stdout.reconfigure(encoding='utf-8')

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Headers CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Conectar MongoDB
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            
            # Buscar top 10
            users = list(db['users'].find(
                {'username': {'$ne': None, '$ne': ''}},
                {'username': 1, 'balance': 1, '_id': 0}
            ).sort('balance', -1).limit(10))
            
            self.wfile.write(json.dumps(users).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
