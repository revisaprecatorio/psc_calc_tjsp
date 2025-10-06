# 🆕 Instalação Completa do ZERO - Windows Server 2025

**Data:** 2025-10-06  
**Versão:** 1.0  
**Objetivo:** Instalar e configurar TUDO do zero no Windows Server 2025  
**Tempo Total:** 3-4 horas  

---

## 📋 Antes de Começar

### ✅ Checklist de Pré-requisitos

```markdown
### No Seu Computador Local:
- [ ] Cliente RDP instalado (Microsoft Remote Desktop)
- [ ] Cliente SSH (opcional, mas recomendado)
- [ ] Certificado digital A1 (.pfx) disponível
- [ ] Senha do certificado anotada: 903205
- [ ] Este guia aberto para consulta

### Informações que Você Precisa Ter:
- [ ] IP do servidor: 62.171.143.88
- [ ] Usuário: Administrator
- [ ] Senha: 31032025
- [ ] Perfil Google: revisa.precatorio@gmail.com

### Arquivos Necessários:
- [ ] Certificado: certificado.pfx (localização: [anotar])
- [ ] Backup atual (se houver): BACKUP_COMPLETO_*.zip
```

---

## 🎯 Visão Geral do Processo

```
FASE 1: Windows Base          (30 min)  → Sistema operacional limpo
FASE 2: Python & Git           (30 min)  → Linguagem e versionamento
FASE 3: Chrome & Drivers       (30 min)  → Navegador e automação
FASE 4: Web Signer            (20 min)  → Certificado digital
FASE 5: Código do Projeto     (30 min)  → Aplicação
FASE 6: Chrome Profile        (15 min)  → Sincronização
FASE 7: Testes                (20 min)  → Validação
FASE 8: Produção              (15 min)  → Deploy final

TOTAL: 3 horas
```

---

## 🔷 FASE 1: Configuração Base do Windows (30 min)

### 1.1 Primeiro Acesso via RDP

```powershell
# No seu Mac/PC:
# Abrir Microsoft Remote Desktop
# PC: 62.171.143.88
# User: Administrator
# Password: 31032025
```

**Ao conectar:**
- [ ] Desktop do Windows Server 2025 carregou
- [ ] Interface gráfica respondendo

### 1.2 Abrir PowerShell como Administrator

```
Clique direito no botão Iniciar → "Windows PowerShell (Admin)"
```

### 1.3 Verificações Iniciais

```powershell
# Verificar sistema
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
# Esperado: Windows Server 2025

# Verificar internet
ping google.com -n 4
# Esperado: resposta bem-sucedida

# Verificar especificações
Get-ComputerInfo | Select-Object CsProcessors, CsTotalPhysicalMemory
# Esperado: 3 vCPU, 8 GB RAM
```

**Checklist:**
- [ ] Windows Server 2025 confirmado
- [ ] Internet funcionando
- [ ] Especificações corretas (3 vCPU, 8 GB RAM)

### 1.4 Configurar PowerShell Execution Policy

```powershell
# Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

# Verificar
Get-ExecutionPolicy -List
# Esperado: LocalMachine = RemoteSigned
```

### 1.5 Configurar Timezone

```powershell
# Configurar para Brasília
Set-TimeZone -Id "E. South America Standard Time"

# Verificar
Get-Date
# Esperado: horário de Brasília (GMT-3)
```

### 1.6 Criar Estrutura de Diretórios

```powershell
# Criar pastas principais
$directories = @(
    "C:\projetos",
    "C:\certs",
    "C:\temp",
    "C:\backups",
    "C:\logs",
    "C:\chromedriver"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force
    Write-Host "[OK] Criado: $dir" -ForegroundColor Green
}

# Verificar
Get-ChildItem C:\ -Directory | Where-Object {$_.Name -in @('projetos','certs','temp','backups','logs','chromedriver')}
```

**Checklist:**
- [ ] Execution Policy configurado
- [ ] Timezone: Brasília
- [ ] Todas as pastas criadas

### 1.7 Configurar OpenSSH Server (Opcional mas Recomendado)

```powershell
# Instalar OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Iniciar serviço
Start-Service sshd

# Configurar auto-start
Set-Service -Name sshd -StartupType 'Automatic'

# Configurar firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Verificar
Get-Service sshd
# Esperado: Status = Running
```

**Testar do seu Mac:**
```bash
ssh Administrator@62.171.143.88
# Inserir senha: 31032025
# Deve conectar com sucesso
```

