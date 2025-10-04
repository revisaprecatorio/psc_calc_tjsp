# ==========================================
# Script de Setup Completo - Windows Server
# Crawler TJSP - Migração para Windows
# ==========================================
#
# Este script automatiza a instalação de todas as dependências
# necessárias para rodar o Crawler TJSP no Windows Server.
#
# IMPORTANTE: Executar como Administrator
# Tempo estimado: 60-90 minutos
#
# Uso:
#   .\setup-complete.ps1
#

# Verificar se está rodando como Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Este script precisa ser executado como Administrator!" -ForegroundColor Red
    Write-Host "Clique direito no PowerShell e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Crawler TJSP - Setup Automático" -ForegroundColor Cyan
Write-Host "  Windows Server 2016 - Contabo VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$TEMP_DIR = "C:\temp\installers"
$PYTHON_VERSION = "3.12.3"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-amd64.exe"
$GIT_URL = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$CHROME_URL = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$WEBSIGNER_URL = "https://websigner.softplan.com.br/downloads/websigner-2.12.1-win64.exe"

# Criar diretórios
Write-Host "📁 Criando estrutura de diretórios..." -ForegroundColor Yellow
$directories = @("C:\projetos", "C:\certs", "C:\temp", "C:\temp\installers", "C:\backups", "C:\logs", "C:\chromedriver")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Criado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✅ Já existe: $dir" -ForegroundColor Gray
    }
}

# ==========================================
# FASE 1: Python 3.12
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 1: Instalando Python 3.12" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$pythonInstaller = "$TEMP_DIR\python-$PYTHON_VERSION-amd64.exe"

if (-not (Test-Path $pythonInstaller)) {
    Write-Host "📥 Baixando Python $PYTHON_VERSION..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $PYTHON_URL -OutFile $pythonInstaller -ErrorAction Stop
        Write-Host "  ✅ Python baixado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao baixar Python: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ Python installer já baixado" -ForegroundColor Gray
}

Write-Host "🔧 Instalando Python..." -ForegroundColor Yellow
Start-Process -FilePath $pythonInstaller -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tcltk=0" -Wait -NoNewWindow

# Atualizar PATH na sessão atual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verificar instalação
Start-Sleep -Seconds 3
$pythonVersion = & python --version 2>&1
if ($pythonVersion -match "Python 3.12") {
    Write-Host "  ✅ Python instalado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Python pode não estar no PATH. Reinicie o PowerShell e tente novamente." -ForegroundColor Yellow
}

# Atualizar pip
Write-Host "🔧 Atualizando pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet

# Instalar ferramentas básicas
Write-Host "🔧 Instalando virtualenv, wheel, setuptools..." -ForegroundColor Yellow
& pip install virtualenv wheel setuptools --quiet
Write-Host "  ✅ Ferramentas Python instaladas!" -ForegroundColor Green

# ==========================================
# FASE 2: Git para Windows
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 2: Instalando Git" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$gitInstaller = "$TEMP_DIR\git-installer.exe"

if (-not (Test-Path $gitInstaller)) {
    Write-Host "📥 Baixando Git..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $GIT_URL -OutFile $gitInstaller -ErrorAction Stop
        Write-Host "  ✅ Git baixado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao baixar Git: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ Git installer já baixado" -ForegroundColor Gray
}

Write-Host "🔧 Instalando Git..." -ForegroundColor Yellow
Start-Process -FilePath $gitInstaller -Args "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS" -Wait -NoNewWindow

# Atualizar PATH
Start-Sleep -Seconds 5
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$gitVersion = & git --version 2>&1
if ($gitVersion -match "git version") {
    Write-Host "  ✅ Git instalado: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Git pode não estar no PATH. Reinicie o PowerShell." -ForegroundColor Yellow
}

# Configurar Git
Write-Host "🔧 Configurando Git..." -ForegroundColor Yellow
& git config --global user.name "Revisa Precatorio"
& git config --global user.email "revisa.precatorio@gmail.com"
& git config --global core.autocrlf true
Write-Host "  ✅ Git configurado!" -ForegroundColor Green

# ==========================================
# FASE 3: Google Chrome
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 3: Instalando Google Chrome" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$chromeInstaller = "$TEMP_DIR\chrome-installer.msi"

if (-not (Test-Path $chromeInstaller)) {
    Write-Host "📥 Baixando Chrome..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $CHROME_URL -OutFile $chromeInstaller -ErrorAction Stop
        Write-Host "  ✅ Chrome baixado com sucesso!" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Erro ao baixar Chrome: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ Chrome installer já baixado" -ForegroundColor Gray
}

Write-Host "🔧 Instalando Chrome..." -ForegroundColor Yellow
Start-Process -FilePath "msiexec.exe" -Args "/i $chromeInstaller /quiet /norestart" -Wait -NoNewWindow

$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
    Write-Host "  ✅ Chrome instalado: versão $chromeVersion" -ForegroundColor Green

    # Anotar major version para ChromeDriver
    $chromeMajorVersion = $chromeVersion.Split('.')[0]
    Write-Host "  📝 Chrome Major Version: $chromeMajorVersion (necessário para ChromeDriver)" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ Chrome não foi instalado corretamente!" -ForegroundColor Red
}

# ==========================================
# FASE 4: ChromeDriver
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 4: Instalando ChromeDriver" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "⚠️ ATENÇÃO: ChromeDriver precisa ser compatível com Chrome $chromeVersion" -ForegroundColor Yellow
Write-Host "📋 Acesse: https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor Cyan
Write-Host "   Procure pela versão $chromeVersion (ou mais próxima)" -ForegroundColor Cyan
Write-Host ""

# Exemplo para Chrome 122 (AJUSTAR conforme versão instalada)
$chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/$chromeVersion/win64/chromedriver-win64.zip"

