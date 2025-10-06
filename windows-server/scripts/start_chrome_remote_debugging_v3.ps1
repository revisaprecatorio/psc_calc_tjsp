# Script para iniciar Chrome com Remote Debugging - VERSAO 3
# SOLUCAO DEFINITIVA: Usa mesma linha de comando do icone + remote debugging

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "CHROME COM REMOTE DEBUGGING - V3" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Fechar Chrome se estiver aberto
Write-Host "Fechando Chrome existente..." -ForegroundColor Yellow
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Write-Host "Chrome fechado." -ForegroundColor Green
Write-Host ""

# Caminho do Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9222

Write-Host "Iniciando Chrome com Remote Debugging..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuracao:" -ForegroundColor Yellow
Write-Host "  Executavel: $chromePath" -ForegroundColor White
Write-Host "  Remote Debugging Port: $debugPort" -ForegroundColor White
Write-Host "  Perfil: Default (ultimo usado - revisa.precatorio@gmail.com)" -ForegroundColor White
Write-Host ""

# METODO DEFINITIVO: cmd.exe para passar argumentos corretamente
# Mesmo comportamento do icone + remote debugging
try {
    $cmdArgs = "/c start `"Chrome Remote Debugging`" `"$chromePath`" --remote-debugging-port=$debugPort"

    Write-Host "Executando comando:" -ForegroundColor Gray
    Write-Host "  cmd.exe $cmdArgs" -ForegroundColor DarkGray
    Write-Host ""

    Start-Process "cmd.exe" -ArgumentList $cmdArgs -WindowStyle Hidden

    Write-Host "Comando enviado!" -ForegroundColor Green
    Write-Host ""

    # Aguardar Chrome carregar
    Write-Host "Aguardando Chrome carregar (8 segundos)..." -ForegroundColor Cyan
    Start-Sleep -Seconds 8

    # Verificar se porta 9222 esta ativa
    Write-Host ""
    Write-Host "Verificando porta de Remote Debugging..." -ForegroundColor Cyan

    $maxRetries = 3
    $retryCount = 0
    $connected = $false

    while ($retryCount -lt $maxRetries -and -not $connected) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$debugPort/json/version" -UseBasicParsing -TimeoutSec 5
            $versionInfo = $response.Content | ConvertFrom-Json

            Write-Host ""
            Write-Host "=====================================" -ForegroundColor Green
            Write-Host "REMOTE DEBUGGING ATIVO!" -ForegroundColor Green
            Write-Host "=====================================" -ForegroundColor Green
            Write-Host "  Browser: $($versionInfo.Browser)" -ForegroundColor White
            Write-Host "  User Agent: $($versionInfo.'User-Agent')" -ForegroundColor White
            Write-Host "  WebSocket: $($versionInfo.webSocketDebuggerUrl)" -ForegroundColor White
            Write-Host ""

            $connected = $true

        } catch {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "Tentativa $retryCount falhou, aguardando 3 segundos..." -ForegroundColor Yellow
                Start-Sleep -Seconds 3
            } else {
                Write-Host ""
                Write-Host "AVISO: Nao foi possivel verificar porta $debugPort" -ForegroundColor Red
                Write-Host "  Erro: $($_.Exception.Message)" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "TROUBLESHOOTING:" -ForegroundColor Yellow
                Write-Host "  1. Verifique se Chrome abriu (deve estar visivel)" -ForegroundColor White
                Write-Host "  2. Abra novo Chrome e acesse: http://localhost:$debugPort" -ForegroundColor White
                Write-Host "  3. Se mostrar JSON com tabs, Remote Debugging ESTA funcionando" -ForegroundColor White
                Write-Host "  4. Se nao mostrar nada, Chrome nao iniciou com --remote-debugging-port" -ForegroundColor White
                Write-Host ""
                Write-Host "SOLUCAO MANUAL:" -ForegroundColor Cyan
                Write-Host "  1. Feche Chrome: Stop-Process -Name chrome -Force" -ForegroundColor White
                Write-Host "  2. Execute manualmente:" -ForegroundColor White
                Write-Host "     & `"$chromePath`" --remote-debugging-port=$debugPort" -ForegroundColor Gray
                Write-Host ""
            }
        }
    }

    if ($connected) {
        Write-Host "SUCESSO! Chrome esta pronto para Selenium." -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANTE:" -ForegroundColor Cyan
        Write-Host "  - Chrome ficara ABERTO" -ForegroundColor White
        Write-Host "  - Perfil: revisa.precatorio@gmail.com" -ForegroundColor White
        Write-Host "  - Web Signer carregado automaticamente" -ForegroundColor White
        Write-Host "  - Selenium conecta na porta $debugPort" -ForegroundColor White
        Write-Host ""
        Write-Host "NAO FECHE CHROME!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Para testar Selenium:" -ForegroundColor Cyan
        Write-Host "  python windows-server\scripts\test_authentication_remote.py" -ForegroundColor White
        Write-Host ""
    }

} catch {
    Write-Host "ERRO ao iniciar Chrome: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "Pressione qualquer tecla para fechar este script..." -ForegroundColor Gray
Write-Host "(Chrome continuara rodando)" -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
