# ==========================================
# Setup Simplificado - Windows Server
# Crawler TJSP - Migração para Windows
# ==========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Crawler TJSP - Setup Automatico" -ForegroundColor Cyan
Write-Host "  Windows Server 2016 - Contabo VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se esta rodando como Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERRO: Este script precisa ser executado como Administrator!" -ForegroundColor Red
    Write-Host "Clique direito no PowerShell e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

# Habilitar TLS 1.2 para downloads
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# ==========================================
# FASE 1: Estrutura de Diretorios
# ==========================================
Write-Host "Criando estrutura de diretorios..." -ForegroundColor Yellow
$directories = @("C:\projetos", "C:\certs", "C:\temp", "C:\backups", "C:\logs", "C:\chromedriver")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Criado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Ja existe: $dir" -ForegroundColor Gray
    }
}

# ==========================================
# FASE 2: Python 3.12
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALANDO PYTHON 3.12.3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$pythonInstaller = "C:\temp\python-installer.exe"

Write-Host "Baixando Python 3.12.3..." -ForegroundColor Yellow
try {
    if (-not (Test-Path $pythonInstaller)) {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -ErrorAction Stop
        Write-Host "  Download concluido!" -ForegroundColor Green
    } else {
        Write-Host "  Instalador ja existe" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERRO ao baixar Python: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Instalando Python (pode demorar 2-3 minutos)..." -ForegroundColor Yellow
Start-Process -FilePath $pythonInstaller -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tcltk=0" -Wait -NoNewWindow
Write-Host "  Python instalado!" -ForegroundColor Green

# Atualizar PATH na sessao atual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Aguardar Python inicializar
Start-Sleep -Seconds 3

# Verificar instalacao
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  Versao instalada: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "  AVISO: Python pode nao estar no PATH. Reinicie o PowerShell apos o script." -ForegroundColor Yellow
}

# Atualizar pip
Write-Host "Atualizando pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet 2>&1 | Out-Null

# Instalar ferramentas basicas
Write-Host "Instalando virtualenv, wheel, setuptools..." -ForegroundColor Yellow
& pip install virtualenv wheel setuptools --quiet 2>&1 | Out-Null
Write-Host "  Ferramentas instaladas!" -ForegroundColor Green

# ==========================================
# FASE 3: Google Chrome
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALANDO GOOGLE CHROME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$chromeInstaller = "C:\temp\chrome-installer.msi"

Write-Host "Baixando Google Chrome..." -ForegroundColor Yellow
try {
    if (-not (Test-Path $chromeInstaller)) {
        Invoke-WebRequest -Uri $chromeUrl -OutFile $chromeInstaller -ErrorAction Stop
        Write-Host "  Download concluido!" -ForegroundColor Green
    } else {
        Write-Host "  Instalador ja existe" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ERRO ao baixar Chrome: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Instalando Chrome (pode demorar 1-2 minutos)..." -ForegroundColor Yellow
Start-Process -FilePath "msiexec.exe" -Args "/i $chromeInstaller /quiet /norestart" -Wait -NoNewWindow
Write-Host "  Chrome instalado!" -ForegroundColor Green

# Verificar versao do Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
    Write-Host "  Versao do Chrome: $chromeVersion" -ForegroundColor Cyan

    # Extrair major version para ChromeDriver
    $chromeMajorVersion = $chromeVersion.Split('.')[0]
    Write-Host "  Chrome Major Version: $chromeMajorVersion" -ForegroundColor Cyan
} else {
    Write-Host "  AVISO: Chrome nao encontrado em $chromePath" -ForegroundColor Yellow
}

# ==========================================
# FASE 4: ChromeDriver
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CHROMEDRIVER (Instalacao Manual)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "IMPORTANTE: ChromeDriver precisa ser instalado manualmente!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Passos para instalar ChromeDriver:" -ForegroundColor Cyan
Write-Host "  1. Acesse: https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor White
Write-Host "  2. Procure pela versao: $chromeVersion (ou mais proxima)" -ForegroundColor White
Write-Host "  3. Baixe: chromedriver-win64.zip" -ForegroundColor White
Write-Host "  4. Extraia chromedriver.exe para: C:\chromedriver\" -ForegroundColor White
Write-Host ""

# Tentar baixar ChromeDriver (pode falhar se versao exata nao existir)
$chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/$chromeVersion/win64/chromedriver-win64.zip"
$chromedriverZip = "C:\temp\chromedriver.zip"

Write-Host "Tentando baixar ChromeDriver automaticamente..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $chromedriverUrl -OutFile $chromedriverZip -ErrorAction Stop
    Write-Host "  Download bem-sucedido!" -ForegroundColor Green

    # Extrair
    Expand-Archive -Path $chromedriverZip -DestinationPath "C:\temp\chromedriver-temp" -Force

    # Mover executavel
    $chromedriverExe = Get-ChildItem -Path "C:\temp\chromedriver-temp" -Filter "chromedriver.exe" -Recurse | Select-Object -First 1
    if ($chromedriverExe) {
        Copy-Item -Path $chromedriverExe.FullName -Destination "C:\chromedriver\chromedriver.exe" -Force
        Write-Host "  ChromeDriver instalado em C:\chromedriver\chromedriver.exe" -ForegroundColor Green
    }
} catch {
    Write-Host "  Download automatico falhou (normal se versao exata nao existir)" -ForegroundColor Yellow
    Write-Host "  Faca download manual conforme instrucoes acima" -ForegroundColor Yellow
}

# Adicionar ao PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*C:\chromedriver*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\chromedriver", [EnvironmentVariableTarget]::Machine)
    $env:Path += ";C:\chromedriver"
    Write-Host "  ChromeDriver adicionado ao PATH" -ForegroundColor Green
}