Write-Host "🔍 Tentando baixar ChromeDriver para versão $chromeVersion..." -ForegroundColor Yellow
$chromedriverZip = "$TEMP_DIR\chromedriver.zip"

try {
    Invoke-WebRequest -Uri $chromedriverUrl -OutFile $chromedriverZip -ErrorAction Stop
    Write-Host "  ✅ ChromeDriver baixado!" -ForegroundColor Green

    # Extrair
    Expand-Archive -Path $chromedriverZip -DestinationPath "$TEMP_DIR\chromedriver-temp" -Force

    # Mover executável
    $chromedriverExe = Get-ChildItem -Path "$TEMP_DIR\chromedriver-temp" -Filter "chromedriver.exe" -Recurse | Select-Object -First 1
    if ($chromedriverExe) {
        Copy-Item -Path $chromedriverExe.FullName -Destination "C:\chromedriver\chromedriver.exe" -Force
        Write-Host "  ✅ ChromeDriver instalado em C:\chromedriver\chromedriver.exe" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️ Não foi possível baixar ChromeDriver automaticamente" -ForegroundColor Yellow
    Write-Host "  📝 Você precisará baixar manualmente:" -ForegroundColor Cyan
    Write-Host "     1. Acesse: https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor Cyan
    Write-Host "     2. Procure versão: $chromeVersion" -ForegroundColor Cyan
    Write-Host "     3. Baixe chromedriver-win64.zip" -ForegroundColor Cyan
    Write-Host "     4. Extraia chromedriver.exe para C:\chromedriver\" -ForegroundColor Cyan
}

# Adicionar ao PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*C:\chromedriver*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\chromedriver", [EnvironmentVariableTarget]::Machine)
    $env:Path += ";C:\chromedriver"
    Write-Host "  ✅ ChromeDriver adicionado ao PATH" -ForegroundColor Green
}

# ==========================================
# FASE 5: Web Signer (Download manual recomendado)
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 5: Web Signer (Softplan)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "⚠️ Web Signer precisa ser baixado manualmente:" -ForegroundColor Yellow
Write-Host "   1. Acesse: https://websigner.softplan.com.br/downloads" -ForegroundColor Cyan
Write-Host "   2. Baixe versão Windows (websigner-X.X.X-win64.exe)" -ForegroundColor Cyan
Write-Host "   3. Execute o instalador" -ForegroundColor Cyan
Write-Host "   4. Inicie o Web Signer (ficará na bandeja do sistema)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione qualquer tecla quando concluir a instalação do Web Signer..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Verificar se Web Signer foi instalado
$webSignerPath = "C:\Program Files\Softplan\WebSigner\websigner.exe"
if (Test-Path $webSignerPath) {
    Write-Host "  ✅ Web Signer encontrado em: $webSignerPath" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Web Signer não encontrado. Verifique a instalação." -ForegroundColor Yellow
}

# ==========================================
# FASE 6: Clonar Repositório
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 6: Clonando Repositório" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$repoPath = "C:\projetos\crawler_tjsp"
if (-not (Test-Path $repoPath)) {
    Write-Host "📥 Clonando repositório..." -ForegroundColor Yellow
    Set-Location "C:\projetos"
    & git clone https://github.com/revisaprecatorio/crawler_tjsp.git

    if (Test-Path $repoPath) {
        Write-Host "  ✅ Repositório clonado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Erro ao clonar repositório!" -ForegroundColor Red
    }
} else {
    Write-Host "  ✅ Repositório já existe em: $repoPath" -ForegroundColor Gray
}

# ==========================================
# FASE 7: Virtual Environment e Dependências
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FASE 7: Configurando Virtual Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location $repoPath

if (-not (Test-Path "$repoPath\venv")) {
    Write-Host "🔧 Criando virtual environment..." -ForegroundColor Yellow
    & python -m venv venv
    Write-Host "  ✅ Venv criado!" -ForegroundColor Green
} else {
    Write-Host "  ✅ Venv já existe" -ForegroundColor Gray
}

Write-Host "🔧 Instalando dependências do projeto..." -ForegroundColor Yellow
& "$repoPath\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "$repoPath\venv\Scripts\pip.exe" install -r requirements.txt --quiet
Write-Host "  ✅ Dependências instaladas!" -ForegroundColor Green

# ==========================================
# RESUMO FINAL
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ SETUP CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos Passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Transferir certificado .pfx para C:\certs\certificado.pfx" -ForegroundColor Yellow
Write-Host "   - Via RDP: arrastar e soltar do computador local" -ForegroundColor Gray
Write-Host "   - Via SCP: scp certificado.pfx Administrator@62.171.143.88:C:/certs/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Importar certificado no Windows Certificate Store:" -ForegroundColor Yellow
Write-Host "   - Duplo-clique no .pfx OU usar PowerShell:" -ForegroundColor Gray
Write-Host "   `$cert = ConvertTo-SecureString '903205' -AsPlainText -Force" -ForegroundColor Gray
Write-Host "   Import-PfxCertificate -FilePath C:\certs\certificado.pfx -CertStoreLocation Cert:\CurrentUser\My -Password `$cert" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configurar arquivo .env em C:\projetos\crawler_tjsp\.env" -ForegroundColor Yellow
Write-Host "   - Copiar de .env.example e preencher variáveis" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Testar autenticação:" -ForegroundColor Yellow
Write-Host "   cd C:\projetos\crawler_tjsp" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python tests\test_esaj_auth.py" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Documentação completa em:" -ForegroundColor Cyan
Write-Host "   C:\projetos\crawler_tjsp\windows-server\DEPLOYMENT_PLAN.md" -ForegroundColor Gray
Write-Host ""
