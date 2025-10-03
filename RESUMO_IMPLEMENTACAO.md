# 📋 RESUMO EXECUTIVO - Implementação Xvfb + Web Signer

**Data:** 2025-10-03 03:20:00  
**Status:** ✅ **PRONTO PARA IMPLEMENTAÇÃO**

---

## 🎯 O QUE FOI FEITO

### ✅ 1. Código Atualizado
- **Arquivo:** `crawler_full.py`
- **Mudança:** Prioriza autenticação por certificado digital
- **Commit:** `feat: priorizar autenticação por certificado digital`
- **GitHub:** ✅ Commitado e enviado

### ✅ 2. Documentação Completa
- **Arquivo:** `INSTRUCOES_DEPLOY_XVFB.md`
- **Conteúdo:** 576 linhas de instruções passo a passo
- **Inclui:** Instalação, configuração, troubleshooting, checklist
- **GitHub:** ✅ Commitado e enviado

### ✅ 3. Deploy Tracking Atualizado
- **Arquivo:** `DEPLOY_TRACKING.md`
- **Status:** Atualizado com entrada [25] - BREAKTHROUGH
- **GitHub:** ✅ Commitado e enviado

---

## 🚀 PRÓXIMOS PASSOS (PASSO A PASSO)

### **PASSO 1: Atualizar Código no Servidor**

```bash
# 1. Conectar via SSH
ssh root@srv987902.hstgr.cloud

# 2. Navegar para o projeto
cd /opt/crawler_tjsp

# 3. Fazer backup
cp crawler_full.py crawler_full.py.backup-$(date +%Y%m%d_%H%M%S)

# 4. Atualizar do GitHub
git pull origin main

# 5. Verificar atualização
git log -1 --oneline
# Deve mostrar: "feat: priorizar autenticação por certificado digital"
```

---

### **PASSO 2: Instalar Xvfb**

```bash
# 1. Instalar pacotes
sudo apt update
sudo apt install -y xvfb x11vnc wget unzip

# 2. Verificar instalação
which Xvfb
# Deve retornar: /usr/bin/Xvfb
```

---

### **PASSO 3: Instalar Chrome e ChromeDriver**

```bash
# 1. Verificar se Chrome já está instalado
google-chrome --version

# 2. Se NÃO estiver, instalar:
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm -f google-chrome-stable_current_amd64.deb

# 3. Detectar versão do Chrome
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome versão: $CHROME_VERSION"

# 4. Baixar ChromeDriver compatível
cd /tmp
wget "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.6778.85/linux64/chromedriver-linux64.zip"

# 5. Instalar ChromeDriver
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64 chromedriver-linux64.zip

# 6. Verificar instalação
chromedriver --version
```

---

### **PASSO 4: Configurar Serviços Systemd**

#### 4.1. Criar script Xvfb

```bash
cat > /opt/start-xvfb.sh << 'EOF'
#!/bin/bash
pkill -f "Xvfb :99" || true
sleep 1
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
echo "Xvfb iniciado com PID: $XVFB_PID"
echo $XVFB_PID > /var/run/xvfb.pid
sleep 3
if ps -p $XVFB_PID > /dev/null; then
   echo "✅ Xvfb rodando no DISPLAY :99"
else
   echo "❌ Erro ao iniciar Xvfb"
   exit 1
fi
wait $XVFB_PID
EOF

chmod +x /opt/start-xvfb.sh
```

#### 4.2. Criar serviço Xvfb

```bash
cat > /etc/systemd/system/xvfb.service << 'EOF'
[Unit]
Description=X Virtual Frame Buffer
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

#### 4.3. Criar script ChromeDriver

```bash
cat > /opt/start-chromedriver.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99
pkill -f "chromedriver" || true
sleep 1
/usr/local/bin/chromedriver \
  --port=4444 \
  --whitelisted-ips="" \
  --verbose \
  --log-path=/var/log/chromedriver.log &
CHROMEDRIVER_PID=$!
echo "ChromeDriver iniciado com PID: $CHROMEDRIVER_PID"
echo $CHROMEDRIVER_PID > /var/run/chromedriver.pid
sleep 3
if ps -p $CHROMEDRIVER_PID > /dev/null; then
   echo "✅ ChromeDriver rodando na porta 4444"
else
   echo "❌ Erro ao iniciar ChromeDriver"
   exit 1
fi
wait $CHROMEDRIVER_PID
EOF

