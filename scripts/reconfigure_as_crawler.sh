#!/bin/bash
# Script para Reconfigurar ChromeDriver e Xvfb para rodar como usuário crawler

echo "================================================================================"
echo "RECONFIGURANDO PARA USAR USUÁRIO CRAWLER"
echo "================================================================================"

# 1. Parar serviços
echo ""
echo "[1] Parando serviços..."
systemctl stop chromedriver
systemctl stop xvfb

# 2. Reconfigurar Xvfb para rodar como crawler
echo ""
echo "[2] Reconfigurando Xvfb para usuário crawler..."

cat > /etc/systemd/system/xvfb.service << 'EOF'
[Unit]
Description=X Virtual Frame Buffer Service
After=network.target

[Service]
Type=simple
User=crawler
Group=crawler
Environment="DISPLAY=:99"
ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Xvfb configurado para usuário crawler"

# 3. Reconfigurar ChromeDriver para rodar como crawler
echo ""
echo "[3] Reconfigurando ChromeDriver para usuário crawler..."

cat > /etc/systemd/system/chromedriver.service << 'EOF'
[Unit]
Description=ChromeDriver for Selenium
After=xvfb.service
Requires=xvfb.service

[Service]
Type=simple
User=crawler
Group=crawler
Environment="DISPLAY=:99"
ExecStart=/usr/local/bin/chromedriver --port=4444 --whitelisted-ips="" --verbose --log-path=/var/log/chromedriver.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ ChromeDriver configurado para usuário crawler"

# 4. Ajustar permissões do log
echo ""
echo "[4] Ajustando permissões..."
touch /var/log/chromedriver.log
chown crawler:crawler /var/log/chromedriver.log

# 5. Recarregar systemd
echo ""
echo "[5] Recarregando systemd..."
systemctl daemon-reload

# 6. Iniciar serviços
echo ""
echo "[6] Iniciando serviços..."
systemctl start xvfb
sleep 2
systemctl start chromedriver
sleep 2

# 7. Verificar status
echo ""
echo "[7] Verificando status..."
echo ""
echo "=== Xvfb ==="
systemctl status xvfb --no-pager | grep "Active:"

echo ""
echo "=== ChromeDriver ==="
systemctl status chromedriver --no-pager | grep "Active:"

# 8. Testar API
echo ""
echo "[8] Testando API do ChromeDriver..."
sleep 3
curl -s http://localhost:4444/status | grep -o '"ready":true' && echo "✅ ChromeDriver respondendo!" || echo "❌ ChromeDriver não está respondendo"

echo ""
echo "================================================================================"
echo "RECONFIGURAÇÃO CONCLUÍDA!"
echo "================================================================================"
echo ""
echo "Próximos passos:"
echo "  1. Verifique se os serviços estão rodando"
echo "  2. Faça login no Google via RDP (como crawler)"
echo "  3. Execute: python3 verify_google_login.py"
echo ""
