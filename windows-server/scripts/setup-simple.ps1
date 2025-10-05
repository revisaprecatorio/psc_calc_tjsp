# ==========================================
# Setup Simplificado - Windows Server
# Crawler TJSP - Migração para Windows
# ==========================================

$ErrorActionPreference = 'Stop'

function Ensure-Dir($path) {
  if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

function Download-File($url, $outPath, $timeoutSec = 60, $retries = 3) {
  # tenta com BITS (melhor p/ Server/Proxy) e cai para Invoke-WebRequest
  for ($i=1; $i -le $retries; $i++) {
    try {
      try {
        Start-BitsTransfer -Source $url -Destination $outPath -ErrorAction Stop
      } catch {
        Invoke-WebRequest -Uri $url -OutFile $outPath -TimeoutSec $timeoutSec -UseBasicParsing -ErrorAction Stop
      }
      if ((Test-Path $outPath) -and ((Get-Item $outPath).Length -gt 0)) { return $true }
      throw "Arquivo vazio."
    } catch {
      if ($i -eq $retries) { throw }
      Start-Sleep -Seconds ([int][math]::Min(30, 2*$i))
    }
  }
}

function Broadcast-EnvPath {
  $sig = @"
using System;
using System.Runtime.InteropServices;
public class NativeMethods {
  [DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
  public static extern IntPtr SendMessageTimeout(IntPtr hWnd, int Msg, IntPtr wParam, string lParam, int fuFlags, int uTimeout, out IntPtr lpdwResult);
}
"@
  Add-Type $sig -ErrorAction SilentlyContinue | Out-Null
  [void][NativeMethods]::SendMessageTimeout([IntPtr]0xffff,0x1A,[IntPtr]0,"Environment",2,5000,[ref]([IntPtr]::Zero))
}

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
$directories | ForEach-Object { Ensure-Dir $_; Write-Host "  OK: $_" -ForegroundColor Green }

# ==========================================
# FASE 2: Python 3.12
# ==========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALANDO PYTHON 3.12.3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$pythonInstaller = "C:\temp\python-installer.exe"
$pythonLog = "C:\logs\python_install.log"

Write-Host "Baixando Python 3.12.3..." -ForegroundColor Yellow
if (-not (Test-Path $pythonInstaller)) {
  Download-File $pythonUrl $pythonInstaller | Out-Null
  Write-Host "  Download concluido!" -ForegroundColor Green
} else {
  Write-Host "  Instalador ja existe" -ForegroundColor Gray
}

Write-Host "Instalando Python (pode demorar 2-3 minutos)..." -ForegroundColor Yellow
$pyArgs = @(
  '/quiet',
  'InstallAllUsers=1',
  'PrependPath=1',
  'Include_test=0',
  'Include_pip=1',
  'Include_tcltk=0',
  "Log=$pythonLog"
)
$pyProc = Start-Process -FilePath $pythonInstaller -ArgumentList $pyArgs -Wait -PassThru -WindowStyle Hidden
if ($pyProc.ExitCode -ne 0) {
  Write-Host "  ERRO: Instalação do Python falhou. ExitCode=$($pyProc.ExitCode). Veja $pythonLog" -ForegroundColor Red
  exit $pyProc.ExitCode
}
Write-Host "  Python instalado!" -ForegroundColor Green

# Atualizar PATH na sessao atual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Start-Sleep -Seconds 3

# Verificar instalacao
try {
  $pythonVersion = & python --version 2>&1
  Write-Host "  Versao instalada: $pythonVersion" -ForegroundColor Cyan
} catch {
  Write-Host "  AVISO: Python pode nao estar no PATH. Reinicie o PowerShell apos o script." -ForegroundColor Yellow
}

# Atualizar pip e ferramentas
Write-Host "Atualizando pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip --quiet 2>&1 | Out-Null
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
$chromeLog = "C:\logs\chrome_install.log"

Write-Host "Baixando Google Chrome..." -ForegroundColor Yellow
if (-not (Test-Path $chromeInstaller)) {
  Download-File $chromeUrl $chromeInstaller | Out-Null
  Write-Host "  Download concluido!" -ForegroundColor Green
} else {
  Write-Host "  Instalador ja existe" -ForegroundColor Gray
}

Write-Host "Instalando Chrome (pode demorar 1-3 minutos)..." -ForegroundColor Yellow
$msiArgs = @(
  '/i', "`"$chromeInstaller`"",
  '/qn',
  '/norestart',
  '/L*v', $chromeLog
)
$msi = Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait -PassThru -WindowStyle Hidden

if ($msi.ExitCode -in 0,3010) {
  Write-Host "  Chrome instalado! (ExitCode=$($msi.ExitCode))" -ForegroundColor Green
  if ($msi.ExitCode -eq 3010) { Write-Host "  OBS: Requer reinicialização." -ForegroundColor Yellow }
} else {
  Write-Host "  Falha na instalação do Chrome. ExitCode=$($msi.ExitCode). Log: $chromeLog" -ForegroundColor Red
  exit $msi.ExitCode
}

# Verificar versao do Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$chromeVersion = $null
if (Test-Path $chromePath) {
  $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
  Write-Host "  Versao do Chrome: $chromeVersion" -ForegroundColor Cyan
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
Write-Host "CHROMEDRIVER (Instalacao Automatica/Assistida)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Ensure-Dir "C:\chromedriver"
Ensure-Dir "C:\temp"

$chromedriverZip = "C:\temp\chromedriver.zip"
$tmpExtract      = "C:\temp\chromedriver-temp"
Remove-Item $chromedriverZip -ErrorAction SilentlyContinue
Remove-Item $tmpExtract -Recurse -Force -ErrorAction SilentlyContinue

if (-not $chromeVersion) {
  Write-Host "  AVISO: Sem versao do Chrome detectada; tente manualmente." -ForegroundColor Yellow
} else {
  Write-Host "Detectando versão do ChromeDriver compatível..." -ForegroundColor Yellow
  $major = $chromeVersion.Split('.')[0]

  # tenta EXATA
  $exactUrl = "https://storage.googleapis.com/chrome-for-testing-public/$chromeVersion/win64/chromedriver-win64.zip"
  $dlOk = $false
  try {
    Write-Host "Tentando baixar versão EXATA: $chromeVersion" -ForegroundColor Yellow
    $dlOk = Download-File $exactUrl $chromedriverZip
    if ($dlOk) { Write-Host "  OK (exata)" -ForegroundColor Green }
  } catch {
    Write-Host "  Versao exata nao encontrada ou rede bloqueada." -ForegroundColor DarkYellow
  }

  # fallback por major
  if (-not $dlOk) {
    try {
      $kvg = Invoke-RestMethod "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
      $fallbackVersion = ($kvg.versions | Where-Object { $_.version -like "$major.*" } | Select-Object -Last 1).version
      if ($fallbackVersion) {
        $fallbackUrl = "https://storage.googleapis.com/chrome-for-testing-public/$fallbackVersion/win64/chromedriver-win64.zip"
        Write-Host "Tentando fallback do mesmo major ($major): $fallbackVersion" -ForegroundColor Yellow
        $dlOk = Download-File $fallbackUrl $chromedriverZip
        if ($dlOk) { Write-Host "  OK (fallback $fallbackVersion)" -ForegroundColor Green }
      }
    } catch {
      Write-Host "  Falha ao obter lista de versões conhecidas." -ForegroundColor Red
    }
  }

  if ($dlOk) {
    Write-Host "Extraindo ChromeDriver..." -ForegroundColor Yellow
    Expand-Archive -Path $chromedriverZip -DestinationPath $tmpExtract -Force
    $exe = Get-ChildItem -Path $tmpExtract -Filter "chromedriver.exe" -Recurse | Select-Object -First 1
    if (-not $exe) {
      Write-Host "  ERRO: chromedriver.exe não encontrado no ZIP." -ForegroundColor Red
      exit 1
    }
    Copy-Item $exe.FullName -Destination "C:\chromedriver\chromedriver.exe" -Force
    Write-Host "ChromeDriver instalado em C:\chromedriver\chromedriver.exe" -ForegroundColor Green
  } else {
    Write-Host "  Download automatico falhou (normal se versao exata nao existir)." -ForegroundColor Yellow
    Write-Host "  Instale manualmente em: https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor Yellow
  }

  # limpeza
  Remove-Item $tmpExtract -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item $chromedriverZip -Force -ErrorAction SilentlyContinue
}

# Adicionar ao PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if ($currentPath -notlike "*C:\chromedriver*") {
  [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\chromedriver", [EnvironmentVariableTarget]::Machine)
  $env:Path += ";C:\chromedriver"
  Broadcast-EnvPath
  Write-Host "  ChromeDriver adicionado ao PATH" -ForegroundColor Green
}

# Verificação final do chromedriver (se existir)
if (Test-Path "C:\chromedriver\chromedriver.exe") {
  try {
    $drvVer = & "C:\chromedriver\chromedriver.exe" --version
    Write-Host "  ChromeDriver: $drvVer" -ForegroundColor Cyan
  } catch { }
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
try {
  $pyv = & python --version 2>&1
  Write-Host "  - $pyv" -ForegroundColor White
} catch {
  Write-Host "  - Python 3.12.3 (verificar PATH)" -ForegroundColor White
}
if ($chromeVersion) { Write-Host "  - Google Chrome $chromeVersion" -ForegroundColor White } else { Write-Host "  - Google Chrome (verificar instalação)" -ForegroundColor White }
if (Test-Path "C:\chromedriver\chromedriver.exe") { Write-Host "  - ChromeDriver (no PATH)" -ForegroundColor White } else { Write-Host "  - ChromeDriver (instalação manual pode ser necessária)" -ForegroundColor White }
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
Write-Host "   - Baixe versao compativel com Chrome detectado" -ForegroundColor White
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
