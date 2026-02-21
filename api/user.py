from http.server import BaseHTTPRequestHandler
import json
from pymongo import MongoClient
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

MONGODB_URI = "mongodb://joaopsb6890_db_user:BcOi8oG5uQwcuLBl@cluster0-shard-00-00.xdlwmli.mongodb.net:27017,cluster0-shard-00-01.xdlwmli.mongodb.net:27017,cluster0-shard-00-02.xdlwmli.mongodb.net:27017/bot_saldo?ssl=true&replicaSet=atlas-14p8yr-shard-0&authSource=admin&retryWrites=true&w=majority"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Pegar ID da URL
            user_id = self.path.split('/')[-1]
            
            if not user_id:
                self.wfile.write(json.dumps({'error': 'ID não fornecido'}).encode())
                return
            
            # Conectar MongoDB
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            db = client['bot_saldo']
            
            # Buscar usuário
            user = db['users'].find_one({'user_id': user_id})
            
            if user:
                # Converter ObjectId para string
                user['_id'] = str(user['_id'])
                # Converter datetime para string
                if user.get('last_daily'):
                    user['last_daily'] = str(user['last_daily'])
                if user.get('created_at'):
                    user['created_at'] = str(user['created_at'])
                
                self.wfile.write(json.dumps(user).encode())
            else:
                # Se não existir, criar esqueleto básico
                novo_usuario = {
                    'user_id': user_id,
                    'username': '',
                    'balance': 0,
                    'last_daily': None,
                    'total_earned': 0,
                    'daily_streak': 0
                }
                self.wfile.write(json.dumps(novo_usuario).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({
                'error': str(e),
                'user_id': user_id,
                'status': 'erro_conexao'
            }).encode())
