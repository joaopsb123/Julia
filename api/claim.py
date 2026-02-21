from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import db
from datetime import datetime
import os

FIREBASE_CONFIG = {
    "databaseURL": "https://bot-discord-4d74d-default-rtdb.firebaseio.com/",
    "projectId": "bot-discord-4d74d"
}
DAILY_AMOUNT = 100

if not firebase_admin._apps:
    firebase_admin.initialize_app(options=FIREBASE_CONFIG)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            user_id = self.path.split('/')[-1]
            username = data.get('username', '')
            
            user_ref = db.reference(f'/users/{user_id}')
            user = user_ref.get()
            now = datetime.now()
            
            if not user:
                user_data = {
                    'username': username,
                    'balance': 0,
                    'last_daily': None,
                    'total_earned': 0,
                    'daily_streak': 0,
                    'created_at': now.isoformat()
                }
                user_ref.set(user_data)
                user = user_data
            
            # Verificar se já resgatou hoje
            if user.get('last_daily'):
                last = datetime.fromisoformat(user['last_daily'])
                time_diff = now - last
                if time_diff.total_seconds() < 86400:
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': '⏰ Já resgatou hoje!'
                    }).encode())
                    return
            
            # Calcular streak
            if user.get('last_daily'):
                last = datetime.fromisoformat(user['last_daily'])
                hours_since = (now - last).total_seconds() / 3600
                if hours_since < 48:
                    streak = user.get('daily_streak', 0) + 1
                else:
                    streak = 1
            else:
                streak = 1
            
            # Calcular bônus
            bonus = 1.0 + (min(streak, 7) * 0.1)
            amount = int(DAILY_AMOUNT * bonus)
            
            # Atualizar
            user_ref.update({
                'balance': user.get('balance', 0) + amount,
                'last_daily': now.isoformat(),
                'daily_streak': streak,
                'total_earned': user.get('total_earned', 0) + amount,
                'username': username
            })
            
            self.wfile.write(json.dumps({
                'success': True,
                'amount': amount,
                'streak': streak,
                'message': f'🎉 Ganhou {amount} moedas! Streak: {streak}'
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
