@echo off
REM Script para iniciar Chrome com Remote Debugging
REM Arquivo .bat e mais confiavel que PowerShell para passar argumentos

echo ======================================
echo INICIAR CHROME COM REMOTE DEBUGGING
echo ======================================
echo.

REM Fechar Chrome existente
echo Fechando Chrome existente...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 3 /nobreak >nul
echo Chrome fechado.
echo.

REM Iniciar Chrome com Remote Debugging
echo Iniciando Chrome com Remote Debugging...
echo Porta: 9222
echo Perfil: Default (revisa.precatorio@gmail.com)
echo.

REM COMANDO DIRETO - mais confiavel
start "Chrome Remote Debugging" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

echo.
echo Chrome iniciado!
echo.
echo IMPORTANTE:
echo   - NAO FECHE a janela do Chrome
echo   - Chrome esta rodando com Remote Debugging na porta 9222
echo.

REM Aguardar Chrome carregar
echo Aguardando Chrome carregar (5 segundos)...
timeout /t 5 /nobreak >nul

echo.
echo Para testar Selenium:
echo   python windows-server\scripts\test_authentication_remote.py
echo.

pause
