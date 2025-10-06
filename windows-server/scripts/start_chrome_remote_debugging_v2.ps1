# Script para iniciar Chrome com Remote Debugging - VERSAO 2
# Corrige problema de passagem de argumentos no Start-Process

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "INICIAR CHROME COM REMOTE DEBUGGING" -ForegroundColor Cyan
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

# Porta de Remote Debugging
$debugPort = 9222

Write-Host "Iniciando Chrome com Remote Debugging..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuracao:" -ForegroundColor Yellow
Write-Host "  Executavel: $chromePath" -ForegroundColor White
Write-Host "  Remote Debugging Port: $debugPort" -ForegroundColor White
Write-Host "  Perfil: Default (abre ultimo perfil usado)" -ForegroundColor White
Write-Host ""

# Iniciar Chrome com argumentos
try {
    # METODO SIMPLES: Passar argumentos diretamente
    # Chrome vai usar perfil Default automaticamente (revisa.precatorio@gmail.com)
    $process = Start-Process -FilePath $chromePath -ArgumentList "--remote-debugging-port=$debugPort" -PassThru

    Write-Host "Chrome iniciado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes:" -ForegroundColor Yellow
    Write-Host "  PID: $($process.Id)" -ForegroundColor White
    Write-Host "  Remote Debugging: http://localhost:$debugPort" -ForegroundColor White
    Write-Host ""

    # Aguardar Chrome carregar
    Write-Host "Aguardando Chrome carregar (5 segundos)..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5

    # Verificar se porta 9222 esta ativa
    Write-Host ""
    Write-Host "Verificando porta de Remote Debugging..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$debugPort/json/version" -UseBasicParsing -TimeoutSec 5
        $versionInfo = $response.Content | ConvertFrom-Json

        Write-Host "Remote Debugging ATIVO!" -ForegroundColor Green
        Write-Host "  Browser: $($versionInfo.Browser)" -ForegroundColor White
        Write-Host "  WebSocket: $($versionInfo.webSocketDebuggerUrl)" -ForegroundColor White
        Write-Host ""

    } catch {
        Write-Host "AVISO: Nao foi possivel verificar porta $debugPort" -ForegroundColor Yellow
        Write-Host "  Erro: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Isso pode significar:" -ForegroundColor Yellow
        Write-Host "  1. Chrome ainda esta inicializando (aguarde mais)" -ForegroundColor White
        Write-Host "  2. Remote debugging nao foi ativado" -ForegroundColor White
        Write-Host ""
    }

    Write-Host "IMPORTANTE:" -ForegroundColor Cyan
    Write-Host "  - Chrome ficara ABERTO" -ForegroundColor White
    Write-Host "  - Perfil: revisa.precatorio@gmail.com (ultimo usado)" -ForegroundColor White
    Write-Host "  - Web Signer carregado automaticamente" -ForegroundColor White
    Write-Host "  - Selenium pode conectar na porta $debugPort" -ForegroundColor White
    Write-Host ""
    Write-Host "NAO FECHE ESTA JANELA DO CHROME!" -ForegroundColor Red
    Write-Host "Selenium vai controlar este Chrome." -ForegroundColor Red
    Write-Host ""
    Write-Host "Para testar Selenium:" -ForegroundColor Cyan
    Write-Host "  python windows-server\scripts\test_authentication_remote.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Para verificar manualmente se Remote Debugging esta ativo:" -ForegroundColor Cyan
    Write-Host "  1. Abra novo Chrome" -ForegroundColor White
    Write-Host "  2. Acesse: http://localhost:$debugPort" -ForegroundColor White
    Write-Host "  3. Deve mostrar lista de paginas abertas" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "ERRO ao iniciar Chrome: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique:" -ForegroundColor Yellow
    Write-Host "  1. Chrome esta instalado em: $chromePath" -ForegroundColor White
    Write-Host "  2. Porta $debugPort nao esta em uso" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Pressione qualquer tecla para fechar este script..." -ForegroundColor Gray
Write-Host "(Chrome continuara rodando em background)" -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
