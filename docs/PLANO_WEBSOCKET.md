# 🔌 Plano de Implementação: Solução WebSocket

**Data:** 2025-10-03  
**Status:** 🟢 EM IMPLEMENTAÇÃO  
**Estimativa:** 15-20 horas total

---

## 🎯 Objetivo

Substituir Web Signer Native Messaging por solução WebSocket customizada que funciona em ambiente headless.

---

## 📋 FASE 1: Preparação (2-3 horas)

### **1.1 Criar Ícones da Extensão**

```bash
cd /opt/crawler_tjsp/chrome_extension

# Criar ícones simples (pode usar ImageMagick)
convert -size 16x16 xc:blue icon16.png
convert -size 48x48 xc:blue icon48.png
convert -size 128x128 xc:blue icon128.png
```

**OU** baixar ícones prontos:
```bash
# Usar ícones genéricos de certificado
wget https://via.placeholder.com/16x16/4285f4/ffffff?text=WS -O icon16.png
wget https://via.placeholder.com/48x48/4285f4/ffffff?text=WS -O icon48.png
wget https://via.placeholder.com/128x128/4285f4/ffffff?text=WS -O icon128.png
```

### **1.2 Instalar Dependências Python**

```bash
pip install websockets cryptography
```

### **1.3 Preparar Certificado**

```bash
# Copiar certificado para local acessível
cp /path/to/certificado.pfx /opt/crawler_tjsp/certificado.pfx
chmod 600 /opt/crawler_tjsp/certificado.pfx
```

---

## 📋 FASE 2: Teste Servidor WebSocket (2-3 horas)

### **2.1 Testar Servidor Standalone**

```bash
cd /opt/crawler_tjsp

# Iniciar servidor
python3 websocket_cert_server.py certificado.pfx 903205
```

**Saída esperada:**
```
🚀 Servidor WebSocket iniciando em ws://localhost:8765
✅ Certificado carregado: FLAVIO EDUARDO CAPPI:517648902230
✅ Servidor rodando!
   Aguardando conexões da extensão Chrome...
```

### **2.2 Testar Conexão WebSocket**

Criar script de teste:

```python
# test_websocket_client.py
import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Listar certificados
        await websocket.send(json.dumps({'action': 'list_certificates'}))
        response = await websocket.recv()
        print(f"Resposta: {response}")

asyncio.run(test_connection())
```

```bash
python3 test_websocket_client.py
```

**Resultado esperado:**
```json
{
  "action": "list_certificates",
  "certificates": [{
    "subject": "FLAVIO EDUARDO CAPPI:517648902230",
    "nome": "FLAVIO EDUARDO CAPPI",
    "cpf": "517648902230",
    ...
  }]
}
```

---

## 📋 FASE 3: Teste Extensão Manualmente (3-4 horas)

### **3.1 Carregar Extensão no Chrome (via RDP)**

1. Abrir Chrome via RDP
2. Ir para: `chrome://extensions/`
3. Ativar "Developer mode"
4. Clicar "Load unpacked"
5. Selecionar pasta: `/opt/crawler_tjsp/chrome_extension`

**Verificar:**
- ✅ Extensão aparece na lista
- ✅ Sem erros no console
- ✅ Ícone aparece na barra

### **3.2 Testar Conexão WebSocket**

1. Abrir DevTools (F12)
2. Ir para aba "Console"
3. Verificar logs:

```
🔌 Conectando ao servidor WebSocket...
✅ Conectado ao servidor WebSocket
📋 Certificados disponíveis: [...]
🚀 Web Signer Custom (WebSocket) - Service Worker iniciado
```

### **3.3 Testar no e-SAJ**

1. Acessar: https://esaj.tjsp.jus.br/cpopg/open.do
2. Clicar em "Certificado digital"
3. **Verificar se dropdown de certificados aparece!**

**Se aparecer:** ✅ Extensão funcionando!  
**Se não aparecer:** Verificar console para erros

---

## 📋 FASE 4: Integração com Selenium (4-5 horas)

### **4.1 Criar Script de Teste**