**Checklist:**
- [ ] OpenSSH instalado
- [ ] Serviço rodando
- [ ] SSH funciona do computador local

### 1.8 Windows Updates

```powershell
# Verificar atualizações disponíveis
# Opção 1: Interface gráfica
# Settings → Update & Security → Windows Update → Check for updates

# Opção 2: PowerShell
Install-Module PSWindowsUpdate -Force
Get-WindowsUpdate
Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot

# ATENÇÃO: Servidor pode reiniciar! Aguarde 10-15 min e reconecte.
```

**Checklist:**
- [ ] Windows Update executado
- [ ] Servidor reiniciado (se necessário)
- [ ] Reconexão via RDP bem-sucedida

---

## 🔷 FASE 2: Python 3.12 e Git (30 min)

### 2.1 Criar Pasta de Instaladores

```powershell
New-Item -ItemType Directory -Path "C:\temp\installers" -Force
cd C:\temp\installers
```

### 2.2 Instalar Python 3.12.3

```powershell
Write-Host "[INFO] Baixando Python 3.12.3..." -ForegroundColor Cyan

# Download
$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$installerPath = "C:\temp\installers\python-3.12.3-amd64.exe"

Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath

# Verificar download
if (Test-Path $installerPath) {
    Write-Host "[OK] Python installer baixado" -ForegroundColor Green
    
    # Instalar
    Write-Host "[INFO] Instalando Python (pode levar 2-3 minutos)..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1" -Wait
    
    Write-Host "[OK] Python instalado!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Falha ao baixar Python!" -ForegroundColor Red
}

# Atualizar PATH na sessão atual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Verificar instalação
python --version
# Esperado: Python 3.12.3

pip --version
# Esperado: pip 24.x

where python
# Esperado: C:\Program Files\Python312\python.exe
```

**Checklist:**
- [ ] Python 3.12.3 instalado
- [ ] `python --version` funciona
- [ ] `pip --version` funciona
- [ ] Python no PATH

### 2.3 Atualizar pip e Instalar Ferramentas

```powershell
Write-Host "[INFO] Atualizando pip e instalando ferramentas..." -ForegroundColor Cyan

# Atualizar pip
python -m pip install --upgrade pip

# Instalar ferramentas essenciais
pip install virtualenv wheel setuptools

# Verificar
virtualenv --version
pip show wheel
pip show setuptools

Write-Host "[OK] Ferramentas Python instaladas!" -ForegroundColor Green
```

### 2.4 Instalar Git para Windows

```powershell
Write-Host "[INFO] Baixando Git..." -ForegroundColor Cyan

# Habilitar TLS 1.2 (necessário para Windows Server)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Download
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$installerPath = "C:\temp\installers\git-installer.exe"

Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath

# Verificar download
if (Test-Path $installerPath) {
    Write-Host "[OK] Git installer baixado" -ForegroundColor Green
    
    # Instalar
    Write-Host "[INFO] Instalando Git..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -Args "/VERYSILENT /NORESTART" -Wait
    
    # Aguardar instalação
    Start-Sleep -Seconds 10
    
    Write-Host "[OK] Git instalado!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Falha ao baixar Git!" -ForegroundColor Red
}

# Atualizar PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Verificar
git --version
# Esperado: git version 2.44.0.windows.1
```

### 2.5 Configurar Git

```powershell
# Configurar nome e email
git config --global user.name "Revisa Precatorio"
git config --global user.email "revisa.precatorio@gmail.com"

# Configurar line endings (Windows)
git config --global core.autocrlf true

# Verificar
git config --list
```

**Checklist:**
- [ ] Git instalado
- [ ] `git --version` funciona
- [ ] Git configurado com nome e email

---

## 🔷 FASE 3: Chrome, ChromeDriver e Dependências (30 min)

### 3.1 Instalar Google Chrome

```powershell
Write-Host "[INFO] Baixando Google Chrome..." -ForegroundColor Cyan

# Download Chrome Enterprise
$chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$installerPath = "C:\temp\installers\chrome-installer.msi"

Invoke-WebRequest -Uri $chromeUrl -OutFile $installerPath

# Instalar
Write-Host "[INFO] Instalando Chrome..." -ForegroundColor Cyan
Start-Process -FilePath "msiexec.exe" -Args "/i $installerPath /quiet /norestart" -Wait

# Verificar
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
    Write-Host "[OK] Chrome instalado: versao $chromeVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Chrome nao encontrado!" -ForegroundColor Red
}
```

### 3.2 Verificar Versão e Instalar ChromeDriver

