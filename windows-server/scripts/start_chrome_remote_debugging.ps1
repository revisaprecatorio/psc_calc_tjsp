# Script para iniciar Chrome com Remote Debugging
# Execute UMA vez ao ligar o servidor
# Chrome fica aberto e Selenium conecta nele

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

# User Data Directory (IMPORTANTE: usar o Default para ter Web Signer)
$userDataDir = "C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"

Write-Host "Iniciando Chrome com Remote Debugging..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuracao:" -ForegroundColor Yellow
Write-Host "  Executavel: $chromePath" -ForegroundColor White
Write-Host "  Remote Debugging Port: $debugPort" -ForegroundColor White
Write-Host "  User Data Dir: $userDataDir" -ForegroundColor White
Write-Host "  Profile: Default (revisa.precatorio@gmail.com)" -ForegroundColor White
Write-Host ""

# Argumentos do Chrome
$arguments = @(
    "--remote-debugging-port=$debugPort"
    "--user-data-dir=`"$userDataDir`""
    "--no-first-run"
    "--no-default-browser-check"
)

# Iniciar Chrome
try {
    $process = Start-Process -FilePath $chromePath -ArgumentList $arguments -PassThru

    Write-Host "Chrome iniciado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes:" -ForegroundColor Yellow
    Write-Host "  PID: $($process.Id)" -ForegroundColor White
    Write-Host "  Remote Debugging: http://localhost:$debugPort" -ForegroundColor White
    Write-Host ""
    Write-Host "IMPORTANTE:" -ForegroundColor Cyan
    Write-Host "  - Chrome ficara ABERTO" -ForegroundColor White
    Write-Host "  - Perfil: revisa.precatorio@gmail.com" -ForegroundColor White
    Write-Host "  - Web Signer carregado automaticamente" -ForegroundColor White
    Write-Host "  - Selenium pode conectar na porta $debugPort" -ForegroundColor White
    Write-Host ""
    Write-Host "NAO FECHE ESTA JANELA DO CHROME!" -ForegroundColor Red
    Write-Host "Selenium vai controlar este Chrome." -ForegroundColor Red
    Write-Host ""
    Write-Host "Para testar Selenium:" -ForegroundColor Cyan
    Write-Host "  python windows-server\scripts\test_authentication.py" -ForegroundColor White
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
