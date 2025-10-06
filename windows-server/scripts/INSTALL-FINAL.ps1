# =====================================================================
# AUTO INSTALACAO COMPLETA - CRAWLER TJSP
# Windows Server 2022 - VERSAO FINAL LIMPA
# =====================================================================
# Versao: 1.1 FINAL LIMPA
# Data: 2025-10-06
# Tempo estimado: 2-3 horas
# =====================================================================

param(
    [switch]$SkipPython = $false,
    [switch]$SkipGit = $false,
    [switch]$SkipChrome = $false
)

# =====================================================================
# CONFIGURACOES GLOBAIS
# =====================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$logFile = "C:\temp\install_log_$timestamp.txt"

# =====================================================================
# FUNCOES AUXILIARES
# =====================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Type] $Message"
    
    switch ($Type) {
        "INFO"    { Write-Host $logMessage -ForegroundColor Cyan }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "ERROR"   { Write-Host $logMessage -ForegroundColor Red }
        "WARN"    { Write-Host $logMessage -ForegroundColor Yellow }
        "STEP"    { 
            Write-Host ""
            Write-Host "============================================" -ForegroundColor Cyan
            Write-Host $logMessage -ForegroundColor Cyan
            Write-Host "============================================" -ForegroundColor Cyan
            Write-Host ""
        }
    }
    
    Add-Content -Path $logFile -Value $logMessage -ErrorAction SilentlyContinue
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-InternetConnection {
    try {
        $result = Test-Connection -ComputerName google.com -Count 2 -Quiet
        return $result
    } catch {
        return $false
    }
}

# =====================================================================
# BANNER INICIAL
# =====================================================================

Clear-Host
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  AUTO INSTALACAO COMPLETA - CRAWLER TJSP" -ForegroundColor Cyan
Write-Host "  Windows Server 2022" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Gray
Write-Host "  Tempo estimado: 2-3 horas" -ForegroundColor Gray
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# =====================================================================
# PRE-VALIDACOES
# =====================================================================

Write-Log "Iniciando pre-validacoes..." "STEP"

if (-not (Test-Administrator)) {
    Write-Log "ERRO: Execute este script como Administrator!" "ERROR"
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Log "Executando como Administrator" "SUCCESS"

Write-Log "Testando conexao com a internet..." "INFO"
if (-not (Test-InternetConnection)) {
    Write-Log "ERRO: Sem conexao com a internet!" "ERROR"
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Log "Conexao com internet OK" "SUCCESS"

$osInfo = Get-WmiObject -Class Win32_OperatingSystem
Write-Log "Sistema: $($osInfo.Caption)" "INFO"
Write-Log "Versao: $($osInfo.Version)" "INFO"

# =====================================================================
# ETAPA 1: CONFIGURACAO BASE
# =====================================================================

Write-Log "ETAPA 1/7: Configuracao Base do Sistema" "STEP"

Write-Log "Habilitando TLS 1.2..." "INFO"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Log "Configurando Execution Policy..." "INFO"
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
    Write-Log "Execution Policy configurado" "SUCCESS"
} catch {
    $errorMsg = $_.Exception.Message
    Write-Log "Falha ao configurar Execution Policy: $errorMsg" "WARN"
}

Write-Log "Configurando timezone para Brasilia..." "INFO"
try {
    Set-TimeZone -Id "E. South America Standard Time"
    $tz = Get-TimeZone
    Write-Log "Timezone: $($tz.Id)" "SUCCESS"
} catch {
    $errorMsg = $_.Exception.Message
    Write-Log "Falha ao configurar timezone: $errorMsg" "WARN"
}

Write-Log "Criando estrutura de diretorios..." "INFO"
$directories = @(
    "C:\projetos",
    "C:\certs",
    "C:\temp",
    "C:\temp\installers",
    "C:\backups",
    "C:\logs",
    "C:\chromedriver"
)

foreach ($dir in $directories) {
    try {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Criado: $dir" "SUCCESS"
        } else {
            Write-Log "Ja existe: $dir" "INFO"
        }
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Log "Falha ao criar ${dir}: $errorMsg" "ERROR"
    }
}

# =====================================================================
# ETAPA 2: INSTALAR PYTHON 3.12.3
# =====================================================================