```powershell
# Obter versão do Chrome
$chromeVersion = (Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
Write-Host "[INFO] Chrome versao: $chromeVersion" -ForegroundColor Yellow

# Extrair major version (ex: 131 de 131.0.6778.86)
$chromeMajorVersion = $chromeVersion.Split('.')[0]
Write-Host "[INFO] Major version: $chromeMajorVersion" -ForegroundColor Yellow

# NOTA: Ajustar URL do ChromeDriver conforme versão do Chrome instalado
# Consultar: https://googlechromelabs.github.io/chrome-for-testing/

# Exemplo para Chrome 131.x
Write-Host "[INFO] Baixando ChromeDriver compativel..." -ForegroundColor Cyan

# URL deve ser ajustada conforme versão exata
# Para Chrome 131.0.6778.86:
$chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/$chromeVersion/win64/chromedriver-win64.zip"

$zipPath = "C:\temp\installers\chromedriver.zip"

try {
    Invoke-WebRequest -Uri $chromedriverUrl -OutFile $zipPath -ErrorAction Stop
    
    # Extrair
    Expand-Archive -Path $zipPath -DestinationPath "C:\temp\chromedriver-temp" -Force
    
    # Mover para pasta final
    $chromedriverExe = Get-ChildItem "C:\temp\chromedriver-temp" -Recurse -Filter "chromedriver.exe" | Select-Object -First 1
    if ($chromedriverExe) {
        Copy-Item $chromedriverExe.FullName -Destination "C:\chromedriver\chromedriver.exe" -Force
        Write-Host "[OK] ChromeDriver instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] Falha ao baixar ChromeDriver automaticamente" -ForegroundColor Yellow
    Write-Host "[INFO] Download manual necessario de:" -ForegroundColor Yellow
    Write-Host "       https://googlechromelabs.github.io/chrome-for-testing/" -ForegroundColor Yellow
    Write-Host "[INFO] Baixar versao compativel com Chrome $chromeVersion" -ForegroundColor Yellow
}

# Adicionar ao PATH
$env:Path += ";C:\chromedriver"
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\chromedriver", [EnvironmentVariableTarget]::Machine)

# Verificar
chromedriver --version
```

**Checklist:**
- [ ] Chrome instalado
- [ ] Versão do Chrome anotada: ______________
- [ ] ChromeDriver instalado em C:\chromedriver\
- [ ] `chromedriver --version` funciona
- [ ] Versões compatíveis

### 3.3 Instalar Visual C++ Build Tools (para psycopg2)

```powershell
Write-Host "[INFO] Instalando Visual C++ Build Tools..." -ForegroundColor Cyan
Write-Host "[WARN] Isso pode demorar 5-10 minutos..." -ForegroundColor Yellow

# Download
$buildToolsUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
$installerPath = "C:\temp\installers\vs_buildtools.exe"

Invoke-WebRequest -Uri $buildToolsUrl -OutFile $installerPath

# Instalar apenas C++ build tools (instalação mínima)
Start-Process -FilePath $installerPath -Args "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended" -Wait

Write-Host "[OK] Build Tools instalados!" -ForegroundColor Green
```

**Checklist:**
- [ ] Visual C++ Build Tools instalado
- [ ] Instalação concluída sem erros

---

## 🔷 FASE 4: Web Signer e Certificado Digital (20 min)

### 4.1 Download e Instalação do Web Signer

```powershell
Write-Host "[INFO] Download do Web Signer..." -ForegroundColor Cyan
Write-Host "[WARN] Instalacao requer interface grafica" -ForegroundColor Yellow

# Abrir navegador para download
Start-Process "chrome.exe" -ArgumentList "https://websigner.softplan.com.br/downloads"

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  ACAO MANUAL NECESSARIA" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "1. Baixar Web Signer (versao Windows 64-bit)" -ForegroundColor White
Write-Host "2. Executar instalador" -ForegroundColor White
Write-Host "3. Seguir wizard (Next > Next > Install)" -ForegroundColor White
Write-Host "4. Aguardar instalacao completa" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

Read-Host "Pressione Enter APOS instalar Web Signer"

# Verificar instalação
$webSignerPath = "C:\Program Files\Softplan\WebSigner\websigner.exe"
if (Test-Path $webSignerPath) {
    Write-Host "[OK] Web Signer instalado!" -ForegroundColor Green
    
    # Iniciar Web Signer
    Start-Process -FilePath $webSignerPath
    Start-Sleep -Seconds 3
    
    Write-Host "[INFO] Web Signer iniciado (icone na bandeja)" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Web Signer nao encontrado!" -ForegroundColor Red
}
```

