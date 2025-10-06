@echo off
REM Script para iniciar Chrome com Remote Debugging - V2
REM Adiciona --remote-allow-origins=* para Chrome moderno

echo ======================================
echo CHROME REMOTE DEBUGGING - V2
echo ======================================
echo.

REM Fechar Chrome existente
echo Fechando Chrome...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo Chrome fechado.
echo.

REM Iniciar Chrome com Remote Debugging + CORS
echo Iniciando Chrome...
echo Porta: 9222
echo Argumentos adicionais:
echo   --remote-allow-origins=*  (permite Selenium conectar)
echo.

REM COMANDO COM --remote-allow-origins
start "Chrome Debug" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=*

echo.
echo Chrome iniciado!
echo.

REM Aguardar Chrome carregar
echo Aguardando 8 segundos...
timeout /t 8 /nobreak >nul

echo.
echo Testando porta 9222...
curl -s http://localhost:9222/json/version

echo.
echo.
echo Se aparecer JSON acima, Remote Debugging ESTA ATIVO!
echo Se nao aparecer nada, porta 9222 NAO esta escutando.
echo.
echo Para testar Selenium:
echo   python windows-server\scripts\test_authentication_remote_v2.py
echo.

pause
