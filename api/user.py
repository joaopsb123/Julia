from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime
import os

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_id = self.path.split('/')[-1]
        
        try:
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            user = db['users'].find_one({'user_id': user_id})
            
            if user:
                user['_id'] = str(user['_id'])
                if user.get('last_daily'):
                    if isinstance(user['last_daily'], datetime):
                        user['last_daily'] = user['last_daily'].isoformat()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(user).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