if (-not $SkipPython) {
    Write-Log "ETAPA 2/7: Instalacao do Python 3.12.3" "STEP"
    
    $pythonExe = "C:\Program Files\Python312\python.exe"
    if (Test-Path $pythonExe) {
        Write-Log "Python ja instalado" "INFO"
        $currentVersion = & $pythonExe --version 2>&1
        Write-Log "Versao atual: $currentVersion" "INFO"
    } else {
        Write-Log "Baixando Python 3.12.3..." "INFO"
        Write-Log "Isso pode levar 2-3 minutos..." "WARN"
        
        $pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        $installerPath = "C:\temp\installers\python-3.12.3-amd64.exe"
        
        try {
            Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
            Write-Log "Download concluido" "SUCCESS"
            
            Write-Log "Instalando Python (pode levar 3-5 minutos)..." "INFO"
            $installArgs = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tcltk=0"
            Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait
            
            Write-Log "Python instalado" "SUCCESS"
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
            
        } catch {
            $errorMsg = $_.Exception.Message
            Write-Log "Falha ao instalar Python: $errorMsg" "ERROR"
        }
    }
    
    Start-Sleep -Seconds 3
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    
    try {
        $pythonVersion = & python --version 2>&1
        Write-Log "Python verificado: $pythonVersion" "SUCCESS"
        
        Write-Log "Atualizando pip..." "INFO"
        & python -m pip install --upgrade pip --quiet
        
        Write-Log "Instalando virtualenv, wheel, setuptools..." "INFO"
        & pip install virtualenv wheel setuptools --quiet
        Write-Log "Ferramentas Python instaladas" "SUCCESS"
        
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Log "Falha ao verificar Python: $errorMsg" "ERROR"
    }
} else {
    Write-Log "ETAPA 2/7: Python (PULADO)" "STEP"
}

# =====================================================================
# ETAPA 3: INSTALAR GIT
# =====================================================================

if (-not $SkipGit) {
    Write-Log "ETAPA 3/7: Instalacao do Git" "STEP"
    
    try {
        $gitVersion = & git --version 2>&1
        Write-Log "Git ja instalado: $gitVersion" "INFO"
    } catch {
        Write-Log "Baixando Git..." "INFO"
        Write-Log "Isso pode levar 2-3 minutos..." "WARN"
        
        $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
        $installerPath = "C:\temp\installers\git-installer.exe"
        
        try {
            Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath -UseBasicParsing
            Write-Log "Download concluido" "SUCCESS"
            
            Write-Log "Instalando Git (pode levar 2-3 minutos)..." "INFO"
            Start-Process -FilePath $installerPath -ArgumentList "/VERYSILENT /NORESTART" -Wait
            
            Write-Log "Git instalado" "SUCCESS"
            
            Start-Sleep -Seconds 10
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
            
        } catch {
            $errorMsg = $_.Exception.Message
            Write-Log "Falha ao instalar Git: $errorMsg" "ERROR"
        }
    }
    
    Start-Sleep -Seconds 3
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    
    try {
        $gitVersion = & git --version 2>&1
        Write-Log "Git verificado: $gitVersion" "SUCCESS"
        
        Write-Log "Configurando Git..." "INFO"
        & git config --global user.name "Revisa Precatorio"
        & git config --global user.email "revisa.precatorio@gmail.com"
        & git config --global core.autocrlf true
        Write-Log "Git configurado" "SUCCESS"
        
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Log "Falha ao verificar Git: $errorMsg" "WARN"
    }
} else {
    Write-Log "ETAPA 3/7: Git (PULADO)" "STEP"
}

# =====================================================================
# ETAPA 4: INSTALAR CHROME
# =====================================================================

