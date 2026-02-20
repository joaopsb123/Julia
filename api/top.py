from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
import os

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            users = list(db['users'].find(
                {'username': {'$ne': None}},
                {'username': 1, 'balance': 1, '_id': 0}
            ).sort('balance', -1).limit(10))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(users).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
