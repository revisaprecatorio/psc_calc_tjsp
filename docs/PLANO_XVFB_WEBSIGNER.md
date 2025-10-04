# 🚀 PLANO DE IMPLEMENTAÇÃO: Xvfb + Web Signer

**Data:** 2025-10-02  
**Objetivo:** Implementar solução com Xvfb para usar certificado digital A1 com Web Signer  
**Tempo Estimado:** 6-8 horas

---

## 📊 CONTEXTO E DECISÃO

### **Por que abandonar Selenium Grid Docker:**

1. ❌ **Web Signer não funciona em containers Docker**
   - Plugin nativo requer acesso ao sistema
   - Certificado precisa estar no sistema operacional
   - Diálogos nativos não funcionam em headless

2. ❌ **Login CPF/Senha não é viável:**
   - 2FA obrigatório
   - Emails randômicos de validação
   - Áreas restritas sem certificado
   - Controle de acesso muito rígido

3. ✅ **Certificado é a ÚNICA opção:**
   - Testado e funcionando no macOS
   - Não requer usuário/senha
   - Acesso completo ao sistema
   - Apenas certificado + Web Signer

---

## 🎯 ARQUITETURA PROPOSTA

### **ANTES (Não Funciona):**
```
┌─────────────────────────────────────────┐
│ Container: selenium-chrome              │
│ - Chrome headless                       │
│ - Sem Web Signer                        │
│ - Sem certificado                       │
│ ❌ NÃO FUNCIONA                         │
└─────────────────────────────────────────┘
```

### **DEPOIS (Solução):**
```
┌──────────────────────────────────────────────────────────┐
│ VPS Ubuntu (srv987902) - Host Direto                     │
│                                                           │
│ ┌───────────────────────────────────────────────────────┐│
│ │ 1. Xvfb (Display Virtual :99)                         ││
│ │    - Framebuffer em memória                           ││
│ │    - Simula ambiente gráfico                          ││
│ │    - Serviço systemd (sempre ativo)                   ││
│ └───────────────────────────────────────────────────────┘│
│                           ↓                               │
│ ┌───────────────────────────────────────────────────────┐│
│ │ 2. Chrome (Instalado no Ubuntu)                       ││
│ │    - Modo NÃO-headless (usa Xvfb)                     ││
│ │    - Web Signer instalado e funcionando               ││
│ │    - Certificado A1 importado (NSS database)          ││
│ │    - DISPLAY=:99                                      ││
│ └───────────────────────────────────────────────────────┘│
│                           ↓                               │
│ ┌───────────────────────────────────────────────────────┐│
│ │ 3. ChromeDriver (Porta 4444)                          ││
│ │    - Controla Chrome local                            ││
│ │    - Serviço systemd (sempre ativo)                   ││
│ │    - API compatível com Selenium                      ││
│ └───────────────────────────────────────────────────────┘│
│                           ↓                               │
│ ┌───────────────────────────────────────────────────────┐│
│ │ 4. Worker Python (Container Docker)                   ││
│ │    - Conecta ao ChromeDriver via localhost:4444       ││
│ │    - network_mode: host                               ││
│ │    - Mantém PostgreSQL em Docker                      ││
│ └───────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Web Signer funciona 100%
- ✅ Certificado A1 utilizável
- ✅ Worker Python continua em Docker
- ✅ PostgreSQL continua em Docker
- ✅ Apenas Chrome sai do Docker

---

## 📋 PLANO DE IMPLEMENTAÇÃO

### **FASE 1: Preparação (1-2 horas)**

#### **1.1. Backup e Parada de Serviços**

```bash
# Conectar na VPS
ssh root@srv987902.hstgr.cloud

# Navegar para diretório
cd /opt/crawler_tjsp

# Backup do docker-compose.yml atual
cp docker-compose.yml docker-compose.yml.backup-grid
cp .env .env.backup

# Parar Selenium Grid (vamos substituir)
docker compose stop selenium-chrome
# NÃO deletar ainda, apenas parar

# Parar worker temporariamente
docker compose stop worker
```

#### **1.2. Instalar Dependências**

```bash
# Atualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Xvfb e ferramentas
sudo apt install -y xvfb x11vnc wget unzip

# Instalar certutil (para gerenciar certificados)
sudo apt install -y libnss3-tools
```

---

### **FASE 2: Instalar Chrome no Host (30 min)**

```bash
# 1. Baixar Chrome
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 2. Instalar
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 3. Verificar versão
google-chrome --version
# Exemplo: Google Chrome 131.0.6778.85

# 4. Baixar ChromeDriver (mesma versão)
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome versão: $CHROME_VERSION"

# Baixar última versão do ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -O /tmp/chromedriver_version.txt
CHROMEDRIVER_VERSION=$(cat /tmp/chromedriver_version.txt)
echo "ChromeDriver versão: $CHROMEDRIVER_VERSION"

wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 5. Verificar ChromeDriver
chromedriver --version
# Deve mostrar versão compatível com Chrome

# 6. Limpar arquivos temporários
rm -f google-chrome-stable_current_amd64.deb chromedriver_linux64.zip
```

---

### **FASE 3: Instalar Web Signer (30 min)**

```bash
# 1. Baixar Web Signer para Ubuntu
cd /tmp
wget https://websigner.softplan.com.br/Downloads/Instalador/Linux/WebSigner_Ubuntu_x64.deb

# 2. Instalar
sudo dpkg -i WebSigner_Ubuntu_x64.deb

# 3. Se der erro de dependências, corrigir:
sudo apt-get install -f -y

# 4. Verificar instalação
ls -la /opt/WebSigner/
# Deve mostrar arquivos do Web Signer

# 5. Verificar serviço
sudo systemctl status websigner
# Deve estar ativo

# 6. Limpar
rm -f WebSigner_Ubuntu_x64.deb
```

---

### **FASE 4: Configurar Certificado A1 (30 min)**

```bash
# 1. Criar diretório para certificados
mkdir -p /root/.certificados
chmod 700 /root/.certificados

# 2. Copiar certificado .pfx
cp /opt/crawler_tjsp/certs/25424636_pf.pfx /root/.certificados/
chmod 600 /root/.certificados/25424636_pf.pfx

# 3. Criar NSS database (Chrome usa NSS para certificados)
mkdir -p /root/.pki/nssdb
certutil -N -d sql:/root/.pki/nssdb --empty-password

# 4. Importar certificado .pfx para NSS database
pk12util -i /root/.certificados/25424636_pf.pfx -d sql:/root/.pki/nssdb
# Vai pedir senha do .pfx: 903205

# 5. Listar certificados importados
certutil -L -d sql:/root/.pki/nssdb
# Deve mostrar: FLAVIO EDUARDO CAPPI:517648

# 6. Verificar detalhes do certificado
certutil -L -d sql:/root/.pki/nssdb -n "FLAVIO EDUARDO CAPPI:517648"
# Deve mostrar informações do certificado
```

---

### **FASE 5: Configurar Xvfb (30 min)**

#### **5.1. Criar Script de Inicialização**

```bash
cat > /opt/start-xvfb.sh << 'EOF'
#!/bin/bash
# Script de inicialização do Xvfb

# Matar Xvfb existente (se houver)
pkill -f "Xvfb :99" || true
sleep 1

# Iniciar Xvfb no display :99
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

echo "Xvfb iniciado com PID: $XVFB_PID"
echo $XVFB_PID > /var/run/xvfb.pid

# Aguardar Xvfb iniciar
sleep 3

# Exportar DISPLAY
export DISPLAY=:99

# Verificar se Xvfb está rodando
if ps -p $XVFB_PID > /dev/null; then
   echo "✅ Xvfb rodando no DISPLAY :99"
   echo "✅ Resolução: 1920x1080x24"
else
   echo "❌ Erro ao iniciar Xvfb"
   exit 1
fi

# Manter script rodando
wait $XVFB_PID
EOF

chmod +x /opt/start-xvfb.sh
```

#### **5.2. Criar Serviço Systemd**

```bash
cat > /etc/systemd/system/xvfb.service << 'EOF'
[Unit]
Description=X Virtual Frame Buffer
Documentation=man:Xvfb(1)
After=network.target

[Service]
Type=forking
ExecStart=/opt/start-xvfb.sh
PIDFile=/var/run/xvfb.pid
Restart=always
RestartSec=10
Environment="DISPLAY=:99"

[Install]
WantedBy=multi-user.target
EOF
```

#### **5.3. Habilitar e Iniciar Serviço**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable xvfb

# Iniciar serviço
sudo systemctl start xvfb

# Verificar status
sudo systemctl status xvfb

# Verificar se display está ativo
export DISPLAY=:99
xdpyinfo | head -10
# Deve mostrar informações do display :99
```

---

### **FASE 6: Configurar ChromeDriver (1 hora)**

#### **6.1. Criar Script de Inicialização**

```bash
cat > /opt/start-chromedriver.sh << 'EOF'
#!/bin/bash
# Script de inicialização do ChromeDriver

# Exportar DISPLAY
export DISPLAY=:99

# Matar ChromeDriver existente (se houver)
pkill -f "chromedriver" || true
sleep 1

# Iniciar ChromeDriver
/usr/local/bin/chromedriver \
  --port=4444 \
  --whitelisted-ips="" \
  --verbose \
  --log-path=/var/log/chromedriver.log &

CHROMEDRIVER_PID=$!
echo "ChromeDriver iniciado com PID: $CHROMEDRIVER_PID"
echo $CHROMEDRIVER_PID > /var/run/chromedriver.pid

# Aguardar ChromeDriver iniciar
sleep 3

# Verificar se está rodando
if ps -p $CHROMEDRIVER_PID > /dev/null; then
   echo "✅ ChromeDriver rodando na porta 4444"
   echo "✅ DISPLAY: :99"
else
   echo "❌ Erro ao iniciar ChromeDriver"
   exit 1
fi

# Manter script rodando
wait $CHROMEDRIVER_PID
EOF

chmod +x /opt/start-chromedriver.sh
```