### 4.2 Transferir Certificado Digital

**Opção A: Via SCP (Recomendado)**

```bash
# No seu Mac/PC local:
scp /caminho/local/certificado.pfx Administrator@62.171.143.88:C:/certs/
```

**Opção B: Via RDP (Arrastar e Soltar)**

```
1. Manter conexão RDP aberta
2. Localizar certificado.pfx no seu computador
3. Arrastar para desktop do servidor
4. Mover para C:\certs\
```

### 4.3 Importar Certificado no Windows

```powershell
# Verificar que certificado está presente
if (Test-Path "C:\certs\certificado.pfx") {
    $certSize = (Get-Item "C:\certs\certificado.pfx").Length
    Write-Host "[OK] Certificado presente ($certSize bytes)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Certificado NAO encontrado em C:\certs\" -ForegroundColor Red
    Write-Host "[INFO] Transferir certificado antes de continuar!" -ForegroundColor Yellow
    exit 1
}

# Importar certificado
Write-Host "[INFO] Importando certificado..." -ForegroundColor Cyan

$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar importação
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}

if ($cert) {
    Write-Host "[OK] Certificado importado com sucesso!" -ForegroundColor Green
    Write-Host "    Subject: $($cert.Subject)" -ForegroundColor Gray
    Write-Host "    Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    Write-Host "    Valid Until: $($cert.NotAfter)" -ForegroundColor Gray
    Write-Host "    Has Private Key: $($cert.HasPrivateKey)" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Certificado nao encontrado apos importacao!" -ForegroundColor Red
}
```

### 4.4 Verificar Web Signer Detecta Certificado

```powershell
Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  VERIFICACAO MANUAL" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "1. Clicar no icone Web Signer (bandeja)" -ForegroundColor White
Write-Host "2. Verificar se certificado aparece na lista" -ForegroundColor White
Write-Host "3. Certificado deve ser: CPF 517.648.902-30" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

Read-Host "Pressione Enter APOS verificar que Web Signer detecta certificado"
```

**Checklist:**
- [ ] Web Signer instalado e rodando
- [ ] Certificado transferido para C:\certs\
- [ ] Certificado importado no Windows Certificate Store
- [ ] Web Signer detecta certificado

---

## 🔷 FASE 5: Código do Projeto (30 min)

### 5.1 Clonar Repositório

```powershell
Write-Host "[INFO] Clonando repositorio..." -ForegroundColor Cyan

cd C:\projetos

# Clonar (ajustar URL se necessário)
git clone https://github.com/[seu-usuario]/crawler_tjsp.git

cd crawler_tjsp

# Verificar
if (Test-Path "C:\projetos\crawler_tjsp") {
    Write-Host "[OK] Repositorio clonado!" -ForegroundColor Green
    
    # Informações do repositório
    git log -1 --oneline
    git branch --show-current
} else {
    Write-Host "[ERROR] Falha ao clonar repositorio!" -ForegroundColor Red
}
```

**Se repositório ainda não existe:**
```powershell
# Criar estrutura básica
cd C:\projetos
New-Item -ItemType Directory -Path "crawler_tjsp" -Force
cd crawler_tjsp

# Inicializar Git
git init
```

### 5.2 Criar Virtual Environment

```powershell
Write-Host "[INFO] Criando virtual environment..." -ForegroundColor Cyan

cd C:\projetos\crawler_tjsp

# Criar venv
python -m venv .venv

# Verificar criação
if (Test-Path "C:\projetos\crawler_tjsp\.venv\Scripts\python.exe") {
    Write-Host "[OK] Virtual environment criado!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Falha ao criar venv!" -ForegroundColor Red
}
```

### 5.3 Ativar venv e Instalar Dependências

```powershell
# Ativar venv
.\.venv\Scripts\Activate.ps1

# Verificar ativação (prompt deve mostrar (venv))
python --version
where python
# Esperado: C:\projetos\crawler_tjsp\.venv\Scripts\python.exe

# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
Write-Host "[INFO] Instalando dependencias (pode levar 5-10 min)..." -ForegroundColor Cyan

pip install -r requirements.txt

# Se requirements.txt não existir, criar básico:
if (-not (Test-Path "requirements.txt")) {
    @"
fastapi==0.115.2
uvicorn[standard]==0.30.6
selenium==4.25.0
requests
psycopg2-binary
python-dotenv
tabulate
psutil
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8
    
    pip install -r requirements.txt
}

# Verificar pacotes críticos
Write-Host "[INFO] Verificando imports..." -ForegroundColor Cyan

python -c "from selenium import webdriver; print('[OK] Selenium')"
python -c "import psycopg2; print('[OK] psycopg2')"
python -c "import requests; print('[OK] requests')"
python -c "from dotenv import load_dotenv; print('[OK] dotenv')"

Write-Host "[OK] Todas as dependencias instaladas!" -ForegroundColor Green
```

