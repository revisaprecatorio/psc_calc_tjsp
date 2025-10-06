# Script para capturar linha de comando exata do Chrome em execucao
# Execute com Chrome aberto pelo icone (perfil revisa.precatorio@gmail.com)

$outputFile = "C:\projetos\crawler_tjsp\chrome_command_line.txt"

Write-Host "Capturando linha de comando do Chrome..." -ForegroundColor Cyan
Write-Host ""

# Pegar todos os processos Chrome
$chromeProcesses = Get-Process chrome -ErrorAction SilentlyContinue

if ($chromeProcesses) {
    Write-Host "Encontrados $($chromeProcesses.Count) processos Chrome" -ForegroundColor Green
    Write-Host ""

    # Criar arquivo de output
    "CHROME COMMAND LINE CAPTURE" | Out-File -FilePath $outputFile -Encoding UTF8
    "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8

    # Pegar processo principal (primeiro)
    $mainProcess = $chromeProcesses | Select-Object -First 1

    Write-Host "Processo Principal:" -ForegroundColor Yellow
    Write-Host "  PID: $($mainProcess.Id)" -ForegroundColor White
    Write-Host "  Path: $($mainProcess.Path)" -ForegroundColor White
    Write-Host ""

    "PROCESSO PRINCIPAL:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "PID: $($mainProcess.Id)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "Path: $($mainProcess.Path)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8

    # Capturar linha de comando completa
    try {
        $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($mainProcess.Id)").CommandLine

        if ($commandLine) {
            Write-Host "Linha de comando capturada com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "COMMAND LINE (primeiros 200 caracteres):" -ForegroundColor Cyan

            $previewLength = [Math]::Min(200, $commandLine.Length)
            Write-Host $commandLine.Substring(0, $previewLength) -ForegroundColor White
            Write-Host "..." -ForegroundColor Gray
            Write-Host ""

            "COMMAND LINE COMPLETA:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
            "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8
            $commandLine | Out-File -FilePath $outputFile -Append -Encoding UTF8
            "" | Out-File -FilePath $outputFile -Append -Encoding UTF8

            # Separar argumentos
            "ARGUMENTOS SEPARADOS:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
            "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8

            # Parse manual dos argumentos (Chrome usa --flag=value)
            $arguments = $commandLine -split ' --'

            foreach ($arg in $arguments) {
                if ($arg.Trim()) {
                    "  --$arg" | Out-File -FilePath $outputFile -Append -Encoding UTF8
                }
            }

        } else {
            Write-Host "Linha de comando vazia" -ForegroundColor Red
            "ERRO: Linha de comando vazia" | Out-File -FilePath $outputFile -Append -Encoding UTF8
        }

    } catch {
        Write-Host "Erro ao capturar: $($_.Exception.Message)" -ForegroundColor Red
        "ERRO: $($_.Exception.Message)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    }

    # Listar TODOS os processos Chrome (para debug)
    "" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "TODOS OS PROCESSOS CHROME:" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    "======================================" | Out-File -FilePath $outputFile -Append -Encoding UTF8

    foreach ($proc in $chromeProcesses) {
        "PID: $($proc.Id) | StartTime: $($proc.StartTime)" | Out-File -FilePath $outputFile -Append -Encoding UTF8
    }

    Write-Host "Arquivo salvo em: $outputFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Captura concluida!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Abra o arquivo para ver comando completo:" -ForegroundColor Cyan
    Write-Host "  notepad $outputFile" -ForegroundColor White

} else {
    Write-Host "Chrome nao esta em execucao!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "  1. Abra Chrome clicando no icone (perfil revisa.precatorio@gmail.com)" -ForegroundColor White
    Write-Host "  2. Execute este script novamente" -ForegroundColor White
    Write-Host ""

    "ERRO: Chrome nao esta em execucao" | Out-File -FilePath $outputFile -Encoding UTF8
}
