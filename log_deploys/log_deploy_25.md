# Autenticaçao 

Perfeito! Agora entendo completamente o contexto. Você está 100% correto - certificado é a ÚNICA opção viável. Vou fazer uma análise profunda e propor soluções práticas.

🔍 ANÁLISE CRÍTICA: Por que Selenium Grid + Docker NÃO funciona
Arquitetura Atual (PROBLEMA):
┌─────────────────────────────────────────────┐
│ Container: selenium-chrome                  │
│ (selenium/standalone-chrome:latest)         │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Chrome Headless                         │ │
│ │ - Sem interface gráfica                 │ │
│ │ - Sem suporte a plugins nativos         │ │
│ │ - Sem acesso a certificados do sistema │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ❌ Web Signer NÃO pode ser instalado       │
│ ❌ Certificado .pfx não pode ser carregado │
│ ❌ Diálogos nativos não funcionam          │
└─────────────────────────────────────────────┘
Por que não funciona:

❌ Container isolado: Não tem acesso ao sistema de certificados
❌ Headless: Web Signer precisa de display gráfico
❌ Plugin nativo: Não pode ser instalado em container
❌ Imagem pré-construída: Não podemos modificar facilmente
💡 SOLUÇÕES VIÁVEIS (Análise Profunda)
🎯 OPÇÃO A: Xvfb + Chrome FORA do Docker (RECOMENDADO)
Por que ABANDONAR o Selenium Grid atual:

O Selenium Grid com containers Docker é incompatível com Web Signer. Precisamos de:

Chrome instalado diretamente no Ubuntu (não em container)
Web Signer instalado no sistema
Xvfb para criar display virtual
Certificado importado no sistema
Nova Arquitetura Proposta:

┌─────────────────────────────────────────────────────────┐
│ VPS Ubuntu (srv987902) - Host Direto                    │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ 1. Xvfb (Display Virtual :99)                        ││
│ │    - Cria framebuffer em memória                     ││
│ │    - Simula ambiente gráfico                         ││
│ │    export DISPLAY=:99                                ││
│ └──────────────────────────────────────────────────────┘│
│                          ↓                               │
│ ┌──────────────────────────────────────────────────────┐│
│ │ 2. Chrome (Instalado no Ubuntu, não Docker)          ││
│ │    - Roda em modo não-headless no Xvfb               ││
│ │    - Web Signer instalado e funcionando              ││
│ │    - Certificado A1 importado no sistema             ││
│ └──────────────────────────────────────────────────────┘│
│                          ↓                               │
│ ┌──────────────────────────────────────────────────────┐│
│ │ 3. ChromeDriver (Local, não Grid)                    ││
│ │    - Conecta ao Chrome local                         ││
│ │    - Usa DISPLAY=:99                                 ││
│ └──────────────────────────────────────────────────────┘│
│                          ↓                               │
│ ┌──────────────────────────────────────────────────────┐│
│ │ 4. Worker Python (Container Docker)                  ││
│ │    - Conecta ao ChromeDriver via rede                ││
│ │    - PostgreSQL (mantém container)                   ││
│ │    - Código Python (mantém container)                ││
│ └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
Vantagens:

✅ Web Signer funciona 100%
✅ Certificado A1 utilizável
✅ Mantém worker Python em Docker
✅ Mantém PostgreSQL em Docker
✅ Apenas Chrome sai do Docker
Desvantagens:

⚠️ Chrome não está mais isolado em container
⚠️ Precisa manter Xvfb rodando
⚠️ Menos "limpo" que solução 100% Docker
🔧 OPÇÃO B: Selenium Grid com Node Xvfb (HÍBRIDO)
Ideia: Manter Grid, mas com node customizado

┌────────────────────────────────────────────────────────┐
│ VPS Ubuntu                                             │
│                                                        │
│ ┌────────────────────┐    ┌─────────────────────────┐ │
│ │ Container: Hub     │    │ Host: Selenium Node     │ │
│ │ (Grid Hub)         │◄───│ - Xvfb :99              │ │
│ │ - Coordena jobs    │    │ - Chrome + Web Signer   │ │
│ └────────────────────┘    │ - ChromeDriver          │ │
│          ↑                │ - Certificado A1        │ │
│          │                └─────────────────────────┘ │
│ ┌────────────────────┐                                │
│ │ Container: Worker  │                                │
│ │ - Python           │                                │
│ │ - PostgreSQL       │                                │
│ └────────────────────┘                                │
└────────────────────────────────────────────────────────┘
Vantagens:

✅ Mantém conceito de Grid
✅ Worker continua em Docker
✅ Web Signer funciona
Desvantagens:

