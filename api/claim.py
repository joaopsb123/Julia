from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime
import os

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"
DAILY_AMOUNT = 100

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        user_id = self.path.split('/')[-1]
        username = data.get('username', '')
        
        try:
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            users = db['users']
            
            user = users.find_one({'user_id': user_id})
            now = datetime.now()
            
            if not user:
                users.insert_one({
                    'user_id': user_id,
                    'username': username,
                    'balance': 0,
                    'last_daily': None,
                    'total_earned': 0,
                    'daily_streak': 0,
                    'created_at': now
                })
                user = users.find_one({'user_id': user_id})
            
            if user.get('last_daily'):
                last = user['last_daily']
                if isinstance(last, str):
                    last = datetime.fromisoformat(last)
                time_diff = now - last
                if time_diff.total_seconds() < 86400:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': '⏰ Você já resgatou hoje!'
                    }).encode())
                    return
            
            if user.get('last_daily'):
                last = user['last_daily']
                if isinstance(last, str):
                    last = datetime.fromisoformat(last)
                hours_since = (now - last).total_seconds() / 3600
                streak = user.get('daily_streak', 0) + 1 if hours_since < 48 else 1
            else:
                streak = 1
            
            bonus = 1.0 + (min(streak, 7) * 0.1)
            amount = int(DAILY_AMOUNT * bonus)
            
            users.update_one(
                {'user_id': user_id},
                {
                    '$inc': {'balance': amount, 'total_earned': amount},
                    '$set': {
                        'last_daily': now,
                        'daily_streak': streak,
                        'username': username
                    }
                }
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'amount': amount,
                'streak': streak,
                'message': f'🎉 Ganhou {amount} moedas! Streak: {streak}'
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
