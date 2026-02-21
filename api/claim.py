from http.server import BaseHTTPRequestHandler
import json
import urllib.request
from datetime import datetime
import urllib.parse

DAILY_AMOUNT = 100

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
            
            # Buscar usuário no Firebase
            url = f"https://bot-discord-4d74d-default-rtdb.firebaseio.com/users/{user_id}.json"
            response = urllib.request.urlopen(url)
            user_data = response.read().decode()
            user = json.loads(user_data) if user_data != 'null' else None
            
            now = datetime.now()
            
            if not user:
                # Criar novo usuário
                user = {
                    'username': username,
                    'balance': 0,
                    'last_daily': None,
                    'total_earned': 0,
                    'daily_streak': 0,
                    'created_at': now.isoformat()
                }
            
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
                streak = user.get('daily_streak', 0) + 1 if hours_since < 48 else 1
            else:
                streak = 1
            
            # Calcular bônus
            bonus = 1.0 + (min(streak, 7) * 0.1)
            amount = int(DAILY_AMOUNT * bonus)
            
            # Atualizar dados
            user['balance'] = user.get('balance', 0) + amount
            user['last_daily'] = now.isoformat()
            user['daily_streak'] = streak
            user['total_earned'] = user.get('total_earned', 0) + amount
            user['username'] = username
            
            # Salvar no Firebase (usando PUT/POST)
            data = json.dumps(user).encode()
            req = urllib.request.Request(url, data=data, method='PUT')
            req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(req)
            
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