⚠️ Node não está em container
⚠️ Configuração mais complexa
🚀 OPÇÃO C: Container Customizado com Xvfb (IDEAL, mas complexo)
Ideia: Criar imagem Docker customizada com tudo incluído

dockerfile
FROM selenium/standalone-chrome:latest

# Instalar Xvfb
RUN apt-get update && apt-get install -y xvfb x11vnc

# Instalar Web Signer
COPY websigner.deb /tmp/
RUN dpkg -i /tmp/websigner.deb || apt-get install -f -y

# Configurar certificado
COPY certificado.pfx /root/.certificados/
RUN # Importar certificado para o sistema

# Script de inicialização
COPY start-with-xvfb.sh /opt/bin/
RUN chmod +x /opt/bin/start-with-xvfb.sh

ENTRYPOINT ["/opt/bin/start-with-xvfb.sh"]
Vantagens:

✅ Mantém tudo em Docker
✅ Mantém Selenium Grid atual
✅ Solução mais "limpa"
Desvantagens:

❌ MUITO COMPLEXO de fazer funcionar
❌ Web Signer pode não funcionar em container
❌ Certificado pode não ser reconhecido
❌ Alto risco de não funcionar
🎯 RECOMENDAÇÃO: OPÇÃO A (Xvfb + Chrome no Host)
Por que esta é a melhor opção:
✅ Comprovadamente funciona: Xvfb é solução padrão
✅ Menor risco: Web Signer funciona em Ubuntu
✅ Mantém worker em Docker: Apenas Chrome sai
✅ Tempo de implementação: 6-8 horas
✅ Debugável: Pode usar VNC para ver o que acontece
📋 PLANO DE IMPLEMENTAÇÃO DETALHADO
FASE 1: Preparação (1-2 horas)
bash
# 1. Conectar na VPS
ssh root@srv987902.hstgr.cloud

# 2. Parar Selenium Grid atual (vamos substituir)
cd /opt/crawler_tjsp
docker compose stop selenium-chrome
# Não deletar ainda, apenas parar

# 3. Instalar dependências
sudo apt update
sudo apt install -y xvfb x11vnc wget
FASE 2: Instalar Chrome no Host (30 min)
bash
# 1. Baixar e instalar Chrome
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 2. Verificar instalação
google-chrome --version
# Deve mostrar: Google Chrome 131.x.x.x

# 3. Instalar ChromeDriver (mesma versão do Chrome)
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}
CHROMEDRIVER_VERSION=$(cat LATEST_RELEASE_${CHROME_VERSION})
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 4. Verificar ChromeDriver
chromedriver --version
FASE 3: Instalar Web Signer (30 min)
bash
# 1. Baixar Web Signer para Ubuntu
cd /tmp
wget https://websigner.softplan.com.br/Downloads/Instalador/Linux/WebSigner_Ubuntu_x64.deb

# 2. Instalar
sudo dpkg -i WebSigner_Ubuntu_x64.deb
# Se der erro de dependências:
sudo apt-get install -f -y

# 3. Verificar instalação
ls -la /opt/WebSigner/
# Deve mostrar arquivos do Web Signer
FASE 4: Configurar Certificado (30 min)
bash
# 1. Criar diretório para certificados
mkdir -p /root/.certificados
chmod 700 /root/.certificados

# 2. Copiar certificado .pfx
cp /opt/crawler_tjsp/certs/25424636_pf.pfx /root/.certificados/

# 3. Importar certificado para o sistema (NSS database)
# Chrome usa NSS para certificados
mkdir -p /root/.pki/nssdb
certutil -N -d sql:/root/.pki/nssdb --empty-password

# 4. Importar .pfx
pk12util -i /root/.certificados/25424636_pf.pfx -d sql:/root/.pki/nssdb
# Vai pedir senha: 903205

# 5. Listar certificados importados
certutil -L -d sql:/root/.pki/nssdb
# Deve mostrar o certificado
FASE 5: Configurar Xvfb (30 min)
bash
# 1. Criar script de inicialização do Xvfb
cat > /opt/start-xvfb.sh << 'EOF'
#!/bin/bash
# Inicia Xvfb no display :99
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
echo "Xvfb iniciado com PID: $XVFB_PID"
echo $XVFB_PID > /var/run/xvfb.pid

# Aguardar Xvfb iniciar
sleep 2

# Exportar DISPLAY
export DISPLAY=:99

# Verificar se Xvfb está rodando
if ps -p $XVFB_PID > /dev/null; then
   echo "✅ Xvfb rodando no DISPLAY :99"
