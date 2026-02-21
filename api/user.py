from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Configurar headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Pegar ID da URL
            user_id = self.path.split('/')[-1]
            if not user_id or user_id == 'user':
                self.wfile.write(json.dumps({'error': 'ID não fornecido'}).encode())
                return
            
            # URL direta do Firebase
            firebase_url = f"https://bot-discord-4d74d-default-rtdb.firebaseio.com/users/{user_id}.json"
            
            # Fazer requisição
            req = urllib.request.Request(firebase_url)
            req.add_header('Content-Type', 'application/json')
            
            response = urllib.request.urlopen(req, timeout=10)
            data = response.read().decode()
            
            if data and data != 'null':
                # Dados encontrados
                self.wfile.write(data.encode())
            else:
                # Usuário não existe - retorna estrutura vazia
                self.wfile.write(json.dumps({
                    'user_id': user_id,
                    'username': '',
                    'balance': 0,
                    'daily_streak': 0,
                    'total_earned': 0
                }).encode())
                
        except urllib.error.URLError as e:
            self.wfile.write(json.dumps({
                'error': f'Erro de conexão com Firebase: {str(e)}',
                'user_id': user_id
            }).encode())
        except Exception as e:
            self.wfile.write(json.dumps({
                'error': f'Erro inesperado: {str(e)}',
                'user_id': user_id
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
