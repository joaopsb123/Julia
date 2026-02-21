from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Buscar todos os usuários
            firebase_url = "https://bot-discord-4d74d-default-rtdb.firebaseio.com/"
            
            req = urllib.request.Request(firebase_url)
            req.add_header('Content-Type', 'application/json')
            
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode()
            
            if not data or data == 'null':
                self.wfile.write(json.dumps([]).encode())
                return
            
            users_data = json.loads(data)
            
            # Converter para lista
            users_list = []
            for user_id, user in users_data.items():
                if user and user.get('username'):
                    users_list.append({
                        'username': user['username'],
                        'balance': user.get('balance', 0)
                    })
            
            # Ordenar por saldo (maior para menor)
            users_list.sort(key=lambda x: x['balance'], reverse=True)
            
            # Limitar a 10
            self.wfile.write(json.dumps(users_list[:10]).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
