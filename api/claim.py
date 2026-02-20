from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

MONGODB_URI = "mongodb+srv://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0.xdlwmli.mongodb.net/"
DAILY_AMOUNT = 100

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Headers CORS
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Pegar user_id da URL
            parts = self.path.split('/')
            user_id = parts[-1] if parts else ''
            
            # Ler body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            username = data.get('username', '')
            
            if not user_id:
                self.wfile.write(json.dumps({'success': False, 'message': 'ID não fornecido'}).encode())
                return
            
            # Conectar MongoDB
            client = MongoClient(MONGODB_URI)
            db = client['bot_saldo']
            users = db['users']
            
            # Buscar ou criar usuário
            user = users.find_one({'user_id': user_id})
            now = datetime.now()
            
            if not user:
                user_data = {
                    'user_id': user_id,
                    'username': username,
                    'balance': 0,
                    'last_daily': None,
                    'total_earned': 0,
                    'daily_streak': 0,
                    'created_at': now
                }
                users.insert_one(user_data)
                user = user_data
            
            # Verificar se já resgatou hoje
            if user.get('last_daily'):
                last = user['last_daily']
                if isinstance(last, str):
                    last = datetime.fromisoformat(last)
                
                time_diff = now - last
                if time_diff.total_seconds() < 86400:  # 24h
                    self.wfile.write(json.dumps({
                        'success': False,
                        'message': '⏰ Você já resgatou hoje!'
                    }).encode())
                    return
            
            # Calcular streak
            if user.get('last_daily'):
                last = user['last_daily']
                if isinstance(last, str):
                    last = datetime.fromisoformat(last)
                
                hours_since = (now - last).total_seconds() / 3600
                streak = user.get('daily_streak', 0) + 1 if hours_since < 48 else 1
            else:
                streak = 1
            
            # Calcular bônus
            bonus = 1.0 + (min(streak, 7) * 0.1)
            amount = int(DAILY_AMOUNT * bonus)
            
            # Atualizar usuário
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
            
            # Resposta
            self.wfile.write(json.dumps({
                'success': True,
                'amount': amount,
                'streak': streak,
                'message': f'🎉 Ganhou {amount} moedas! Streak: {streak}'
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                'success': False,
                'message': str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