#### **6.2. Criar Serviço Systemd**

```bash
cat > /etc/systemd/system/chromedriver.service << 'EOF'
[Unit]
Description=ChromeDriver for Selenium
Documentation=https://chromedriver.chromium.org/
After=xvfb.service
Requires=xvfb.service

[Service]
Type=forking
ExecStart=/opt/start-chromedriver.sh
PIDFile=/var/run/chromedriver.pid
Restart=always
RestartSec=10
Environment="DISPLAY=:99"

[Install]
WantedBy=multi-user.target
EOF
```

#### **6.3. Habilitar e Iniciar Serviço**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable chromedriver

# Iniciar serviço
sudo systemctl start chromedriver

# Verificar status
sudo systemctl status chromedriver

# Testar API do ChromeDriver
curl http://localhost:4444/status
# Deve retornar JSON com status "ready"
```

---

### **FASE 7: Testar Chrome + Web Signer (1 hora)**

#### **7.1. Teste Manual do Chrome**

```bash
# Exportar DISPLAY
export DISPLAY=:99

# Testar Chrome
google-chrome --no-sandbox --disable-dev-shm-usage https://websigner.softplan.com.br/Setup &

# Aguardar alguns segundos
sleep 5

# Verificar se Chrome está rodando
ps aux | grep chrome
# Deve mostrar processo do Chrome

# Matar Chrome de teste
pkill -f "google-chrome"
```

#### **7.2. Configurar VNC para Debug Visual (Opcional)**

```bash
# Instalar x11vnc (se ainda não instalou)
sudo apt install -y x11vnc

# Iniciar VNC server
x11vnc -display :99 -bg -nopw -listen localhost -xkb -forever

# No seu Mac, criar túnel SSH
# ssh -L 5900:localhost:5900 root@srv987902.hstgr.cloud

# Abrir VNC Viewer no Mac
# Conectar em: localhost:5900

# Agora você pode ver o Xvfb visualmente!
```

#### **7.3. Testar Acesso ao TJSP**

```bash
# Via VNC, você pode ver o Chrome abrindo
export DISPLAY=:99
google-chrome --no-sandbox --disable-dev-shm-usage https://esaj.tjsp.jus.br/sajcas/login &

# Verificar se:
# 1. Página de login abre
# 2. Aba "Certificado digital" está disponível
# 3. Web Signer está ativo
# 4. Certificado aparece na lista
```

---

### **FASE 8: Modificar docker-compose.yml (30 min)**

```bash
cd /opt/crawler_tjsp

# Backup do atual
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d)

# Editar
nano docker-compose.yml
```

**Novo conteúdo:**

```yaml
version: '3.8'

services:
  # REMOVIDO: selenium-chrome
  # Agora usamos Chrome + Xvfb no host
  
  worker:
    build: .
    image: tjsp-worker:latest
    container_name: tjsp_worker_1
    
    # IMPORTANTE: network_mode host para acessar ChromeDriver
    network_mode: "host"
    
    environment:
      # Banco de dados
      - DB_HOST=72.60.62.124
      - DB_PORT=5432
      - DB_NAME=n8n
      - DB_USER=admin
      - DB_PASSWORD=${DB_PASSWORD}
      
      # REMOVIDO: SELENIUM_REMOTE_URL
      # Worker vai conectar ao ChromeDriver local (localhost:4444)
      
      # Certificado (para auto-seleção)
      - CERT_PATH=/app/certs/25424636_pf.pfx
      - CERT_PASSWORD=903205
      - CERT_SUBJECT_CN=517.648.902-30
      - CERT_ISSUER_CN=AC Certisign Múltipla G5
      
      # Autenticação (não será usada com certificado)
      - CAS_USUARIO=${CAS_USUARIO}
      - CAS_SENHA=${CAS_SENHA}
    
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots
      - ./certs:/app/certs
    
    restart: unless-stopped
```

---

### **FASE 9: Atualizar .env (5 min)**

```bash
nano .env
```

**Remover linha:**
```bash
# REMOVER ESTA LINHA:
# SELENIUM_REMOTE_URL=http://selenium-chrome:4444
```

**Arquivo final deve ter:**
```bash
# ===== BANCO DE DADOS =====
DB_HOST=72.60.62.124
DB_PORT=5432
DB_NAME=n8n
DB_USER=admin
DB_PASSWORD=BetaAgent2024SecureDB