chmod +x /opt/start-chromedriver.sh
```

#### 4.4. Criar serviço ChromeDriver

```bash
cat > /etc/systemd/system/chromedriver.service << 'EOF'
[Unit]
Description=ChromeDriver for Selenium
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

#### 4.5. Habilitar e iniciar serviços

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviços
sudo systemctl enable xvfb
sudo systemctl enable chromedriver

# Iniciar Xvfb
sudo systemctl start xvfb
sudo systemctl status xvfb

# Iniciar ChromeDriver
sudo systemctl start chromedriver
sudo systemctl status chromedriver

# Testar API
curl http://localhost:4444/status
```

---

### **PASSO 5: Importar Certificado no Root**

```bash
# 1. Criar NSS database
mkdir -p /root/.pki/nssdb
certutil -N -d sql:/root/.pki/nssdb --empty-password

# 2. Importar certificado
pk12util -i /opt/crawler_tjsp/certs/25424636_pf.pfx -d sql:/root/.pki/nssdb
# Senha: 903205

# 3. Verificar
certutil -L -d sql:/root/.pki/nssdb
# Deve mostrar: FLAVIO EDUARDO CAPPI:517648902230
```

---

### **PASSO 6: Atualizar docker-compose.yml**

```bash
# 1. Backup
cd /opt/crawler_tjsp
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d_%H%M%S)

# 2. Editar
nano docker-compose.yml
```

**Conteúdo:**

```yaml
version: '3.8'

services:
  worker:
    build: .
    image: tjsp-worker:latest
    container_name: tjsp_worker_1
    
    # IMPORTANTE: network_mode host
    network_mode: "host"
    
    environment:
      - DB_HOST=72.60.62.124
      - DB_PORT=5432
      - DB_NAME=n8n
      - DB_USER=admin
      - DB_PASSWORD=${DB_PASSWORD}
      - CERT_SUBJECT_CN=517.648.902-30
      - CAS_USUARIO=${CAS_USUARIO}
      - CAS_SENHA=${CAS_SENHA}
    
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots
      - ./certs:/app/certs
    
    restart: unless-stopped
```

---

### **PASSO 7: Rebuild e Deploy**

```bash
# 1. Parar worker
docker compose stop worker

# 2. Remover Selenium Grid (se existir)
docker compose rm -f selenium-chrome

# 3. Rebuild
docker compose build --no-cache worker

# 4. Iniciar worker
docker compose up -d worker

# 5. Monitorar logs
docker compose logs -f worker
```

---

### **PASSO 8: Testar Autenticação**

```bash
# 1. Resetar 1 job
psql -h 72.60.62.124 -U admin -d n8n -c "UPDATE consultas_esaj SET status = FALSE WHERE id = 28;"

# 2. Monitorar logs
docker compose logs -f worker

# 3. Verificar sucesso
# Logs esperados:
# CAS: tentando aba CERTIFICADO…
# CAS: certificado = FLAVIO EDUARDO CAPPI:517648902230
# CAS: certificado OK.
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Marque conforme for completando:

- [ ] Código atualizado do GitHub
- [ ] Xvfb instalado e rodando
- [ ] ChromeDriver instalado e rodando
- [ ] ChromeDriver API respondendo (curl localhost:4444/status)
- [ ] Certificado importado no root
- [ ] docker-compose.yml atualizado (network_mode: host)
- [ ] Worker rodando
- [ ] Autenticação com certificado funciona
- [ ] Processo consultado com sucesso
- [ ] PDFs baixados

---

## 📚 DOCUMENTAÇÃO DE REFERÊNCIA

1. **Instruções Completas:** `INSTRUCOES_DEPLOY_XVFB.md`
2. **Plano Original:** `PLANO_XVFB_WEBSIGNER.md`
3. **Deploy Tracking:** `DEPLOY_TRACKING.md`
4. **Código Atualizado:** `crawler_full.py` (linhas 279-335)

---

## 🆘 SUPORTE

Se encontrar problemas, consulte:
- **Troubleshooting:** Seção completa em `INSTRUCOES_DEPLOY_XVFB.md`
- **Logs do Xvfb:** `sudo journalctl -u xvfb -n 50`
- **Logs do ChromeDriver:** `tail -f /var/log/chromedriver.log`
- **Logs do Worker:** `docker compose logs -f worker`

---

**Última Atualização:** 2025-10-03 03:20:00  
**Autor:** Cascade AI  
**Status:** ✅ PRONTO PARA IMPLEMENTAÇÃO
