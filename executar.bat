@echo off
echo --- ORQUESTRADOR DE FILA TJSP ---

:: 1. Limpeza inicial (Garante que a porta 9222 esteja livre)
echo [1/3] Limpando processos antigos...
taskkill /F /IM chrome.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

:: 2. Abre o Chrome Mestre (Com configurações anti-popup e certificado)
echo [2/3] Abrindo Chrome Debugger (Instancia Unica)...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Temp\ChromeDebug" --disable-popup-blocking --default-download-path="C:\Temp\RevisaDownloads" --no-first-run --no-default-browser-check

:: 3. Espera o Chrome estar pronto
echo Aguardando 5 segundos para inicializacao do Chrome...
timeout /t 5 /nobreak >nul

:: 4. Ativa o ambiente e roda o Orquestrador
echo [3/3] Iniciando processamento da fila do Banco de Dados...
call env\Scripts\activate

:: AQUI ESTÁ A MÁGICA: Chamamos o orquestrador, não o crawler direto
python orchestrator_subprocess.py

echo.
echo --- PROCESSO FINALIZADO ---
pause