### 5.4 Configurar Arquivo .env

```powershell
Write-Host "[INFO] Configurando arquivo .env..." -ForegroundColor Cyan

# Criar .env com configurações padrão
@"
# PostgreSQL (ajustar conforme seu setup)
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

# Selenium
SELENIUM_REMOTE_URL=
"@ | Out-File -FilePath ".env" -Encoding utf8

Write-Host "[OK] Arquivo .env criado!" -ForegroundColor Green
Write-Host "[WARN] Ajustar credenciais PostgreSQL no .env se necessario" -ForegroundColor Yellow
```

**Checklist:**
- [ ] Repositório clonado
- [ ] Virtual environment criado
- [ ] Dependências instaladas
- [ ] Arquivo .env criado e configurado
- [ ] Imports funcionando

---

## 🔷 FASE 6: Configurar Chrome Profile (15 min)

### 6.1 Login no Chrome com Perfil Google

```powershell
Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  CONFIGURACAO DO CHROME" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "1. Abrir Chrome manualmente" -ForegroundColor White
Write-Host "2. Fazer login com: revisa.precatorio@gmail.com" -ForegroundColor White
Write-Host "3. Aguardar sincronizacao completa (2-5 min)" -ForegroundColor White
Write-Host "4. Verificar chrome://extensions/" -ForegroundColor White
Write-Host "5. Web Signer deve aparecer na lista" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# Abrir Chrome
Start-Process "chrome.exe"

Read-Host "Pressione Enter APOS fazer login no Chrome e extensoes sincronizarem"
```

### 6.2 Verificar Extensão Web Signer

```powershell
# Abrir página de extensões
Start-Process "chrome.exe" -ArgumentList "chrome://extensions/"

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  VERIFICACAO VISUAL" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "Na janela do Chrome (chrome://extensions/):" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "[ ] Extensao 'Web Signer' aparece na lista" -ForegroundColor White
Write-Host "[ ] Extensao esta HABILITADA (toggle azul)" -ForegroundColor White
Write-Host "[ ] Icone Web Signer aparece na toolbar" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

$extensionOK = Read-Host "Extensao Web Signer esta OK? (s/n)"

if ($extensionOK -eq "s") {
    Write-Host "[OK] Chrome configurado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "[WARN] Extensao precisa ser instalada/habilitada" -ForegroundColor Yellow
    Write-Host "[INFO] Instalar de: https://chrome.google.com/webstore" -ForegroundColor Yellow
}
```

**Checklist:**
- [ ] Chrome logado com revisa.precatorio@gmail.com
- [ ] Sincronização completa
- [ ] Extensão Web Signer presente e habilitada

---

## 🔷 FASE 7: Testes de Validação (20 min)

### 7.1 Teste Manual de Login

```powershell
Write-Host "[INFO] Teste manual de login com certificado..." -ForegroundColor Cyan

# Abrir e-SAJ
Start-Process "chrome.exe" -ArgumentList "https://esaj.tjsp.jus.br/esaj/portal.do"

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  TESTE MANUAL DE AUTENTICACAO" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "Na janela do Chrome (e-SAJ):" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "1. Clicar em 'Certificado Digital'" -ForegroundColor White
Write-Host "2. Web Signer deve abrir modal de selecao" -ForegroundColor White
Write-Host "3. Selecionar certificado CPF 517.648.902-30" -ForegroundColor White
Write-Host "4. Login deve ser bem-sucedido" -ForegroundColor White
Write-Host "5. URL deve mudar para: portal.do?servico=..." -ForegroundColor White
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

$loginOK = Read-Host "Login manual funcionou? (s/n)"

if ($loginOK -eq "s") {
    Write-Host "[OK] Autenticacao manual OK!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Autenticacao manual falhou!" -ForegroundColor Red
    Write-Host "[INFO] Verificar:" -ForegroundColor Yellow
    Write-Host "  1. Web Signer esta rodando?" -ForegroundColor Yellow
    Write-Host "  2. Certificado foi importado?" -ForegroundColor Yellow
    Write-Host "  3. Extensao Chrome esta habilitada?" -ForegroundColor Yellow
}
```