```python
# test_selenium_websocket.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Remote
import subprocess
import time

def start_websocket_server():
    """Inicia servidor WebSocket em background"""
    process = subprocess.Popen([
        'python3', 'websocket_cert_server.py',
        'certificado.pfx',
        '903205'
    ])
    time.sleep(2)
    return process

def test_selenium_with_websocket():
    """Testa Selenium com extensão WebSocket"""
    
    # 1. Iniciar servidor WebSocket
    print("🚀 Iniciando servidor WebSocket...")
    ws_process = start_websocket_server()
    
    try:
        # 2. Configurar Chrome com extensão
        opts = Options()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--load-extension=/opt/crawler_tjsp/chrome_extension")
        
        # 3. Conectar ao ChromeDriver
        driver = Remote(
            command_executor="http://localhost:4444",
            options=opts
        )
        
        # 4. Acessar e-SAJ
        print("📄 Acessando e-SAJ...")
        driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        time.sleep(3)
        
        # 5. Clicar em "Certificado digital"
        print("🔐 Clicando em 'Certificado digital'...")
        aba_cert = driver.find_element(By.ID, "linkAbaCertificado")
        aba_cert.click()
        time.sleep(5)  # Aguardar WebSocket carregar certificados
        
        # 6. Verificar dropdown
        print("📋 Verificando dropdown de certificados...")
        dropdown = driver.find_element(By.ID, "certificados")
        options = dropdown.find_elements(By.TAG_NAME, "option")
        
        print(f"   Opções encontradas: {len(options)}")
        for opt in options:
            text = opt.text_content()
            value = opt.get_attribute("value")
            print(f"   - {text} (value: {value})")
        
        # 7. Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/selenium_websocket.png")
        
        # 8. Verificar sucesso
        valid_certs = [opt for opt in options if opt.get_attribute("value")]
        
        if valid_certs:
            print("\n🎉 SUCESSO! Certificado detectado via WebSocket!")
            return True
        else:
            print("\n❌ FALHOU! Certificado não apareceu")
            return False
        
    finally:
        driver.quit()
        ws_process.terminate()

if __name__ == "__main__":
    test_selenium_with_websocket()
```

### **4.2 Executar Teste**

```bash
cd /opt/crawler_tjsp
python3 test_selenium_websocket.py
```

---

## 📋 FASE 5: Ajustes e Debugging (3-4 horas)

### **Problemas Comuns e Soluções:**

#### **Problema 1: Extensão não carrega**
```bash
# Verificar permissões
chmod -R 755 /opt/crawler_tjsp/chrome_extension

# Verificar manifest.json
cat chrome_extension/manifest.json | python3 -m json.tool
```

#### **Problema 2: WebSocket não conecta**
```bash
# Verificar se servidor está rodando
ps aux | grep websocket_cert_server

# Verificar porta
netstat -tlnp | grep 8765

# Testar conexão
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://localhost:8765/
```

#### **Problema 3: Certificado não aparece**
- Verificar console do Chrome (F12)
- Verificar logs do servidor WebSocket
- Verificar se `window.WebSigner` está definido

---

## 📋 FASE 6: Integração com Crawler (2-3 horas)

### **6.1 Criar Serviço Systemd para WebSocket**

```bash
# /etc/systemd/system/websocket-cert.service

[Unit]
Description=WebSocket Certificate Server
After=network.target

[Service]
Type=simple
User=crawler
Group=crawler
WorkingDirectory=/opt/crawler_tjsp
ExecStart=/usr/bin/python3 /opt/crawler_tjsp/websocket_cert_server.py /opt/crawler_tjsp/certificado.pfx 903205
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable websocket-cert
sudo systemctl start websocket-cert
sudo systemctl status websocket-cert
```

### **6.2 Atualizar Crawler Worker**

```python
# Adicionar ao worker.py

from selenium.webdriver.chrome.options import Options

def setup_chrome_with_websocket():
    """Configura Chrome com extensão WebSocket"""
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--headless=new")
    opts.add_argument("--load-extension=/opt/crawler_tjsp/chrome_extension")
    
    driver = Remote(
        command_executor="http://localhost:4444",
        options=opts
    )
    return driver
```

---

## ✅ Checklist de Conclusão

- [ ] Servidor WebSocket rodando e testado
- [ ] Extensão carrega sem erros
- [ ] Conexão WebSocket estabelecida
- [ ] Certificado aparece no dropdown do e-SAJ
- [ ] Login no e-SAJ funciona com certificado
- [ ] Integração com Selenium funciona
- [ ] Serviço systemd configurado
- [ ] Crawler worker atualizado
- [ ] Testes end-to-end passando

---

## 📊 Métricas de Sucesso

- ✅ Certificado aparece no dropdown (< 5 segundos)
- ✅ Login no e-SAJ bem-sucedido
- ✅ Busca de processos funciona
- ✅ Sem erros no console
- ✅ Funciona em headless

---

## 🆘 Suporte

Se encontrar problemas:
1. Verificar logs: `journalctl -u websocket-cert -f`
2. Verificar console do Chrome (F12)
3. Testar servidor standalone
4. Verificar permissões dos arquivos