# ==========================================
# FASE 5: Virtual Environment
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURANDO VIRTUAL ENVIRONMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$projectPath = "C:\projetos\crawler_tjsp"

if (-not (Test-Path $projectPath)) {
    Write-Host "ERRO: Projeto nao encontrado em $projectPath" -ForegroundColor Red
    Write-Host "Execute 'git clone https://github.com/revisaprecatorio/crawler_tjsp.git' primeiro!" -ForegroundColor Yellow
    exit 1
}

Set-Location $projectPath

Write-Host "Criando virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "$projectPath\venv")) {
    & python -m venv venv
    Write-Host "  Venv criado!" -ForegroundColor Green
} else {
    Write-Host "  Venv ja existe" -ForegroundColor Gray
}

Write-Host "Instalando dependencias do projeto (pode demorar 3-5 minutos)..." -ForegroundColor Yellow
& "$projectPath\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet 2>&1 | Out-Null
& "$projectPath\venv\Scripts\pip.exe" install -r requirements.txt --quiet 2>&1 | Out-Null
Write-Host "  Dependencias instaladas!" -ForegroundColor Green

# ==========================================
# RESUMO FINAL
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SETUP CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Componentes instalados:" -ForegroundColor Cyan
Write-Host "  - Python 3.12.3" -ForegroundColor White
Write-Host "  - Google Chrome $chromeVersion" -ForegroundColor White
Write-Host "  - Virtual environment + dependencias" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos (fazer manualmente):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. INSTALAR WEB SIGNER" -ForegroundColor Yellow
Write-Host "   - Acesse: https://websigner.softplan.com.br/downloads" -ForegroundColor White
Write-Host "   - Baixe versao Windows (websigner-X.X.X-win64.exe)" -ForegroundColor White
Write-Host "   - Execute instalador" -ForegroundColor White
Write-Host "   - Inicie Web Signer (icone na bandeja do sistema)" -ForegroundColor White
Write-Host ""
Write-Host "2. VERIFICAR CHROMEDRIVER (se download automatico falhou)" -ForegroundColor Yellow
Write-Host "   - Acesse: https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor White
Write-Host "   - Baixe versao compativel com Chrome $chromeVersion" -ForegroundColor White
Write-Host "   - Extraia para C:\chromedriver\chromedriver.exe" -ForegroundColor White
Write-Host ""
Write-Host "3. TRANSFERIR CERTIFICADO" -ForegroundColor Yellow
Write-Host "   - Transferir 25424636_pf.pfx para C:\certs\certificado.pfx" -ForegroundColor White
Write-Host "   - Via RDP: arrastar e soltar do Mac para servidor" -ForegroundColor White
Write-Host ""
Write-Host "4. IMPORTAR CERTIFICADO" -ForegroundColor Yellow
Write-Host "   Execute no PowerShell:" -ForegroundColor White
Write-Host "   `$cert = ConvertTo-SecureString '903205' -AsPlainText -Force" -ForegroundColor Gray
Write-Host "   Import-PfxCertificate -FilePath C:\certs\certificado.pfx -CertStoreLocation Cert:\CurrentUser\My -Password `$cert" -ForegroundColor Gray
Write-Host ""
Write-Host "5. CONFIGURAR .ENV" -ForegroundColor Yellow
Write-Host "   cd C:\projetos\crawler_tjsp" -ForegroundColor Gray
Write-Host "   Copy-Item .env.example .env" -ForegroundColor Gray
Write-Host "   notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "6. TESTAR AUTENTICACAO" -ForegroundColor Yellow
Write-Host "   cd C:\projetos\crawler_tjsp" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python windows-server\scripts\test_authentication.py" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Documentacao completa em:" -ForegroundColor Cyan
Write-Host "  C:\projetos\crawler_tjsp\windows-server\EXECUTE_NOW.md" -ForegroundColor White
Write-Host ""