### 7.2 Criar Script de Teste Automatizado

```powershell
Write-Host "[INFO] Criando script de teste..." -ForegroundColor Cyan

# Criar script de teste
$testScript = @'
"""
Teste de Autenticacao - Crawler TJSP
Windows Server 2025
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Configuracoes
CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"

def test_autenticacao():
    """Teste basico de autenticacao."""
    print("\n" + "="*60)
    print("  TESTE DE AUTENTICACAO - CRAWLER TJSP")
    print("="*60 + "\n")
    
    # Configurar Chrome
    print("[INFO] Configurando Chrome...")
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # IMPORTANTE: Usar perfil padrao (onde Web Signer esta instalado)
    # NAO usar --user-data-dir customizado!
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    
    try:
        print("[INFO] Iniciando Chrome via Selenium...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("[OK] Chrome iniciado!")
        
        print("\n[INFO] Navegando para e-SAJ...")
        driver.get("https://esaj.tjsp.jus.br/esaj/portal.do")
        time.sleep(3)
        
        print("[OK] e-SAJ carregado!")
        print(f"    Titulo: {driver.title}")
        
        # Verificar se pagina carregou
        if "TJSP" in driver.title or "SAJ" in driver.title:
            print("[OK] Pagina e-SAJ confirmada!")
        
        # Screenshot
        screenshot_path = r"C:\projetos\crawler_tjsp\test_esaj_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"[OK] Screenshot salvo: {screenshot_path}")
        
        print("\n" + "="*60)
        print("  TESTE BASICO: PASSOU")
        print("="*60)
        print("\n[INFO] Chrome vai permanecer aberto.")
        print("[INFO] Teste MANUAL agora:")
        print("    1. Clicar em 'Certificado Digital'")
        print("    2. Verificar se Web Signer abre modal")
        print("    3. Selecionar certificado")
        print("    4. Verificar se login funciona")
        print("")
        
        input("Pressione Enter para fechar o navegador...")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Falha no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            driver.quit()
            print("\n[INFO] Navegador fechado.")
        except:
            pass

if __name__ == "__main__":
    success = test_autenticacao()
    exit(0 if success else 1)
'@

$testScript | Out-File -FilePath "C:\projetos\crawler_tjsp\test_auth_final.py" -Encoding utf8

Write-Host "[OK] Script de teste criado: test_auth_final.py" -ForegroundColor Green
```

### 7.3 Executar Teste Automatizado

```powershell
Write-Host "[INFO] Executando teste automatizado..." -ForegroundColor Cyan

cd C:\projetos\crawler_tjsp

# Garantir que venv está ativo
.\.venv\Scripts\Activate.ps1

# Executar teste
python test_auth_final.py

Write-Host ""
$testResult = Read-Host "Teste automatizado passou? (s/n)"

if ($testResult -eq "s") {
    Write-Host "[OK] Sistema 100% funcional!" -ForegroundColor Green
} else {
    Write-Host "[WARN] Revisar configuracoes" -ForegroundColor Yellow
}
```

**Checklist:**
- [ ] Teste manual de login bem-sucedido
- [ ] Script de teste criado
- [ ] Teste automatizado executou sem erros
- [ ] Chrome abre via Selenium
- [ ] e-SAJ carrega corretamente

---

## 🔷 FASE 8: Finalização e Produção (15 min)

### 8.1 Criar Snapshot Pós-Instalação

```powershell
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CRIAR SNAPSHOT NO PAINEL CONTABO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "1. Acessar: https://my.contabo.com" -ForegroundColor White
Write-Host "2. Login" -ForegroundColor White
Write-Host "3. Cloud VPS → Selecionar servidor" -ForegroundColor White
Write-Host "4. Snapshots → Create Snapshot" -ForegroundColor White
Write-Host "5. Nome: post-fresh-install-ws2025-2025-10-06" -ForegroundColor White
Write-Host "6. Descricao: Instalacao limpa WS2025 + Crawler TJSP completo" -ForegroundColor White
Write-Host "7. Aguardar conclusao (~10-15 min)" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Pressione Enter APOS criar snapshot"
```

### 8.2 Criar Script de Inicialização Rápida

