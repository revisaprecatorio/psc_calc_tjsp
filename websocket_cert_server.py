#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor WebSocket que substitui Web Signer Native Messaging
Gerencia certificados e assina dados
"""

import asyncio
import websockets
import json
import base64
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from pathlib import Path

class CertificateManager:
    """Gerencia certificados A1"""
    
    def __init__(self, cert_path, cert_password):
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.private_key = None
        self.certificate = None
        self.ca_certs = None
        self._load_certificate()
    
    def _load_certificate(self):
        """Carrega certificado .pfx"""
        with open(self.cert_path, 'rb') as f:
            pfx_data = f.read()
        
        self.private_key, self.certificate, self.ca_certs = pkcs12.load_key_and_certificates(
            pfx_data,
            self.cert_password.encode(),
            None
        )
        print(f"✅ Certificado carregado: {self.get_certificate_info()['subject']}")
    
    def get_certificate_info(self):
        """Retorna informações do certificado"""
        subject = self.certificate.subject
        cn = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        
        # Extrair nome e CPF (formato ICP-Brasil: "NOME:CPF")
        if ':' in cn:
            nome, cpf = cn.split(':', 1)
        else:
            nome = cn
            cpf = "N/A"
        
        return {
            'subject': cn,
            'nome': nome,
            'cpf': cpf,
            'issuer': self.certificate.issuer.rfc4514_string(),
            'serial': str(self.certificate.serial_number),
            'not_before': self.certificate.not_valid_before.isoformat(),
            'not_after': self.certificate.not_valid_after.isoformat(),
        }
    
    def sign_data(self, data):
        """Assina dados com o certificado"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        signature = self.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')

class WebSignerServer:
    """Servidor WebSocket que emula Web Signer"""
    
    def __init__(self, cert_manager, host='localhost', port=8765):
        self.cert_manager = cert_manager
        self.host = host
        self.port = port
    
    async def handle_client(self, websocket, path):
        """Processa mensagens do cliente (extensão Chrome)"""
        print(f"🔌 Cliente conectado: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get('action')
                    
                    if action == 'list_certificates':
                        # Listar certificados disponíveis
                        response = {
                            'action': 'list_certificates',
                            'certificates': [self.cert_manager.get_certificate_info()]
                        }
                        await websocket.send(json.dumps(response))
                        print(f"📋 Listou certificados")
                    
                    elif action == 'sign':
                        # Assinar dados
                        payload = data.get('data')
                        signature = self.cert_manager.sign_data(payload)
                        
                        response = {
                            'action': 'sign',
                            'signature': signature,
                            'certificate': self.cert_manager.get_certificate_info()
                        }
                        await websocket.send(json.dumps(response))
                        print(f"✍️ Assinou dados")
                    
                    elif action == 'get_certificate':
                        # Retornar certificado específico
                        response = {
                            'action': 'get_certificate',
                            'certificate': self.cert_manager.get_certificate_info()
                        }
                        await websocket.send(json.dumps(response))
                        print(f"📜 Retornou certificado")
                    
                    else:
                        # Ação desconhecida
                        response = {
                            'error': f'Unknown action: {action}'
                        }
                        await websocket.send(json.dumps(response))
                
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({'error': 'Invalid JSON'}))
                except Exception as e:
                    await websocket.send(json.dumps({'error': str(e)}))
                    print(f"❌ Erro: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Cliente desconectado: {websocket.remote_address}")
    
    async def start(self):
        """Inicia o servidor WebSocket"""
        print(f"🚀 Servidor WebSocket iniciando em ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✅ Servidor rodando!")
            print(f"   Aguardando conexões da extensão Chrome...")
            await asyncio.Future()  # Roda para sempre

def main():
    """Ponto de entrada"""
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python websocket_cert_server.py <caminho_certificado.pfx> <senha>")
        sys.exit(1)
    
    cert_path = sys.argv[1]
    cert_password = sys.argv[2]
    
    if not Path(cert_path).exists():
        print(f"❌ Certificado não encontrado: {cert_path}")
        sys.exit(1)
    
    # Criar gerenciador de certificados
    cert_manager = CertificateManager(cert_path, cert_password)
    
    # Criar e iniciar servidor
    server = WebSignerServer(cert_manager)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado")

if __name__ == "__main__":
    main()
