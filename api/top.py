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
            # Buscar todos os usuários do Firebase
            url = "https://bot-discord-4d74d-default-rtdb.firebaseio.com/users.json"
            response = urllib.request.urlopen(url)
            data = response.read().decode()
            users_data = json.loads(data) if data != 'null' else {}
            
            users_list = []
            for user_id, user in users_data.items():
                if user and user.get('username'):
                    users_list.append({
                        'username': user['username'],
                        'balance': user.get('balance', 0)
                    })
            
            # Ordenar por saldo
            users_list.sort(key=lambda x: x['balance'], reverse=True)
            
            self.wfile.write(json.dumps(users_list[:10]).encode())
            
        except Exception as e:
            self.wfile.write(json.dumps([]).encode())
