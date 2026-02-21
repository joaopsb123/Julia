from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            user_id = self.path.split('/')[-1]
            
            # Buscar direto do Firebase REST API
            url = f"https://bot-discord-4d74d-default-rtdb.firebaseio.com/users/{user_id}.json"
            response = urllib.request.urlopen(url)
            data = response.read().decode()
            
            if data and data != 'null':
                self.wfile.write(data.encode())
            else:
                # Usuário não existe, retorna vazio
                self.wfile.write(json.dumps({
                    'user_id': user_id,
                    'username': '',
                    'balance': 0,
                    'daily_streak': 0,
                    'total_earned': 0
                }).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
