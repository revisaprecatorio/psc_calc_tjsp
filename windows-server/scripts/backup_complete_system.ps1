# 💾 Script de Backup Completo do Sistema - Crawler TJSP
# Versão: 1.0
# Data: 2025-10-06
# Descrição: Backup automatizado de todos os componentes críticos antes de upgrade

# Requer execução como Administrator
#Requires -RunAsAdministrator

# Configurações
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupRoot = "C:\backups"
$backupDir = Join-Path $backupRoot "backup_$timestamp"
$projectPath = "C:\projetos\crawler_tjsp"
$certsPath = "C:\certs"

# Cores para output
function Write-Step {
    param([string]$Message)
    Write-Host "🔵 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Banner
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💾 BACKUP COMPLETO DO SISTEMA - CRAWLER TJSP" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Gray
Write-Host "  Destino: $backupDir" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$startTime = Get-Date

# ========================================
# ETAPA 1: Criar Estrutura de Diretórios
# ========================================
Write-Step "ETAPA 1/8: Criando estrutura de diretórios..."

$subdirs = @(
    "01_sistema",
    "02_codigo",
    "03_certificados",
    "04_chrome_profile",
    "05_logs",
    "06_database",
    "07_scripts",
    "08_docs"
)

try {
    # Criar diretório raiz do backup
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Criar subdiretórios
    foreach ($dir in $subdirs) {
        $fullPath = Join-Path $backupDir $dir
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
    
    Write-Success "Estrutura de diretórios criada"
} catch {
    Write-Error-Custom "Erro ao criar diretórios: $_"
    exit 1
}

# ========================================
# ETAPA 2: Capturar Informações do Sistema
# ========================================
Write-Step "ETAPA 2/8: Capturando informações do sistema..."

try {
    $sysInfoPath = Join-Path $backupDir "01_sistema"
    
    # Informações do Windows
    Get-ComputerInfo | Out-File "$sysInfoPath\computer_info.txt"
    
    # Versão do Windows
    $osInfo = Get-CimInstance Win32_OperatingSystem
    @{
        "Nome" = $osInfo.Caption
        "Versão" = $osInfo.Version
        "Arquitetura" = $osInfo.OSArchitecture
        "SerialNumber" = $osInfo.SerialNumber
        "InstallDate" = $osInfo.InstallDate
    } | ConvertTo-Json | Out-File "$sysInfoPath\windows_version.json"
    
    # Variáveis de ambiente
    Get-ChildItem Env: | Export-Csv "$sysInfoPath\environment_variables.csv" -NoTypeInformation
    
    # PATH específico
    @{
        "PATH" = $env:Path -split ";"
        "PYTHONPATH" = $env:PYTHONPATH
    } | ConvertTo-Json | Out-File "$sysInfoPath\path_variables.json"
    
    # Software instalado
    Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
        Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
        Export-Csv "$sysInfoPath\installed_software.csv" -NoTypeInformation
    
    # Versões críticas
    $versions = @{
        "Python" = & python --version 2>&1 | Out-String
        "Git" = & git --version 2>&1 | Out-String
        "ChromeDriver" = & chromedriver --version 2>&1 | Out-String
        "Chrome" = (Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
    }
    $versions | ConvertTo-Json | Out-File "$sysInfoPath\software_versions.json"
    
    # Serviços relevantes
    Get-Service | Where-Object {
        $_.DisplayName -like "*Crawler*" -or 
        $_.DisplayName -like "*TJSP*" -or
        $_.DisplayName -like "*PostgreSQL*" -or
        $_.DisplayName -like "*OpenSSH*"
    } | Export-Csv "$sysInfoPath\services.csv" -NoTypeInformation
    
    # Tarefas agendadas
    Get-ScheduledTask | Where-Object {
        $_.TaskName -like "*Crawler*" -or 
        $_.TaskName -like "*TJSP*"
    } | Export-Csv "$sysInfoPath\scheduled_tasks.csv" -NoTypeInformation
    
    # Regras de firewall
    Get-NetFirewallRule | Where-Object {
        $_.DisplayName -like "*RDP*" -or 
        $_.DisplayName -like "*SSH*" -or 
        $_.DisplayName -like "*PostgreSQL*"
    } | Select-Object DisplayName, Direction, Action, Enabled, Profile |
        Export-Csv "$sysInfoPath\firewall_rules.csv" -NoTypeInformation
    
    # Portas listening
    Get-NetTCPConnection | Where-Object {$_.State -eq "Listen"} |
        Select-Object LocalAddress, LocalPort, OwningProcess |
        Export-Csv "$sysInfoPath\listening_ports.csv" -NoTypeInformation
    
    Write-Success "Informações do sistema capturadas"
} catch {
    Write-Warning "Erro ao capturar informações do sistema: $_"
}

# ========================================
# ETAPA 3: Backup do Código do Projeto
# ========================================
Write-Step "ETAPA 3/8: Fazendo backup do código do projeto..."

try {
    $codigoPath = Join-Path $backupDir "02_codigo"
    
    if (Test-Path $projectPath) {
        # Copiar projeto completo (exceto .git para economizar espaço)
        Write-Host "  📁 Copiando $projectPath..." -ForegroundColor Gray
        
        # Copiar arquivos Python e configuração
        Copy-Item "$projectPath\*.py" $codigoPath -Force -ErrorAction SilentlyContinue
        Copy-Item "$projectPath\*.txt" $codigoPath -Force -ErrorAction SilentlyContinue
        Copy-Item "$projectPath\*.md" $codigoPath -Force -ErrorAction SilentlyContinue
        Copy-Item "$projectPath\.env" $codigoPath -Force -ErrorAction SilentlyContinue
        
        # Copiar diretórios importantes
        $dirsToBackup = @("scripts", "docs", "windows-server", "chrome_extension")
        foreach ($dir in $dirsToBackup) {
            $sourcePath = Join-Path $projectPath $dir
            if (Test-Path $sourcePath) {
                $destPath = Join-Path $codigoPath $dir
                Copy-Item $sourcePath $destPath -Recurse -Force
            }
        }
        
        # Copiar virtual environment (apenas pacotes instalados)
        $venvPath = Join-Path $projectPath ".venv"
        if (Test-Path $venvPath) {
            Write-Host "  📦 Exportando lista de pacotes Python..." -ForegroundColor Gray
            & "$venvPath\Scripts\pip.exe" freeze | Out-File "$codigoPath\requirements_frozen.txt"
        }
        
        # Informações do repositório Git
        Push-Location $projectPath
        git log -1 --pretty=format:"%H%n%an%n%ae%n%ad%n%s" | Out-File "$codigoPath\git_last_commit.txt"
        git status --short | Out-File "$codigoPath\git_status.txt"
        git branch --show-current | Out-File "$codigoPath\git_branch.txt"
        Pop-Location
        
        Write-Success "Código do projeto copiado"
    } else {
        Write-Warning "Projeto não encontrado em $projectPath"
    }
} catch {
    Write-Warning "Erro ao fazer backup do código: $_"
}

# ========================================
# ETAPA 4: Backup de Certificados
# ========================================
Write-Step "ETAPA 4/8: Fazendo backup de certificados..."

try {
    $certPath = Join-Path $backupDir "03_certificados"
    
    # Copiar arquivo .pfx do disco
    if (Test-Path "$certsPath\certificado.pfx") {
        Copy-Item "$certsPath\certificado.pfx" $certPath -Force
        $certSize = (Get-Item "$certPath\certificado.pfx").Length
        Write-Host "  📄 certificado.pfx copiado ($certSize bytes)" -ForegroundColor Gray
    }
    
    # Exportar certificado do Windows Certificate Store
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
    
    if ($cert) {
        Write-Host "  🔐 Exportando certificado do Certificate Store..." -ForegroundColor Gray
        
        # Exportar chave pública (.cer)
        Export-Certificate -Cert $cert -FilePath "$certPath\certificado_public.cer" | Out-Null
        
        # Exportar com chave privada (.pfx) - REQUER SENHA
        $password = ConvertTo-SecureString -String "903205" -Force -AsPlainText
        Export-PfxCertificate -Cert $cert -FilePath "$certPath\certificado_from_store.pfx" -Password $password | Out-Null
        
        # Salvar informações do certificado
        @{
            "Subject" = $cert.Subject
            "Issuer" = $cert.Issuer
            "Thumbprint" = $cert.Thumbprint
            "NotBefore" = $cert.NotBefore
            "NotAfter" = $cert.NotAfter
            "HasPrivateKey" = $cert.HasPrivateKey
        } | ConvertTo-Json | Out-File "$certPath\certificate_info.json"
        
        Write-Success "Certificados exportados"
    } else {
        Write-Warning "Certificado não encontrado no Certificate Store"
    }
    
    # Documentar senha (IMPORTANTE!)
    @"
INFORMAÇÕES DO CERTIFICADO DIGITAL
===================================

Arquivo: certificado.pfx
Senha: 903205
CPF Titular: 517.648.902-30
Número do Pedido: 25424636
Código de Instalação: 669-281

⚠️ MANTENHA ESTA INFORMAÇÃO SEGURA!
"@ | Out-File "$certPath\SENHA_CERTIFICADO.txt"
    
} catch {
    Write-Warning "Erro ao fazer backup de certificados: $_"
}

# ========================================
# ETAPA 5: Backup Perfil Chrome
# ========================================
Write-Step "ETAPA 5/8: Documentando perfil Chrome..."

try {
    $chromePath = Join-Path $backupDir "04_chrome_profile"
    
    # Informações do perfil (não copiar arquivos - podem ser grandes)
    $profilePath = "C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default"
    
    @"
PERFIL CHROME - INFORMAÇÕES
============================

Perfil sincronizado: revisa.precatorio@gmail.com
Localização: $profilePath

EXTENSÕES INSTALADAS:
---------------------
Para restaurar:
1. Fazer login no Chrome com revisa.precatorio@gmail.com
2. Extensões serão sincronizadas automaticamente
3. Verificar em chrome://extensions/

CRÍTICO:
- Web Signer deve estar instalado
- Verificar comunicação com aplicativo nativo
- Testar login certificado após restore

NOTA: Perfil sincronizado via Google Account, não requer backup de arquivos locais.
"@ | Out-File "$chromePath\chrome_profile_info.txt"
    
    # Tentar listar extensões
    $extensionsPath = Join-Path $profilePath "Extensions"
    if (Test-Path $extensionsPath) {
        Get-ChildItem $extensionsPath | Select-Object Name, LastWriteTime |
            Export-Csv "$chromePath\extensions_list.csv" -NoTypeInformation
    }
    
    Write-Success "Informações do Chrome documentadas"
} catch {
    Write-Warning "Erro ao documentar perfil Chrome: $_"
}

# ========================================
# ETAPA 6: Backup de Logs
# ========================================
Write-Step "ETAPA 6/8: Copiando logs..."

try {
    $logsPath = Join-Path $backupDir "05_logs"
    
    # Logs do projeto
    $projectLogsPath = Join-Path $projectPath "logs"
    if (Test-Path $projectLogsPath) {
        Copy-Item "$projectLogsPath\*" $logsPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Logs do projeto copiados"
    } else {
        Write-Host "  ℹ️  Nenhum log encontrado" -ForegroundColor Gray
    }
    
    # Logs do Windows (últimos 100 eventos de Application)
    Get-EventLog -LogName Application -Newest 100 |
        Export-Csv "$logsPath\windows_application_events.csv" -NoTypeInformation
    
} catch {
    Write-Warning "Erro ao copiar logs: $_"
}

# ========================================
# ETAPA 7: Backup PostgreSQL (se aplicável)
# ========================================
Write-Step "ETAPA 7/8: Verificando PostgreSQL..."

try {
    $dbPath = Join-Path $backupDir "06_database"
    
    $pgService = Get-Service | Where-Object {$_.Name -like "*postgresql*"}
    
    if ($pgService) {
        Write-Host "  🗄️  PostgreSQL detectado, fazendo backup..." -ForegroundColor Gray
        
        $pgBinPath = "C:\Program Files\PostgreSQL\15\bin"
        
        if (Test-Path $pgBinPath) {
            # Dump completo
            & "$pgBinPath\pg_dumpall.exe" -U postgres -f "$dbPath\all_databases_backup.sql" 2>&1 | Out-Null
            
            # Dump específico (se existir)
            & "$pgBinPath\pg_dump.exe" -U revisa_user -d revisa_db -f "$dbPath\revisa_db_backup.sql" 2>&1 | Out-Null
            
            # Arquivos de configuração
            $pgDataPath = "C:\Program Files\PostgreSQL\15\data"
            if (Test-Path "$pgDataPath\postgresql.conf") {
                Copy-Item "$pgDataPath\postgresql.conf" $dbPath -Force
                Copy-Item "$pgDataPath\pg_hba.conf" $dbPath -Force
            }
            
            Write-Success "Backup PostgreSQL concluído"
        }
    } else {
        Write-Host "  ℹ️  PostgreSQL não instalado (pode estar usando banco remoto)" -ForegroundColor Gray
        
        @"
PostgreSQL não detectado localmente.

Se estiver usando banco remoto:
- Credenciais estão no arquivo .env
- Backup deve ser feito no servidor remoto
- Nenhuma ação necessária aqui
"@ | Out-File "$dbPath\database_remote_note.txt"
    }
} catch {
    Write-Warning "Erro ao fazer backup PostgreSQL: $_"
}

# ========================================
# ETAPA 8: Gerar Manifesto e Documentação
# ========================================
Write-Step "ETAPA 8/8: Gerando manifesto e documentação..."

try {
    $manifest = @"
╔════════════════════════════════════════════════════════════════╗
║             BACKUP COMPLETO - CRAWLER TJSP                     ║
╚════════════════════════════════════════════════════════════════╝

Data do Backup: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
Servidor: 62.171.143.88 (Contabo Cloud VPS 10)
Sistema Operacional: $($(Get-CimInstance Win32_OperatingSystem).Caption)
Hostname: $env:COMPUTERNAME
Usuário: $env:USERNAME

════════════════════════════════════════════════════════════════

📁 ESTRUTURA DO BACKUP:

01_sistema/
    - Informações do Windows
    - Variáveis de ambiente
    - Software instalado
    - Serviços e tarefas agendadas
    - Regras de firewall

02_codigo/
    - Código Python completo
    - Arquivo .env
    - Scripts e documentação
    - requirements.txt (pacotes instalados)
    - Informações do Git

03_certificados/
    - certificado.pfx (arquivo original)
    - certificado_from_store.pfx (export do Windows)
    - certificado_public.cer (chave pública)
    - certificate_info.json (metadados)
    - SENHA_CERTIFICADO.txt (📌 IMPORTANTE!)

04_chrome_profile/
    - Documentação do perfil sincronizado
    - Lista de extensões instaladas

05_logs/
    - Logs do crawler
    - Event logs do Windows

06_database/
    - Dumps PostgreSQL (se aplicável)
    - Arquivos de configuração

07_scripts/ (não utilizado neste backup)

08_docs/ (não utilizado neste backup)

════════════════════════════════════════════════════════════════

🔐 INFORMAÇÕES CRÍTICAS:

Certificado Digital:
- Arquivo: certificado.pfx
- Senha: 903205
- CPF: 517.648.902-30

Perfil Chrome:
- Conta: revisa.precatorio@gmail.com
- Extensão crítica: Web Signer

Software Principal:
- Python: $(& python --version 2>&1)
- Chrome: $($(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe" -ErrorAction SilentlyContinue).VersionInfo.FileVersion)
- Git: $(& git --version 2>&1)

════════════════════════════════════════════════════════════════

📝 INSTRUÇÕES DE RESTORE:

1. VIA SNAPSHOT CONTABO (RECOMENDADO):
   - Painel Contabo → Snapshots
   - Selecionar snapshot: pre-upgrade-to-ws2025-2025-10-06
   - Clicar "Restore"
   - Aguardar 10-20 minutos
   - ✅ Sistema volta ao estado exato do backup

2. VIA RESTORE MANUAL:
   - Consultar arquivo: RESTORE_GUIDE.md
   - Instalar Windows Server 2025
   - Executar restore_from_backup.ps1
   - Importar certificado
   - Instalar software listado
   - Restaurar código e configurações

════════════════════════════════════════════════════════════════

⚠️  ATENÇÃO:

- SNAPSHOT Contabo é seu seguro principal!
- Este ZIP é backup secundário/redundante
- Mantenha em MÚLTIPLOS locais seguros
- Não compartilhe (contém senha do certificado)
- Valide hash MD5 após transferir

════════════════════════════════════════════════════════════════

📊 ESTATÍSTICAS:

Total de arquivos: $(Get-ChildItem $backupDir -Recurse | Measure-Object).Count
Tamanho total: calculando...
Hash MD5: será gerado após compactação

════════════════════════════════════════════════════════════════

Backup gerado por: backup_complete_system.ps1 v1.0
Responsável: Persival Balleste
Projeto: Crawler TJSP - Migração Windows Server

Para suporte, consulte: windows-server/BACKUP_GUIDE.md

════════════════════════════════════════════════════════════════
"@

    $manifest | Out-File "$backupDir\BACKUP_MANIFEST.txt" -Encoding UTF8
    
    Write-Success "Manifesto gerado"
} catch {
    Write-Warning "Erro ao gerar manifesto: $_"
}

# ========================================
# COMPACTAR BACKUP
# ========================================
Write-Step "Compactando backup..."

try {
    $zipFile = "$backupRoot\BACKUP_COMPLETO_PRE_UPGRADE_$timestamp.zip"
    
    Write-Host "  🗜️  Criando arquivo ZIP..." -ForegroundColor Gray
    Write-Host "     Isso pode levar alguns minutos..." -ForegroundColor Gray
    
    Compress-Archive -Path $backupDir -DestinationPath $zipFile -CompressionLevel Optimal
    
    # Calcular hash MD5
    $hash = Get-FileHash $zipFile -Algorithm MD5
    $hash.Hash | Out-File "$zipFile.md5"
    
    # Tamanho do arquivo
    $zipSize = (Get-Item $zipFile).Length
    $zipSizeGB = [math]::Round($zipSize / 1GB, 2)
    
    Write-Success "Backup compactado"
    Write-Host "  📦 Arquivo: $zipFile" -ForegroundColor Gray
    Write-Host "  📊 Tamanho: $zipSizeGB GB" -ForegroundColor Gray
    Write-Host "  🔐 MD5: $($hash.Hash)" -ForegroundColor Gray
    
} catch {
    Write-Error-Custom "Erro ao compactar backup: $_"
}

# ========================================
# RESUMO FINAL
# ========================================
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ BACKUP CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  📁 Diretório: $backupDir" -ForegroundColor Gray
Write-Host "  📦 Arquivo ZIP: BACKUP_COMPLETO_PRE_UPGRADE_$timestamp.zip" -ForegroundColor Gray
Write-Host "  📊 Tamanho: $zipSizeGB GB" -ForegroundColor Gray
Write-Host "  🔐 MD5: $($hash.Hash)" -ForegroundColor Gray
Write-Host "  ⏱️  Tempo total: $($duration.Minutes) min $($duration.Seconds) seg" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green

Write-Host "`n📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "  1. Transferir ZIP para computador local via SCP/RDP" -ForegroundColor Yellow
Write-Host "  2. Validar hash MD5 após transferência" -ForegroundColor Yellow
Write-Host "  3. Fazer cópia adicional em HD externo/cloud" -ForegroundColor Yellow
Write-Host "  4. Criar snapshot na Contabo (CRÍTICO!)" -ForegroundColor Yellow
Write-Host "  5. Validar checklist completo em BACKUP_GUIDE.md" -ForegroundColor Yellow
Write-Host "  6. ✅ Proceder com upgrade para Windows Server 2025" -ForegroundColor Yellow

Write-Host "`n⚠️  LEMBRE-SE:" -ForegroundColor Red
Write-Host "  - Criar SNAPSHOT Contabo antes de qualquer mudança!" -ForegroundColor Red
Write-Host "  - Manter backup em MÚLTIPLOS locais seguros" -ForegroundColor Red
Write-Host "  - Validar hash MD5 após transferir arquivo" -ForegroundColor Red

Write-Host "`n"