if (-not $SkipChrome) {
    Write-Log "ETAPA 4/7: Instalacao do Chrome" "STEP"
    
    $chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if (Test-Path $chromePath) {
        $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
        Write-Log "Chrome ja instalado: versao $chromeVersion" "INFO"
    } else {
        Write-Log "Baixando Google Chrome..." "INFO"
        Write-Log "Isso pode levar 2-3 minutos..." "WARN"
        
        $chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
        $installerPath = "C:\temp\installers\chrome-installer.msi"
        
        try {
            Invoke-WebRequest -Uri $chromeUrl -OutFile $installerPath -UseBasicParsing
            Write-Log "Download concluido" "SUCCESS"
            
            Write-Log "Instalando Chrome (pode levar 2-3 minutos)..." "INFO"
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $installerPath /quiet /norestart" -Wait
            
            Write-Log "Chrome instalado" "SUCCESS"
            
        } catch {
            $errorMsg = $_.Exception.Message
            Write-Log "Falha ao instalar Chrome: $errorMsg" "ERROR"
        }
    }
    
    if (Test-Path $chromePath) {
        $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
        Write-Log "Chrome versao: $chromeVersion" "SUCCESS"
        
        Write-Log "Instalando ChromeDriver compativel..." "INFO"
        
        $chromeMajorVersion = $chromeVersion.Split('.')[0]
        Write-Log "Chrome major version: $chromeMajorVersion" "INFO"
        
        $chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/$chromeVersion/win64/chromedriver-win64.zip"
        $zipPath = "C:\temp\installers\chromedriver.zip"
        
        try {
            Write-Log "Baixando ChromeDriver para versao $chromeVersion..." "INFO"
            Invoke-WebRequest -Uri $chromedriverUrl -OutFile $zipPath -UseBasicParsing
            
            Expand-Archive -Path $zipPath -DestinationPath "C:\temp\chromedriver-temp" -Force
            
            $chromedriverExe = Get-ChildItem "C:\temp\chromedriver-temp" -Recurse -Filter "chromedriver.exe" | Select-Object -First 1
            if ($chromedriverExe) {
                Copy-Item $chromedriverExe.FullName -Destination "C:\chromedriver\chromedriver.exe" -Force
                Write-Log "ChromeDriver instalado" "SUCCESS"
                
                $currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
                if ($currentPath -notlike "*C:\chromedriver*") {
                    [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\chromedriver", [EnvironmentVariableTarget]::Machine)
                    $env:Path += ";C:\chromedriver"
                    Write-Log "ChromeDriver adicionado ao PATH" "SUCCESS"
                }
            }
            
        } catch {
            Write-Log "Falha ao baixar ChromeDriver automaticamente" "WARN"
            Write-Log "Download manual necessario de:" "WARN"
            Write-Log "https://googlechromelabs.github.io/chrome-for-testing/" "WARN"
        }
    }
} else {
    Write-Log "ETAPA 4/7: Chrome (PULADO)" "STEP"
}

# =====================================================================
# ETAPA 5: INSTALAR VISUAL C++ BUILD TOOLS
# =====================================================================

Write-Log "ETAPA 5/7: Visual C++ Build Tools" "STEP"
Write-Log "AVISO: Esta instalacao pode demorar 10-15 minutos!" "WARN"

$buildToolsPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"

if (Test-Path $buildToolsPath) {
    Write-Log "Build Tools ja instalado" "INFO"
} else {
    Write-Log "Baixando Visual C++ Build Tools..." "INFO"
    
    $buildToolsUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    $installerPath = "C:\temp\installers\vs_buildtools.exe"
    
    try {
        Invoke-WebRequest -Uri $buildToolsUrl -OutFile $installerPath -UseBasicParsing
        Write-Log "Download concluido" "SUCCESS"
        
        Write-Log "Instalando Build Tools (10-15 minutos)..." "INFO"
        Write-Log "AGUARDE... Nao feche esta janela!" "WARN"
        
        $buildArgs = "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
        Start-Process -FilePath $installerPath -ArgumentList $buildArgs -Wait
        
        Write-Log "Build Tools instalado" "SUCCESS"
        
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Log "Falha ao instalar Build Tools: $errorMsg" "ERROR"
        Write-Log "Continuando instalacao..." "WARN"
    }
}

# =====================================================================
# ETAPA 6: CONFIGURAR PROJETO
# =====================================================================

Write-Log "ETAPA 6/7: Configuracao do Projeto" "STEP"

$projectPath = "C:\projetos\crawler_tjsp"

if (-not (Test-Path $projectPath)) {
    New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
    Write-Log "Pasta do projeto criada" "SUCCESS"
}

cd $projectPath

Write-Log "Criando virtual environment..." "INFO"
if (-not (Test-Path "$projectPath\.venv")) {
    try {
        & python -m venv .venv
        Write-Log "Virtual environment criado" "SUCCESS"
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Log "Falha ao criar venv: $errorMsg" "ERROR"
    }
} else {
    Write-Log "Virtual environment ja existe" "INFO"
}

Write-Log "Criando requirements.txt..." "INFO"
$requirements = @"
fastapi==0.115.2
uvicorn[standard]==0.30.6
selenium==4.25.0
requests
psycopg2-binary
python-dotenv
tabulate
psutil
"@

$requirements | Out-File -FilePath "$projectPath\requirements.txt" -Encoding utf8 -Force
Write-Log "requirements.txt criado" "SUCCESS"

Write-Log "Instalando dependencias Python..." "INFO"
Write-Log "Isso pode levar 5-10 minutos..." "WARN"

try {
    & "$projectPath\.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    & "$projectPath\.venv\Scripts\pip.exe" install -r "$projectPath\requirements.txt" --quiet
    Write-Log "Dependencias instaladas" "SUCCESS"
} catch {
    $errorMsg = $_.Exception.Message
    Write-Log "Falha ao instalar dependencias: $errorMsg" "ERROR"
}

Write-Log "Criando arquivo .env..." "INFO"
$envContent = @"
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=SUA_SENHA_AQUI

# Chrome e ChromeDriver
CHROME_BINARY_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe

# Certificado Digital A1
CERT_PATH=C:\certs\certificado.pfx
CERT_PASSWORD=903205
CERT_CPF=517.648.902-30

# Web Signer
WEBSIGNER_PATH=C:\Program Files\Softplan\WebSigner\websigner.exe

# Logs
LOG_LEVEL=INFO
LOG_PATH=C:\projetos\crawler_tjsp\logs
"@

$envContent | Out-File -FilePath "$projectPath\.env" -Encoding utf8 -Force
Write-Log ".env criado" "SUCCESS"

Write-Log "Criando script quickstart.ps1..." "INFO"
$quickstartContent = @'
# Quick Start - Crawler TJSP
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  CRAWLER TJSP - QUICK START" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1

Write-Host "[OK] Ambiente ativado!" -ForegroundColor Green
Write-Host ""
Write-Host "Python: $(python --version)" -ForegroundColor Gray
Write-Host ""
'@

$quickstartContent | Out-File -FilePath "$projectPath\quickstart.ps1" -Encoding utf8 -Force
Write-Log "quickstart.ps1 criado" "SUCCESS"

# =====================================================================
# ETAPA 7: CRIAR RELATORIO FINAL
# =====================================================================

Write-Log "ETAPA 7/7: Gerando Relatorio Final" "STEP"

$report = @"
=====================================================
  RELATORIO DE INSTALACAO - CRAWLER TJSP
=====================================================

Data: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
Sistema: $($osInfo.Caption)
Versao: $($osInfo.Version)

=====================================================
  SOFTWARE INSTALADO
=====================================================

"@

try {
    $pythonVersion = & python --version 2>&1
    $report += "Python: $pythonVersion`n"
} catch {
    $report += "Python: NAO INSTALADO`n"
}

try {
    $gitVersion = & git --version 2>&1
    $report += "Git: $gitVersion`n"
} catch {
    $report += "Git: NAO INSTALADO`n"
}

if (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") {
    $chromeVersion = (Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
    $report += "Chrome: versao $chromeVersion`n"
} else {
    $report += "Chrome: NAO INSTALADO`n"
}

try {
    $chromedriverVersion = & chromedriver --version 2>&1
    $report += "ChromeDriver: $chromedriverVersion`n"
} catch {
    $report += "ChromeDriver: NAO INSTALADO`n"
}

$report += @"

=====================================================
  PROXIMAS ETAPAS MANUAIS
=====================================================

1. INSTALAR WEB SIGNER:
   - Acessar: https://websigner.softplan.com.br/downloads
   - Baixar versao Windows 64-bit
   - Instalar (seguir wizard)

2. TRANSFERIR CERTIFICADO:
   - Transferir certificado.pfx para C:\certs\
   - Via SCP: scp certificado.pfx Administrator@62.171.143.88:C:/certs/

3. IMPORTAR CERTIFICADO:
   Execute no PowerShell:
   
   `$certPath = "C:\certs\certificado.pfx"
   `$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText
   Import-PfxCertificate -FilePath `$certPath -CertStoreLocation Cert:\CurrentUser\My -Password `$certPassword

4. CONFIGURAR CHROME:
   - Abrir Chrome manualmente
   - Login: revisa.precatorio@gmail.com
   - Aguardar sincronizacao

5. TESTAR AUTENTICACAO:
   - Abrir: https://esaj.tjsp.jus.br/esaj/portal.do
   - Clicar em "Certificado Digital"

=====================================================
  LOGS
=====================================================

Log completo: $logFile

=====================================================
"@

$reportPath = "C:\projetos\crawler_tjsp\INSTALACAO_RELATORIO.txt"
$report | Out-File -FilePath $reportPath -Encoding utf8 -Force

# =====================================================================
# FINALIZAR
# =====================================================================

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  INSTALACAO AUTOMATIZADA CONCLUIDA!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Log "Instalacao automatizada concluida com sucesso!" "SUCCESS"
Write-Log "Relatorio salvo em: $reportPath" "INFO"
Write-Log "Log completo em: $logFile" "INFO"
Write-Host ""
Write-Host "PROXIMAS ETAPAS MANUAIS:" -ForegroundColor Yellow
Write-Host "  1. Instalar Web Signer" -ForegroundColor White
Write-Host "  2. Transferir certificado.pfx" -ForegroundColor White
Write-Host "  3. Importar certificado" -ForegroundColor White
Write-Host "  4. Configurar Chrome (login + extensao)" -ForegroundColor White
Write-Host "  5. Testar autenticacao" -ForegroundColor White
Write-Host ""
Write-Host "Consultar: $reportPath" -ForegroundColor Cyan
Write-Host ""

Read-Host "Pressione Enter para finalizar"