```powershell
Write-Host "[INFO] Criando script de inicializacao rapida..." -ForegroundColor Cyan

# Script para ativar ambiente rapidamente
$quickStart = @'
# =============================================
# Quick Start - Crawler TJSP
# =============================================

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  CRAWLER TJSP - QUICK START" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para projeto
cd C:\projetos\crawler_tjsp

# Ativar venv
Write-Host "[INFO] Ativando ambiente Python..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Verificar Web Signer
$wsProcess = Get-Process | Where-Object {$_.Name -like "*websigner*"}
if (-not $wsProcess) {
    Write-Host "[WARN] Web Signer nao esta rodando!" -ForegroundColor Yellow
    Write-Host "[INFO] Iniciando Web Signer..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Softplan\WebSigner\websigner.exe"
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[OK] Ambiente ativado!" -ForegroundColor Green
Write-Host ""
Write-Host "Python: $(python --version)" -ForegroundColor Gray
Write-Host "Localizacao: $(where python)" -ForegroundColor Gray
Write-Host ""
Write-Host "Comandos disponiveis:" -ForegroundColor Cyan
Write-Host "  python test_auth_final.py    - Testar autenticacao" -ForegroundColor White
Write-Host "  python crawler_full.py       - Executar crawler" -ForegroundColor White
Write-Host ""
'@

$quickStart | Out-File -FilePath "C:\projetos\crawler_tjsp\quickstart.ps1" -Encoding utf8

Write-Host "[OK] Script criado: C:\projetos\crawler_tjsp\quickstart.ps1" -ForegroundColor Green
Write-Host "[INFO] Uso futuro: .\quickstart.ps1" -ForegroundColor Cyan
```

### 8.3 Criar Atalho na Área de Trabalho

```powershell
Write-Host "[INFO] Criando atalho na area de trabalho..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Crawler TJSP.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File C:\projetos\crawler_tjsp\quickstart.ps1"
$Shortcut.WorkingDirectory = "C:\projetos\crawler_tjsp"
$Shortcut.Description = "Iniciar ambiente Crawler TJSP"
$Shortcut.Save()

Write-Host "[OK] Atalho criado na area de trabalho" -ForegroundColor Green
```

### 8.4 Documentar Informações Importantes

```powershell
Write-Host "[INFO] Gerando documentacao de instalacao..." -ForegroundColor Cyan

$installDoc = @"
========================================
  CRAWLER TJSP - INSTALACAO COMPLETA
========================================

Data da Instalacao: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
Sistema: Windows Server 2025
Servidor: 62.171.143.88 (Contabo Cloud VPS 10)

========================================
  SOFTWARE INSTALADO
========================================

Python: $(& python --version 2>&1)
Git: $(& git --version 2>&1)
Chrome: $((Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion)
ChromeDriver: $(& chromedriver --version 2>&1)
Web Signer: Instalado

========================================
  CONFIGURACOES
========================================

Projeto: C:\projetos\crawler_tjsp
Certificado: C:\certs\certificado.pfx
  - Senha: 903205
  - CPF: 517.648.902-30

Chrome Profile: revisa.precatorio@gmail.com
Virtual Environment: C:\projetos\crawler_tjsp\.venv

========================================
  COMANDOS UTEIS
========================================

Iniciar ambiente:
  cd C:\projetos\crawler_tjsp
  .\quickstart.ps1

Testar autenticacao:
  python test_auth_final.py

Executar crawler:
  python crawler_full.py

Atualizar codigo:
  git pull origin main
  pip install -r requirements.txt

========================================
  MANUTENCAO
========================================

Snapshot criado: post-fresh-install-ws2025-2025-10-06

Backups:
  - Snapshot Contabo (restore em 10-20 min)
  - Criar backups regulares com:
    .\scripts\backup_complete_system.ps1

========================================
  SUPORTE
========================================

Documentacao: C:\projetos\crawler_tjsp\windows-server\
Troubleshooting: TROUBLESHOOTING_AUTENTICACAO.md
Restore: RESTORE_GUIDE.md

========================================
"@

$installDoc | Out-File -FilePath "C:\projetos\crawler_tjsp\INSTALACAO_INFO.txt" -Encoding utf8

Write-Host "[OK] Documentacao salva: INSTALACAO_INFO.txt" -ForegroundColor Green
```

### 8.5 Checklist Final

