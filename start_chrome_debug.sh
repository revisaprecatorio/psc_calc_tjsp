#!/bin/bash
# Script para iniciar Chrome com Remote Debugging
# Permite Selenium conectar ao Chrome que já está rodando

echo "🚀 Iniciando Chrome com Remote Debugging..."
echo ""

# Matar Chrome se estiver rodando
echo "1. Verificando se Chrome está rodando..."
if pgrep -f "google-chrome" > /dev/null; then
    echo "   ⚠️ Chrome está rodando. Fechando..."
    pkill -f "google-chrome"
    sleep 3
else
    echo "   ✅ Chrome não está rodando"
fi

# Iniciar Chrome com remote debugging
echo ""
echo "2. Iniciando Chrome com Remote Debugging..."
echo "   Porta: 9222"
echo "   Display: :99"
echo "   Perfil: /home/crawler/.config/google-chrome"
echo ""

DISPLAY=:99 /usr/bin/google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir=/home/crawler/.config/google-chrome \
    --no-sandbox \
    --disable-dev-shm-usage \
    --no-first-run \
    --no-default-browser-check \
    --disable-popup-blocking \
    --disable-infobars \
    > /tmp/chrome_debug.log 2>&1 &

CHROME_PID=$!

echo "✅ Chrome iniciado!"
echo "   PID: $CHROME_PID"
echo "   Remote Debugging: http://localhost:9222"
echo ""
echo "📋 Próximos passos:"
echo "   1. Conecte via RDP"
echo "   2. Abra Chrome (já deve estar aberto)"
echo "   3. Faça login no Google (se necessário)"
echo "   4. Instale/ative extensão Web Signer (se necessário)"
echo "   5. Execute teste Selenium: python3 test_selenium_remote_debug.py"
echo ""
echo "🔍 Para verificar se está funcionando:"
echo "   curl http://localhost:9222/json"
echo ""
echo "⚠️ IMPORTANTE: NÃO feche este Chrome!"
echo "   Selenium vai conectar a ele."