# ===== CERTIFICADO DIGITAL =====
CERT_PATH=/app/certs/25424636_pf.pfx
CERT_PASSWORD=903205
CERT_SUBJECT_CN=517.648.902-30
CERT_ISSUER_CN=AC Certisign Múltipla G5

# ===== AUTENTICAÇÃO (não usado com certificado) =====
CAS_USUARIO=51764890230
CAS_SENHA=903205
```

---

### **FASE 10: Rebuild e Deploy (30 min)**

```bash
cd /opt/crawler_tjsp

# 1. Rebuild da imagem (código mudou)
docker compose build --no-cache worker

# 2. Remover container Selenium Grid antigo
docker compose rm -f selenium-chrome

# 3. Iniciar worker
docker compose up -d worker

# 4. Verificar logs
docker compose logs -f worker
```

---

### **FASE 11: Testar Autenticação (30 min)**

```bash
# 1. Resetar 1 job para teste
psql -h 72.60.62.124 -U admin -d n8n -c "
UPDATE consultas_esaj SET status = FALSE WHERE id = 28;"

# 2. Monitorar logs do worker
docker compose logs -f worker

# 3. Logs esperados (SUCESSO):
# [INFO] Conectando ao ChromeDriver local (Xvfb): http://localhost:4444
# [INFO] ✅ Conectado ao ChromeDriver local com sucesso!
# [INFO] Chrome rodando no Xvfb com Web Signer habilitado
# CAS: tentando aba CERTIFICADO…
# CAS: certificado = FLAVIO EDUARDO CAPPI:517648
# CAS: certificado OK.
# [INFO] ✅ Autenticação bem-sucedida!

# 4. Se der erro, verificar:
# - Xvfb está rodando: systemctl status xvfb
# - ChromeDriver está rodando: systemctl status chromedriver
# - Certificado está importado: certutil -L -d sql:/root/.pki/nssdb
# - Web Signer está ativo: systemctl status websigner
```

---

## 🔍 TROUBLESHOOTING

### **Problema 1: Xvfb não inicia**

```bash
# Verificar logs
sudo journalctl -u xvfb -n 50

# Testar manualmente
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
xdpyinfo

# Se funcionar manual, reiniciar serviço
sudo systemctl restart xvfb
```

### **Problema 2: ChromeDriver não conecta**

```bash
# Verificar se está rodando
sudo systemctl status chromedriver

# Verificar porta
netstat -tulpn | grep 4444

# Testar API
curl http://localhost:4444/status

# Ver logs
tail -f /var/log/chromedriver.log
```

### **Problema 3: Certificado não aparece**

```bash
# Listar certificados
certutil -L -d sql:/root/.pki/nssdb

# Se não aparecer, reimportar
pk12util -i /root/.certificados/25424636_pf.pfx -d sql:/root/.pki/nssdb

# Verificar permissões
ls -la /root/.pki/nssdb/
```

### **Problema 4: Web Signer não funciona**

```bash
# Verificar se está instalado
ls -la /opt/WebSigner/

# Verificar serviço
sudo systemctl status websigner

# Reiniciar
sudo systemctl restart websigner

# Testar no Chrome (via VNC)
export DISPLAY=:99
google-chrome https://websigner.softplan.com.br/Setup
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de considerar concluído, verificar:

- [ ] Xvfb rodando: `systemctl status xvfb`
- [ ] ChromeDriver rodando: `systemctl status chromedriver`
- [ ] Web Signer instalado: `ls /opt/WebSigner/`
- [ ] Certificado importado: `certutil -L -d sql:/root/.pki/nssdb`
- [ ] Chrome abre no Xvfb: `DISPLAY=:99 google-chrome &`
- [ ] Worker conecta ao ChromeDriver: logs mostram conexão
- [ ] Autenticação com certificado funciona: logs mostram "certificado OK"
- [ ] Processo é consultado com sucesso
- [ ] PDFs são baixados

---

## 📊 RESUMO EXECUTIVO

### **O que muda:**
- ❌ **Remove:** Selenium Grid em Docker
- ✅ **Adiciona:** Xvfb + Chrome + ChromeDriver no host
- ✅ **Mantém:** Worker Python em Docker
- ✅ **Mantém:** PostgreSQL em Docker

### **Tempo total:** 6-8 horas
### **Complexidade:** Média-Alta
### **Risco:** Baixo (solução comprovada)

### **Benefícios:**
- ✅ Web Signer funciona 100%
- ✅ Certificado A1 utilizável
- ✅ Sem necessidade de usuário/senha
- ✅ Acesso completo ao sistema TJSP
- ✅ Solução estável e confiável

---

**Última Atualização:** 2025-10-02 15:00:00