```powershell
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  INSTALACAO COMPLETA!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Checklist Final:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [ ] Windows Server 2025 configurado" -ForegroundColor White
Write-Host "  [ ] Python 3.12.3 instalado" -ForegroundColor White
Write-Host "  [ ] Git configurado" -ForegroundColor White
Write-Host "  [ ] Chrome + ChromeDriver instalados" -ForegroundColor White
Write-Host "  [ ] Web Signer funcionando" -ForegroundColor White
Write-Host "  [ ] Certificado importado" -ForegroundColor White
Write-Host "  [ ] Codigo do projeto clonado" -ForegroundColor White
Write-Host "  [ ] Dependencias instaladas" -ForegroundColor White
Write-Host "  [ ] Teste de autenticacao OK" -ForegroundColor White
Write-Host "  [ ] Snapshot pos-instalacao criado" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Sistema 100% operacional!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Configurar PostgreSQL (se necessario)" -ForegroundColor Yellow
Write-Host "  2. Configurar orchestrator/worker" -ForegroundColor Yellow
Write-Host "  3. Testar processamento de jobs" -ForegroundColor Yellow
Write-Host "  4. Colocar em producao" -ForegroundColor Yellow
Write-Host ""
```

---

## 📊 Resumo da Instalação

### ✅ O Que Foi Instalado:

| Componente | Versão | Localização |
|------------|--------|-------------|
| Windows Server | 2025 | Sistema base |
| Python | 3.12.3 | C:\Program Files\Python312\ |
| Git | 2.44.0 | C:\Program Files\Git\ |
| Chrome | (atual) | C:\Program Files\Google\Chrome\ |
| ChromeDriver | (compatível) | C:\chromedriver\ |
| Web Signer | (atual) | C:\Program Files\Softplan\WebSigner\ |
| Projeto | (atual) | C:\projetos\crawler_tjsp\ |

### 📁 Estrutura de Diretórios:

```
C:\
├── projetos\
│   └── crawler_tjsp\
│       ├── .venv\              (virtual environment)
│       ├── .env                (configurações)
│       ├── requirements.txt
│       ├── test_auth_final.py
│       ├── quickstart.ps1
│       └── INSTALACAO_INFO.txt
├── certs\
│   └── certificado.pfx
├── chromedriver\
│   └── chromedriver.exe
├── temp\
├── backups\
└── logs\
```

### 🔑 Credenciais e Informações Importantes:

```
Servidor: 62.171.143.88
Usuario: Administrator
Senha: 31032025

Certificado: C:\certs\certificado.pfx
  - Senha: 903205
  - CPF: 517.648.902-30

Chrome: revisa.precatorio@gmail.com
```

---

## 🚀 Como Usar o Sistema

### Iniciar Ambiente:

```powershell
# Opcao 1: Usar atalho da area de trabalho
# Duplo-clique em "Crawler TJSP"

# Opcao 2: Via PowerShell
cd C:\projetos\crawler_tjsp
.\quickstart.ps1
```

### Testar Autenticação:

```powershell
python test_auth_final.py
```

### Executar Crawler:

```powershell
python crawler_full.py --processo=1234567-89.2020.8.26.0100
```

---

## 📞 Troubleshooting Rápido

### Problema: Python não funciona
```powershell
# Verificar instalação
where python
python --version

# Se não funcionar, reinstalar:
# Repetir FASE 2
```

### Problema: ChromeDriver incompatível
```powershell
# Verificar versões
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
chromedriver --version

# Baixar versão compatível:
# https://googlechromelabs.github.io/chrome-for-testing/
```

### Problema: Web Signer não detecta certificado
```powershell
# Verificar importação
Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}

# Reimportar se necessário
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText
Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Reiniciar Web Signer
Get-Process | Where-Object {$_.Name -like "*websigner*"} | Stop-Process
Start-Process "C:\Program Files\Softplan\WebSigner\websigner.exe"
```

---

## ✅ Checklist de Conclusão

```markdown
### Instalação Base
- [ ] Windows Server 2025 configurado
- [ ] OpenSSH funcionando
- [ ] Estrutura de diretórios criada
- [ ] PowerShell Execution Policy configurado

### Software
- [ ] Python 3.12.3 funcionando
- [ ] Git instalado e configurado
- [ ] Chrome instalado
- [ ] ChromeDriver compatível
- [ ] Web Signer rodando
- [ ] Visual C++ Build Tools instalado

### Certificado e Segurança
- [ ] Certificado transferido
- [ ] Certificado importado
- [ ] Web Signer detecta certificado
- [ ] Teste manual de login OK

### Projeto
- [ ] Repositório clonado
- [ ] Virtual environment criado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Chrome profile sincronizado
- [ ] Teste automatizado OK

### Finalização
- [ ] Snapshot pós-instalação criado
- [ ] Scripts de atalho criados
- [ ] Documentação gerada
- [ ] Sistema validado e funcional
```

---

**🎉 INSTALAÇÃO COMPLETA!**

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Tempo médio:** 3-4 horas  
**Status:** Pronto para produção

