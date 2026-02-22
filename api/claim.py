from http.server import BaseHTTPRequestHandler
import json
import firebase_admin
from firebase_admin import db
from datetime import datetime
import os

FIREBASE_CONFIG = {
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL", "https://bot-discord-4d74d-default-rtdb.firebaseio.com"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", "bot-discord-4d74d")
}

if not firebase_admin._apps:
    firebase_admin.initialize_app(options=FIREBASE_CONFIG)

DAILY_AMOUNT = 100

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Ler body da requisição
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            user_id = data.get('userId')
            username = data.get('username', '')
            
            if not user_id:
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "ID não fornecido"
                }).encode())
                return
            
            # Buscar usuário no Firebase
            ref = db.reference(f'users/{user_id}')
            user = ref.get()
            now = datetime.now()
            
            if not user:
                user = {
                    "user_id": user_id,
                    "username": username or "Usuário",
                    "balance": 0,
                    "last_daily": None,
                    "total_earned": 0,
                    "daily_streak": 0
                }
            
            # Verificar se já resgatou hoje
            if user.get('last_daily'):
                last = datetime.fromisoformat(user['last_daily'])
                diff = (now - last).total_seconds()
                if diff < 86400:
                    self.wfile.write(json.dumps({
                        "success": False,
                        "message": "⏰ Você já resgatou hoje!"
                    }).encode())
                    return
            
            # Calcular streak
            streak = 1
            if user.get('last_daily'):
                last = datetime.fromisoformat(user['last_daily'])
                hours = (now - last).total_seconds() / 3600
                streak = user.get('daily_streak', 0) + 1 if hours < 48 else 1
            
            # Calcular bônus
            bonus = 1 + (min(streak, 7) * 0.1)
            amount = int(DAILY_AMOUNT * bonus)
            
            # Atualizar usuário
            user['balance'] = user.get('balance', 0) + amount
            user['last_daily'] = now.isoformat()
            user['daily_streak'] = streak
            user['total_earned'] = user.get('total_earned', 0) + amount
            user['username'] = username or user.get('username', 'Usuário')
            
            # Salvar no Firebase
            ref.set(user)
            
            self.wfile.write(json.dumps({
                "success": True,
                "amount": amount,
                "streak": streak,
                "message": f"🎉 Ganhou {amount} moedas! Streak: {streak}"
            }).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
