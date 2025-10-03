# 🚀 INSTRUÇÕES DE DEPLOY - Xvfb + Web Signer

**Data:** 2025-10-03 03:20:00  
**Objetivo:** Implementar crawler com certificado digital usando Xvfb  
**Status Web Signer:** ✅ JÁ INSTALADO E FUNCIONANDO

---

## 📋 RESUMO EXECUTIVO

### ✅ O que JÁ está pronto:
- **Web Signer:** Instalado e funcionando
- **Certificado A1:** Importado no Chromium (`FLAVIO EDUARDO CAPPI:517648`)
- **Código atualizado:** Prioriza autenticação por certificado
- **GitHub:** Código commitado e enviado

### 🔧 O que FALTA implementar:
1. Instalar Xvfb (display virtual)
2. Instalar ChromeDriver
3. Configurar serviços systemd
4. Atualizar código no servidor
5. Ajustar docker-compose.yml
6. Testar autenticação

---

## PARTE 1: ATUALIZAR CÓDIGO NO SERVIDOR

### Passo 1.1: Conectar via SSH

```bash
ssh root@srv987902.hstgr.cloud
# Ou: ssh root@72.60.62.124
```

### Passo 1.2: Navegar para o diretório do projeto

```bash
cd /opt/crawler_tjsp
```

### Passo 1.3: Fazer backup do código atual

```bash
# Backup do crawler
cp crawler_full.py crawler_full.py.backup-$(date +%Y%m%d_%H%M%S)

# Verificar backup
ls -lh crawler_full.py*
```

### Passo 1.4: Atualizar código do GitHub

```bash
# Fazer pull do GitHub
git pull origin main

# Verificar se atualizou
git log -1 --oneline
# Deve mostrar: "feat: priorizar autenticação por certificado digital"
```

### Passo 1.5: Verificar mudanças

```bash
# Ver diferenças
git diff HEAD~1 crawler_full.py

# Deve mostrar que agora PRIORIZA certificado ao invés de CPF/senha
```

---

## PARTE 2: INSTALAR INFRAESTRUTURA (Xvfb + ChromeDriver)

### Passo 2.1: Instalar Xvfb

```bash
# Atualizar sistema
sudo apt update

# Instalar Xvfb e ferramentas
sudo apt install -y xvfb x11vnc wget unzip

# Verificar instalação
which Xvfb
# Deve retornar: /usr/bin/Xvfb
```

### Passo 2.2: Instalar Chrome (se ainda não estiver instalado)

```bash
# Verificar se Chrome já está instalado
google-chrome --version

# Se NÃO estiver instalado, executar:
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm -f google-chrome-stable_current_amd64.deb

# Verificar versão instalada
google-chrome --version
# Exemplo: Google Chrome 131.0.6778.85
```

### Passo 2.3: Instalar ChromeDriver (versão compatível)

```bash
# Detectar versão do Chrome
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
echo "Chrome versão: $CHROME_VERSION"

# Baixar ChromeDriver compatível
cd /tmp
wget "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}.0.6778.85/linux64/chromedriver-linux64.zip"

# Se o link acima não funcionar, use:
# wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -O chromedriver_version.txt
# CHROMEDRIVER_VERSION=$(cat chromedriver_version.txt)
# wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip

# Descompactar e instalar
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Limpar arquivos temporários
rm -rf chromedriver-linux64 chromedriver-linux64.zip

# Verificar instalação
chromedriver --version
# Deve mostrar versão compatível com Chrome
```

---

## PARTE 3: CONFIGURAR SERVIÇOS SYSTEMD

### Passo 3.1: Criar script de inicialização do Xvfb

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

### Passo 3.2: Criar serviço systemd para Xvfb

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

### Passo 3.3: Criar script de inicialização do ChromeDriver

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

### Passo 3.4: Criar serviço systemd para ChromeDriver

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

### Passo 3.5: Habilitar e iniciar serviços

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviços para iniciar no boot
sudo systemctl enable xvfb
sudo systemctl enable chromedriver

# Iniciar Xvfb
sudo systemctl start xvfb
sudo systemctl status xvfb
# Deve mostrar: active (running)

# Iniciar ChromeDriver
sudo systemctl start chromedriver
sudo systemctl status chromedriver
# Deve mostrar: active (running)

# Testar API do ChromeDriver
curl http://localhost:4444/status
# Deve retornar JSON com "ready": true
```

---

## PARTE 4: IMPORTAR CERTIFICADO NO CHROME DO ROOT

⚠️ **IMPORTANTE:** O certificado está importado no usuário `crawler`, mas o ChromeDriver rodará como `root`. Precisamos importar o certificado também para o `root`.

### Passo 4.1: Criar NSS database para root

```bash
# Criar diretório
mkdir -p /root/.pki/nssdb

# Criar database
certutil -N -d sql:/root/.pki/nssdb --empty-password
```

### Passo 4.2: Importar certificado .pfx

```bash
# Importar certificado
pk12util -i /opt/crawler_tjsp/certs/25424636_pf.pfx -d sql:/root/.pki/nssdb

# Quando pedir senha, digite: 903205
```

### Passo 4.3: Verificar certificado importado

```bash
# Listar certificados
certutil -L -d sql:/root/.pki/nssdb

# Deve mostrar algo como:
# FLAVIO EDUARDO CAPPI:517648902230
```

---

## PARTE 5: ATUALIZAR DOCKER-COMPOSE.YML

### Passo 5.1: Fazer backup do docker-compose.yml

```bash
cd /opt/crawler_tjsp
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d_%H%M%S)
```

### Passo 5.2: Editar docker-compose.yml

```bash
nano docker-compose.yml
```

**Remover o serviço `selenium-chrome` e ajustar o `worker`:**

```yaml
version: '3.8'

