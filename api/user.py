from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/bot_saldo?retryWrites=true&w=majority"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            user_id = self.path.split('/')[-1]
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            user = db['users'].find_one({'user_id': user_id})
            
            if user:
                user['_id'] = str(user['_id'])
                if user.get('last_daily'):
                    user['last_daily'] = str(user['last_daily'])
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
