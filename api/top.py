from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/bot_saldo?retryWrites=true&w=majority"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            users = list(db['users'].find(
                {'username': {'$ne': None}},
                {'username': 1, 'balance': 1, '_id': 0}
            ).sort('balance', -1).limit(10))
            
            self.wfile.write(json.dumps(users).encode())
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