services:
  # REMOVIDO: selenium-chrome (agora usamos ChromeDriver no host)
  
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
      # Worker conecta ao ChromeDriver local (localhost:4444)
      
      # Certificado
      - CERT_SUBJECT_CN=517.648.902-30
      
      # Autenticação (fallback)
      - CAS_USUARIO=${CAS_USUARIO}
      - CAS_SENHA=${CAS_SENHA}
    
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots
      - ./certs:/app/certs
    
    restart: unless-stopped
```

### Passo 5.3: Salvar e sair

Pressione `Ctrl+X`, depois `Y`, depois `Enter`.

---

## PARTE 6: REBUILD E DEPLOY

### Passo 6.1: Parar worker atual

```bash
cd /opt/crawler_tjsp
docker compose stop worker
```

### Passo 6.2: Remover container Selenium Grid (se existir)

```bash
docker compose rm -f selenium-chrome
```

### Passo 6.3: Rebuild da imagem

```bash
docker compose build --no-cache worker
```

### Passo 6.4: Iniciar worker

```bash
docker compose up -d worker
```

### Passo 6.5: Monitorar logs

```bash
docker compose logs -f worker
```

**Logs esperados:**
```
[INFO] Conectando ao ChromeDriver local (Xvfb): http://localhost:4444
[INFO] ✅ Conectado ao ChromeDriver local com sucesso!
CAS: tentando aba CERTIFICADO…
CAS: certificado = FLAVIO EDUARDO CAPPI:517648902230
CAS: certificado OK.
```

---

## PARTE 7: TESTAR AUTENTICAÇÃO

### Passo 7.1: Resetar 1 job para teste

```bash
# Conectar ao PostgreSQL
psql -h 72.60.62.124 -U admin -d n8n

# Resetar 1 job
UPDATE consultas_esaj SET status = FALSE WHERE id = 28;

# Sair
\q
```

### Passo 7.2: Monitorar logs do worker

```bash
docker compose logs -f worker
```

### Passo 7.3: Verificar sucesso

**Logs de SUCESSO:**
```
✅ Autenticação bem-sucedida!
✅ Processo consultado com sucesso
✅ PDF baixado
```

**Se der erro, verificar:**
```bash
# 1. Xvfb está rodando?
sudo systemctl status xvfb

# 2. ChromeDriver está rodando?
sudo systemctl status chromedriver
curl http://localhost:4444/status

# 3. Certificado está importado?
certutil -L -d sql:/root/.pki/nssdb

# 4. Web Signer está ativo?
ps aux | grep -i websigner
```

---

## 🔍 TROUBLESHOOTING

### Problema 1: ChromeDriver não conecta

```bash
# Ver logs do ChromeDriver
tail -f /var/log/chromedriver.log

# Verificar porta
netstat -tulpn | grep 4444

# Reiniciar serviço
sudo systemctl restart chromedriver
```

### Problema 2: Certificado não aparece

```bash
# Verificar se está importado
certutil -L -d sql:/root/.pki/nssdb

# Reimportar se necessário
pk12util -i /opt/crawler_tjsp/certs/25424636_pf.pfx -d sql:/root/.pki/nssdb
```

### Problema 3: Xvfb não inicia

```bash
# Ver logs
sudo journalctl -u xvfb -n 50

# Testar manualmente
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
xdpyinfo

# Reiniciar serviço
sudo systemctl restart xvfb
```

### Problema 4: Worker não conecta ao ChromeDriver

```bash
# Verificar network_mode no docker-compose.yml
docker inspect tjsp_worker_1 | grep NetworkMode
# Deve retornar: "NetworkMode": "host"

# Se não estiver, editar docker-compose.yml e rebuild
nano docker-compose.yml
docker compose down
docker compose up -d --build
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de considerar concluído, verificar:

- [ ] Código atualizado do GitHub: `git log -1`
- [ ] Xvfb rodando: `systemctl status xvfb`
- [ ] ChromeDriver rodando: `systemctl status chromedriver`
- [ ] ChromeDriver API respondendo: `curl http://localhost:4444/status`
- [ ] Certificado importado no root: `certutil -L -d sql:/root/.pki/nssdb`
- [ ] docker-compose.yml atualizado: `network_mode: "host"`
- [ ] Worker rodando: `docker ps | grep tjsp_worker`
- [ ] Autenticação com certificado funciona: logs mostram "certificado OK"
- [ ] Processo consultado com sucesso
- [ ] PDFs baixados

---

## 📊 RESUMO DAS MUDANÇAS

### Código (crawler_full.py):
- ✅ **Prioriza certificado digital** ao invés de CPF/senha
- ✅ **Fallback para CPF/senha** se certificado falhar
- ✅ **Melhor tratamento de erros** com mensagens detalhadas

### Infraestrutura:
- ✅ **Xvfb:** Display virtual para Chrome rodar sem interface gráfica
- ✅ **ChromeDriver:** Serviço local na porta 4444
- ✅ **Certificado:** Importado no NSS database do root
- ✅ **Web Signer:** Já instalado e funcionando

### Docker:
- ✅ **network_mode: host:** Worker acessa ChromeDriver local
- ✅ **Removido Selenium Grid:** Não é mais necessário

---

**Última Atualização:** 2025-10-03 03:20:00  
**Autor:** Cascade AI  
**Status:** ✅ PRONTO PARA IMPLEMENTAÇÃO
