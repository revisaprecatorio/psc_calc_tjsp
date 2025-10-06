# Script para capturar linha de comando do PROCESSO PRINCIPAL do Chrome
# Versao 2: Pega apenas o processo pai (nao os subprocessos)

$outputFile = "C:\projetos\crawler_tjsp\chrome_command_line.txt"

Write-Host "Capturando linha de comando do Chrome (PROCESSO PRINCIPAL)..." -ForegroundColor Cyan
Write-Host ""

# Pegar todos os processos Chrome
$chromeProcesses = Get-Process chrome -ErrorAction SilentlyContinue

if ($chromeProcesses) {
    Write-Host "Encontrados $($chromeProcesses.Count) processos Chrome" -ForegroundColor Green
    Write-Host ""

    # Criar arquivo de output
    "CHROME COMMAND LINE CAPTURE - V2" | Out-File -FilePath $outputFile -Encoding UTF8
    "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8

    # Pegar TODOS os processos Chrome com linha de comando
    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "ANALISANDO TODOS OS PROCESSOS:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8

    $mainProcess = $null

    foreach ($proc in $chromeProcesses) {
        try {
            $wmiProc = Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)"
            $cmdLine = $wmiProc.CommandLine

            if ($cmdLine) {
                # Verificar se NAO e um subprocesso (nao tem --type=)
                if ($cmdLine -notmatch '--type=') {
                    Write-Host "PROCESSO PRINCIPAL ENCONTRADO!" -ForegroundColor Green
                    Write-Host "  PID: $($proc.Id)" -ForegroundColor Yellow
                    Write-Host "  Command: $($cmdLine.Substring(0, [Math]::Min(100, $cmdLine.Length)))..." -ForegroundColor White
                    Write-Host ""

                    $mainProcess = $proc
                    $mainCommandLine = $cmdLine

                    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    ">>> PROCESSO PRINCIPAL (SEM --type=):" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "PID: $($proc.Id)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "StartTime: $($proc.StartTime)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "Path: $($proc.Path)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "COMMAND LINE COMPLETA:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    $cmdLine | Out-File -FilePath $outputFile -Append -Encoding UTF8
                    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8

                } else {
                    # Subprocesso
                    "PID: $($proc.Id) | Type: $(if ($cmdLine -match '--type=(\S+)') { $matches[1] } else { 'unknown' })" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                }
            }

        } catch {
            "PID: $($proc.Id) | ERRO: $($_.Exception.Message)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        }
    }

    if ($mainProcess) {
        "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        "ARGUMENTOS SEPARADOS (PROCESSO PRINCIPAL):" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8

        # Separar argumentos
        # Chrome pode ter aspas, vamos processar corretamente
        $arguments = $mainCommandLine -split ' --'

        foreach ($arg in $arguments) {
            $argTrimmed = $arg.Trim()
            if ($argTrimmed -and $argTrimmed -ne '') {
                if ($argTrimmed.StartsWith('"')) {
                    # Executavel principal
                    "EXECUTAVEL: $argTrimmed" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                } else {
                    "  --$argTrimmed" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                }
            }
        }

        Write-Host "Arquivo salvo em: $outputFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "PROCESSO PRINCIPAL CAPTURADO COM SUCESSO!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Abra o arquivo:" -ForegroundColor Cyan
        Write-Host "  notepad $outputFile" -ForegroundColor White

    } else {
        Write-Host "NENHUM PROCESSO PRINCIPAL ENCONTRADO!" -ForegroundColor Red
        Write-Host "Todos os processos sao subprocessos (com --type=)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "ISSO SIGNIFICA:" -ForegroundColor Yellow
        Write-Host "  - Chrome foi aberto via Remote Debugging ou modo especial" -ForegroundColor White
        Write-Host "  - Nao e possivel capturar linha de comando original do icone" -ForegroundColor White
        Write-Host ""
        Write-Host "SOLUCAO:" -ForegroundColor Cyan
        Write-Host "  1. Feche Chrome completamente" -ForegroundColor White
        Write-Host "  2. Abra Chrome clicando no ICONE normal (nao via PowerShell)" -ForegroundColor White
        Write-Host "  3. Execute este script novamente" -ForegroundColor White

        "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        "ERRO: Nenhum processo principal encontrado (todos tem --type=)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    }

} else {
    Write-Host "Chrome nao esta em execucao!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "  1. Abra Chrome clicando no icone (perfil revisa.precatorio@gmail.com)" -ForegroundColor White
    Write-Host "  2. Execute este script novamente" -ForegroundColor White
    Write-Host ""

    "ERRO: Chrome nao esta em execucao" | Out-File -FilePath $outputFile -Encoding UTF8
}
