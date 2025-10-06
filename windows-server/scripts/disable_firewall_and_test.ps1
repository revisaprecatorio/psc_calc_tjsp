# Script para desabilitar Firewall e testar Remote Debugging
# ATENCAO: Desabilita TODAS as protecoes para diagnostico

Write-Host "======================================" -ForegroundColor Red
Write-Host "DESABILITAR FIREWALL E TESTAR" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Red
Write-Host ""
Write-Host "ATENCAO: Este script vai:" -ForegroundColor Yellow
Write-Host "  1. Desabilitar Firewall Windows COMPLETAMENTE" -ForegroundColor White
Write-Host "  2. Matar TODAS as instancias Chrome" -ForegroundColor White
Write-Host "  3. Desabilitar Chrome security policies" -ForegroundColor White
Write-Host "  4. Testar Remote Debugging" -ForegroundColor White
Write-Host ""
Write-Host "Isso e PERIGOSO em producao!" -ForegroundColor Red
Write-Host "Use apenas para diagnostico!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Deseja continuar? (digite SIM)"
if ($confirm -ne "SIM") {
    Write-Host "Cancelado." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PASSO 1: DESABILITAR FIREWALL" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar status atual do Firewall
Write-Host "Status atual do Firewall:" -ForegroundColor Yellow
Get-NetFirewallProfile | Select-Object Name, Enabled

Write-Host ""
Write-Host "Desabilitando Firewall em TODOS os perfis..." -ForegroundColor Yellow

try {
    # Desabilitar Firewall para todos os perfis
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

    Write-Host "Firewall DESABILITADO!" -ForegroundColor Green
    Write-Host ""

    # Verificar novo status
    Write-Host "Novo status:" -ForegroundColor Yellow
    Get-NetFirewallProfile | Select-Object Name, Enabled

} catch {
    Write-Host "ERRO ao desabilitar Firewall: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Talvez seja necessario executar como Administrator" -ForegroundColor Yellow
    Write-Host "Clique com botao direito no PowerShell > Executar como Administrador" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PASSO 2: MATAR CHROME" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Listar processos Chrome antes
Write-Host "Processos Chrome ANTES:" -ForegroundColor Yellow
$beforeCount = (Get-Process chrome -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Total: $beforeCount processos" -ForegroundColor White

# Matar TODOS os processos Chrome
Write-Host ""
Write-Host "Matando TODOS os processos Chrome..." -ForegroundColor Yellow
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue

# Aguardar
Start-Sleep -Seconds 5

# Verificar se ainda tem algum
Write-Host ""
Write-Host "Processos Chrome DEPOIS:" -ForegroundColor Yellow
$afterCount = (Get-Process chrome -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Total: $afterCount processos" -ForegroundColor White

if ($afterCount -eq 0) {
    Write-Host "  Todos os processos Chrome foram encerrados!" -ForegroundColor Green
} else {
    Write-Host "  ATENCAO: Ainda existem $afterCount processos Chrome rodando!" -ForegroundColor Red
    Write-Host "  Listando:" -ForegroundColor Yellow
    Get-Process chrome | Select-Object Id, ProcessName, StartTime
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PASSO 3: ABRIR CHROME SEM SECURITY" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9222

Write-Host "Iniciando Chrome com:" -ForegroundColor Yellow
Write-Host "  --remote-debugging-port=$debugPort" -ForegroundColor White
Write-Host "  --remote-allow-origins=*" -ForegroundColor White
Write-Host "  --disable-web-security" -ForegroundColor White
Write-Host "  --disable-features=IsolateOrigins,site-per-process" -ForegroundColor White
Write-Host "  --no-sandbox" -ForegroundColor White
Write-Host "  --disable-setuid-sandbox" -ForegroundColor White
Write-Host ""

# Argumentos Chrome (SEM NENHUMA SEGURANCA)
$chromeArgs = @(
    "--remote-debugging-port=$debugPort",
    "--remote-allow-origins=*",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-software-rasterizer"
)

# Iniciar Chrome
try {
    $process = Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -PassThru
    Write-Host "Chrome iniciado (PID: $($process.Id))" -ForegroundColor Green
} catch {
    Write-Host "ERRO ao iniciar Chrome: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Aguardar Chrome carregar
Write-Host ""
Write-Host "Aguardando Chrome carregar (10 segundos)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PASSO 4: TESTAR PORTA 9222" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se porta esta escutando (netstat)
Write-Host "Verificando porta $debugPort com netstat..." -ForegroundColor Yellow
$netstatResult = netstat -ano | Select-String ":$debugPort"

if ($netstatResult) {
    Write-Host "Porta $debugPort ENCONTRADA:" -ForegroundColor Green
    $netstatResult | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} else {
    Write-Host "Porta $debugPort NAO ENCONTRADA no netstat!" -ForegroundColor Red
}

# Testar com Invoke-WebRequest
Write-Host ""
Write-Host "Testando HTTP na porta $debugPort..." -ForegroundColor Yellow

$maxRetries = 5
$success = $false

for ($i = 1; $i -le $maxRetries; $i++) {
    Write-Host "  Tentativa $i de $maxRetries..." -ForegroundColor Gray

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$debugPort/json/version" -UseBasicParsing -TimeoutSec 5
        $versionInfo = $response.Content | ConvertFrom-Json

        Write-Host ""
        Write-Host "====================================" -ForegroundColor Green
        Write-Host "SUCESSO! REMOTE DEBUGGING ATIVO!" -ForegroundColor Green
        Write-Host "====================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Informacoes:" -ForegroundColor Yellow
        Write-Host "  Browser: $($versionInfo.Browser)" -ForegroundColor White
        Write-Host "  Protocol: $($versionInfo.'Protocol-Version')" -ForegroundColor White
        Write-Host "  WebSocket: $($versionInfo.webSocketDebuggerUrl)" -ForegroundColor White
        Write-Host ""

        $success = $true
        break

    } catch {
        if ($i -lt $maxRetries) {
            Write-Host "    Falhou, aguardando 3 segundos..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
}

if (-not $success) {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "FALHA! PORTA $debugPort NAO RESPONDE" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possibilidades:" -ForegroundColor Yellow
    Write-Host "  1. Chrome nao aceitou argumento --remote-debugging-port" -ForegroundColor White
    Write-Host "  2. Porta bloqueada por outro processo/politica" -ForegroundColor White
    Write-Host "  3. Bug especifico Windows Server 2016" -ForegroundColor White
    Write-Host ""
    Write-Host "TESTE MANUAL:" -ForegroundColor Cyan
    Write-Host "  1. Abra Chrome manualmente (ja esta aberto)" -ForegroundColor White
    Write-Host "  2. Acesse: http://localhost:$debugPort" -ForegroundColor White
    Write-Host "  3. Deve mostrar lista de paginas abertas" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Firewall: DESABILITADO" -ForegroundColor White
Write-Host "Chrome: RODANDO (PID: $($process.Id))" -ForegroundColor White
Write-Host "Security Policies: DESABILITADAS" -ForegroundColor White
Write-Host "Remote Debugging: $(if ($success) { 'FUNCIONANDO' } else { 'FALHOU' })" -ForegroundColor $(if ($success) { 'Green' } else { 'Red' })
Write-Host ""

if ($success) {
    Write-Host "PROXIMO PASSO:" -ForegroundColor Green
    Write-Host "  Execute em OUTRO terminal:" -ForegroundColor White
    Write-Host "    python windows-server\scripts\test_authentication_remote_v2.py" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "DIAGNOSTICO:" -ForegroundColor Red
    Write-Host "  Remote Debugging NAO funciona mesmo com:" -ForegroundColor White
    Write-Host "    - Firewall desabilitado" -ForegroundColor White
    Write-Host "    - Todas security policies desabilitadas" -ForegroundColor White
    Write-Host "    - Nenhuma instancia Chrome anterior" -ForegroundColor White
    Write-Host ""
    Write-Host "  Isso indica bug/limitacao Windows Server 2016 com Chrome" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  RECOMENDACAO: Usar abordagem alternativa (sem Remote Debugging)" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Pressione qualquer tecla para fechar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Perguntar se quer reabilitar Firewall
Write-Host ""
$renable = Read-Host "Deseja REABILITAR Firewall agora? (digite SIM)"
if ($renable -eq "SIM") {
    Write-Host "Reabilitando Firewall..." -ForegroundColor Yellow
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
    Write-Host "Firewall reabilitado!" -ForegroundColor Green
}