else
   echo "❌ Erro ao iniciar Xvfb"
   exit 1
fi
EOF

chmod +x /opt/start-xvfb.sh

# 2. Criar serviço systemd para Xvfb
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

# 3. Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable xvfb
sudo systemctl start xvfb

# 4. Verificar status
sudo systemctl status xvfb
export DISPLAY=:99
FASE 6: Testar Chrome + Web Signer (1 hora)
bash
# 1. Testar Chrome no Xvfb
export DISPLAY=:99
google-chrome --no-sandbox --disable-dev-shm-usage https://websigner.softplan.com.br/Setup &

# 2. (Opcional) Configurar VNC para ver o que está acontecendo
x11vnc -display :99 -bg -nopw -listen localhost -xkb -forever
# Criar túnel SSH para acessar VNC:
# No seu Mac: ssh -L 5900:localhost:5900 root@srv987902.hstgr.cloud
# Abrir VNC Viewer: localhost:5900

# 3. Testar acesso ao TJSP
google-chrome --no-sandbox --disable-dev-shm-usage https://esaj.tjsp.jus.br/sajcas/login &

# 4. Verificar se Web Signer está ativo
# Acessar via VNC e verificar se certificado aparece
FASE 7: Modificar Código Python (2 horas)
Precisamos modificar 
crawler_full.py
 para conectar ao Chrome local em vez do Grid:

Perfeito! O código já está preparado para usar variável de ambiente. Agora vou criar o plano completo:

📋 PLANO COMPLETO DE IMPLEMENTAÇÃO
FASE 7: Modificar docker-compose.yml (30 min)
Vamos modificar para que o worker conecte ao ChromeDriver local (não Grid):

bash
# Na VPS
cd /opt/crawler_tjsp
nano docker-compose.yml
Modificar para:

yaml
version: '3.8'

services:
  # REMOVIDO: selenium-chrome (não precisamos mais)
  # Agora usamos Chrome + Xvfb no host
  
  worker:
    build: .
    image: tjsp-worker:latest
    container_name: tjsp_worker_1
    
    # MODIFICADO: Conecta ao ChromeDriver no host
    environment:
      # Banco de dados
      - DB_HOST=72.60.62.124
      - DB_PORT=5432
      - DB_NAME=n8n
      - DB_USER=admin
      - DB_PASSWORD=${DB_PASSWORD}
      
      # NOVO: ChromeDriver local (não Grid)
      # Removido: SELENIUM_REMOTE_URL
      # Worker vai usar Chrome local via network host
      
      # Certificado (para auto-seleção)
      - CERT_PATH=/app/certs/25424636_pf.pfx
      - CERT_PASSWORD=903205
      - CERT_SUBJECT_CN=517.648.902-30
      - CERT_ISSUER_CN=AC Certisign Múltipla G5
      
      # Autenticação (não será usada, mas mantém)
      - CAS_USUARIO=${CAS_USUARIO}
      - CAS_SENHA=${CAS_SENHA}
    
    # IMPORTANTE: network_mode host para acessar ChromeDriver
    network_mode: "host"
    
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots
      - ./certs:/app/certs
    
    restart: unless-stopped
FASE 8: Criar Serviço ChromeDriver (1 hora)
Precisamos de um serviço que mantenha ChromeDriver rodando:

bash
# 1. Criar script de inicialização do ChromeDriver
cat > /opt/start-chromedriver.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99

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
sleep 2

# Verificar se está rodando
if ps -p $CHROMEDRIVER_PID > /dev/null; then
   echo "✅ ChromeDriver rodando na porta 4444"
else
   echo "❌ Erro ao iniciar ChromeDriver"
   exit 1
fi

# Manter script rodando
wait $CHROMEDRIVER_PID
EOF

chmod +x /opt/start-chromedriver.sh

# 2. Criar serviço systemd
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

# 3. Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable chromedriver
sudo systemctl start chromedriver

# 4. Verificar
sudo systemctl status chromedriver
curl http://localhost:4444/status
FASE 9: Modificar Código Python (1 hora)
O código já está quase pronto, mas precisamos ajustar para conectar ao ChromeDriver local:

crawler_full.py
+9
-2
Agora vamos adicionar suporte para conectar ao ChromeDriver local:

Agora vou adicionar suporte para ChromeDriver local via Remote WebDriver (para usar Xvfb):

crawler_full.py
+19
Perfeito! Agora vou criar um documento completo com todo o plano:

PLANO_XVFB_WEBSIGNER.md
new
+705
Agora vou atualizar o DEPLOY_TRACKING.md e commitar tudo: