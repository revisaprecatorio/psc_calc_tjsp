# 🐍 Instalação do Python 3.12 e Dependências

**Fase 2 do Deployment Plan**
**Tempo estimado:** 30-40 minutos

---

## 📋 Pré-requisitos

- [ ] Fase 1 concluída ([01_initial_server_setup.md](01_initial_server_setup.md))
- [ ] Acesso RDP ao servidor funcionando
- [ ] PowerShell aberto como Administrator
- [ ] Internet funcionando

---

## 1️⃣ Instalação do Python 3.12

### 1.1 Download do Python

```powershell
# Criar pasta temporária
New-Item -ItemType Directory -Path "C:\temp\installers" -Force
cd C:\temp\installers

# Download Python 3.12.3 (versão estável mais recente)
$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$installerPath = "C:\temp\installers\python-3.12.3-amd64.exe"

Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath

# Verificar download
if (Test-Path $installerPath) {
    Write-Host "✅ Python installer baixado com sucesso!" -ForegroundColor Green
    Get-Item $installerPath | Select-Object Name, Length, LastWriteTime
} else {
    Write-Host "❌ Erro ao baixar Python installer" -ForegroundColor Red
}
```

### 1.2 Instalação Silenciosa

```powershell
# Instalar Python com todas as features
# Flags importantes:
#   - InstallAllUsers=1  → Instala para todos os usuários (C:\Program Files\Python312)
#   - PrependPath=1      → Adiciona Python ao PATH automaticamente
#   - Include_test=0     → Não instala suite de testes (economiza espaço)
#   - Include_pip=1      → Instala pip
#   - Include_tcltk=0    → Não instala Tkinter (GUI não necessária)

Start-Process -FilePath $installerPath -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tcltk=0" -Wait

Write-Host "✅ Instalação concluída!" -ForegroundColor Green
```

### 1.3 Verificar Instalação

```powershell
# Fechar e reabrir PowerShell para atualizar PATH
# Ou atualizar PATH na sessão atual:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verificar Python
python --version
# Esperado: Python 3.12.3

# Verificar pip
pip --version
# Esperado: pip 24.x from C:\Program Files\Python312\...

# Verificar localização
where python
# Esperado: C:\Program Files\Python312\python.exe

# Testar Python interativo
python -c "print('Hello from Python 3.12!')"
# Esperado: Hello from Python 3.12!
```

**Checklist:**
- [ ] `python --version` retorna 3.12.x
- [ ] `pip --version` funciona
- [ ] Python está no PATH
- [ ] Python executável em `C:\Program Files\Python312\python.exe`

---

## 2️⃣ Atualizar pip e Instalar Ferramentas Básicas

### 2.1 Atualizar pip

```powershell
# Atualizar pip para versão mais recente
python -m pip install --upgrade pip

# Verificar
pip --version
```

### 2.2 Instalar virtualenv

```powershell
# Instalar virtualenv (para criar ambientes isolados)
pip install virtualenv

# Verificar
virtualenv --version
```

### 2.3 Instalar wheel e setuptools

```powershell
# Instalar wheel e setuptools (necessários para compilar alguns pacotes)
pip install --upgrade wheel setuptools

# Verificar
pip show wheel
pip show setuptools
```

**Checklist:**
- [ ] pip atualizado para versão mais recente
- [ ] virtualenv instalado
- [ ] wheel e setuptools instalados

---

## 3️⃣ Instalação do Git para Windows

### 3.1 Download do Git

```powershell
# Download Git para Windows
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$installerPath = "C:\temp\installers\git-installer.exe"

Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath

# Verificar download
if (Test-Path $installerPath) {
    Write-Host "✅ Git installer baixado!" -ForegroundColor Green
}
```

### 3.2 Instalação Silenciosa do Git

```powershell
# Instalar Git silenciosamente
Start-Process -FilePath $installerPath -Args "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS='icons,ext\reg\shellhere,assoc,assoc_sh'" -Wait

# Aguardar instalação
Start-Sleep -Seconds 10

# Atualizar PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### 3.3 Configurar Git

```powershell
# Verificar instalação
git --version
# Esperado: git version 2.44.0.windows.1

# Configurar nome e email (usar suas credenciais)
git config --global user.name "Revisa Precatorio"
git config --global user.email "revisa.precatorio@gmail.com"

# Configurar line endings (Windows)
git config --global core.autocrlf true

# Verificar configuração
git config --list
```

**Checklist:**
- [ ] `git --version` funciona
- [ ] Git configurado com nome e email
- [ ] Git está no PATH

---

## 4️⃣ Instalar Microsoft Visual C++ Build Tools

Alguns pacotes Python (como `psycopg2`) precisam compilar extensões em C. O Visual C++ Build Tools é necessário para isso.

### 4.1 Download das Build Tools

**Opção A: Via Chocolatey (Recomendado)**

```powershell
# Instalar via Chocolatey (mais rápido)
choco install visualstudio2022buildtools -y

# Instalar workloads necessários
choco install visualstudio2022-workload-vctools -y
```

**Opção B: Download Manual**

```powershell
# Download do instalador
$buildToolsUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
$installerPath = "C:\temp\installers\vs_buildtools.exe"

Invoke-WebRequest -Uri $buildToolsUrl -OutFile $installerPath

# Instalar apenas C++ build tools (instalação mínima)
Start-Process -FilePath $installerPath -Args "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended" -Wait
```

### 4.2 Verificar Instalação

```powershell
# Verificar se cl.exe (compilador C++) está disponível
$vcPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"
if (Test-Path $vcPath) {
    Write-Host "✅ Visual C++ Build Tools instalado!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Build Tools não encontrado em $vcPath" -ForegroundColor Yellow
}
```

**Checklist:**
- [ ] Visual C++ Build Tools instalado
- [ ] Caminho `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\` existe

---

## 5️⃣ Testar Compilação de Pacotes Python

### 5.1 Testar psycopg2 (PostgreSQL adapter)

```powershell
# Tentar instalar psycopg2 (que precisa compilar código C)
pip install psycopg2

# Se der erro, tentar versão binary (pré-compilada):
pip install psycopg2-binary

# Verificar
pip show psycopg2-binary
```

**Se `psycopg2` compilar com sucesso:**
- ✅ Visual C++ Build Tools está funcionando

**Se der erro de compilação:**
- Usar `psycopg2-binary` (versão standalone, não precisa compilar)
- Para produção, `psycopg2-binary` é aceitável

### 5.2 Testar cryptography

```powershell
# Testar outro pacote que compila extensões
pip install cryptography

# Verificar
pip show cryptography
```

**Checklist:**
- [ ] `psycopg2-binary` instalado com sucesso
- [ ] `cryptography` instalado com sucesso

---

## 6️⃣ Criar Estrutura de Projeto

### 6.1 Criar Pasta do Projeto

```powershell
# Criar pasta principal
New-Item -ItemType Directory -Path "C:\projetos\crawler_tjsp" -Force

# Navegar
cd C:\projetos\crawler_tjsp
```

### 6.2 Criar Virtual Environment

```powershell
# Criar venv
python -m venv venv

# Verificar criação
if (Test-Path "C:\projetos\crawler_tjsp\venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment criado!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao criar venv" -ForegroundColor Red
}
```

### 6.3 Ativar Virtual Environment

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Se der erro de ExecutionPolicy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\venv\Scripts\Activate.ps1

# Verificar ativação (prompt deve mostrar (venv))
python --version
pip --version

# Verificar que está usando Python do venv
where python
# Esperado: C:\projetos\crawler_tjsp\venv\Scripts\python.exe
```

**Checklist:**
- [ ] venv criado em `C:\projetos\crawler_tjsp\venv`
- [ ] venv ativado (prompt mostra `(venv)`)
- [ ] `python` aponta para venv

---

## 7️⃣ Instalar Dependências Básicas do Projeto

### 7.1 Criar requirements.txt Temporário

```powershell
# Criar requirements.txt básico (será substituído pelo do repositório)
@"
selenium==4.18.1
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.1
pillow==10.2.0
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8
```

### 7.2 Instalar Dependências

```powershell
# Com venv ativado
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalações
pip list
```

### 7.3 Verificar Pacotes Críticos

```powershell
# Selenium
python -c "from selenium import webdriver; print('✅ Selenium importado com sucesso!')"

# psycopg2
python -c "import psycopg2; print('✅ psycopg2 importado com sucesso!')"

# requests
python -c "import requests; print('✅ requests importado com sucesso!')"

# dotenv
python -c "from dotenv import load_dotenv; print('✅ dotenv importado com sucesso!')"
```

**Checklist:**
- [ ] Todas as dependências instaladas sem erros
- [ ] Imports funcionam corretamente

---

## 8️⃣ Configurar Variáveis de Ambiente do Sistema

### 8.1 Adicionar Variáveis Permanentes

```powershell
# Adicionar Python ao PATH do sistema (se ainda não estiver)
$pythonPath = "C:\Program Files\Python312"
$scriptsPath = "C:\Program Files\Python312\Scripts"

[Environment]::SetEnvironmentVariable("Path", "$env:Path;$pythonPath;$scriptsPath", [EnvironmentVariableTarget]::Machine)

# Criar variável PYTHONPATH (opcional)
[Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\projetos\crawler_tjsp", [EnvironmentVariableTarget]::Machine)

# Verificar
[Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
[Environment]::GetEnvironmentVariable("PYTHONPATH", [EnvironmentVariableTarget]::Machine)
```

### 8.2 Variáveis Específicas do Projeto (via .env)

Essas variáveis serão configuradas no arquivo `.env` posteriormente. Por enquanto, apenas documentar:

```ini
# Será criado em C:\projetos\crawler_tjsp\.env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=senha_segura

CHROME_BINARY_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe

CERT_PATH=C:\certs\certificado.pfx
CERT_PASSWORD=senha_do_certificado
```

**Checklist:**
- [ ] PATH do sistema atualizado com Python
- [ ] PYTHONPATH configurado (opcional)

---

## 9️⃣ Criar Script de Ativação Rápida

Facilita ativar o venv no futuro.

### 9.1 Criar activate.ps1

```powershell
# Criar script de ativação
@'
# Script de ativação rápida do ambiente Python
Write-Host "🐍 Ativando ambiente Python do Crawler TJSP..." -ForegroundColor Cyan

# Navegar para pasta do projeto
cd C:\projetos\crawler_tjsp

# Ativar venv
.\venv\Scripts\Activate.ps1

# Mostrar informações
Write-Host "✅ Ambiente ativado!" -ForegroundColor Green
Write-Host "Python: $(python --version)" -ForegroundColor Yellow
Write-Host "Localização: $(where python)" -ForegroundColor Yellow
Write-Host "Pacotes instalados: $(pip list --format=freeze | Measure-Object -Line | Select-Object -ExpandProperty Lines)" -ForegroundColor Yellow
'@ | Out-File -FilePath "C:\projetos\crawler_tjsp\activate.ps1" -Encoding utf8

Write-Host "✅ Script de ativação criado: C:\projetos\crawler_tjsp\activate.ps1" -ForegroundColor Green
```

### 9.2 Testar Script

```powershell
# Desativar venv atual (se estiver ativo)
deactivate

# Testar script
& C:\projetos\crawler_tjsp\activate.ps1

# Verificar
python --version
```

**Checklist:**
- [ ] Script `activate.ps1` criado
- [ ] Script funciona ao ser executado

---

## 🔟 Limpeza de Arquivos Temporários

```powershell
# Remover instaladores
Remove-Item -Path "C:\temp\installers" -Recurse -Force

# Limpar cache do pip
pip cache purge

Write-Host "✅ Limpeza concluída!" -ForegroundColor Green
```

---

## ✅ Checklist Final da Fase 2

- [ ] Python 3.12.3 instalado em `C:\Program Files\Python312\`
- [ ] `python --version` funciona no PATH
- [ ] pip atualizado e funcional
- [ ] Git instalado e configurado
- [ ] Visual C++ Build Tools instalado
- [ ] Virtual environment criado em `C:\projetos\crawler_tjsp\venv`
- [ ] Dependências básicas instaladas (selenium, psycopg2-binary, requests)
- [ ] Imports de pacotes funcionando
- [ ] Script de ativação rápida criado
- [ ] Limpeza de temporários concluída

---

## 🚀 Próximos Passos

Após concluir esta fase, prosseguir para:

**[03_chrome_websigner.md](03_chrome_websigner.md)** - Instalação do Chrome, ChromeDriver e Web Signer

---

## 📞 Troubleshooting

### Problema: Python não está no PATH

**Solução:**
```powershell
# Adicionar manualmente
$pythonPath = "C:\Program Files\Python312"
$env:Path += ";$pythonPath;$pythonPath\Scripts"

# Tornar permanente
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)

# Fechar e reabrir PowerShell
```

### Problema: pip install falha com erro de compilação

**Soluções:**
```powershell
# 1. Usar versão binary do pacote
pip install psycopg2-binary  # ao invés de psycopg2

# 2. Reinstalar Visual C++ Build Tools
choco install visualstudio2022buildtools -y --force

# 3. Verificar logs de erro
pip install psycopg2 --verbose
```

### Problema: Activate.ps1 não funciona (ExecutionPolicy)

**Solução:**
```powershell
# Liberar execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Ou executar com bypass
PowerShell -ExecutionPolicy Bypass -File C:\projetos\crawler_tjsp\venv\Scripts\Activate.ps1
```

### Problema: Git não está no PATH

**Solução:**
```powershell
# Adicionar manualmente
$gitPath = "C:\Program Files\Git\cmd"
$env:Path += ";$gitPath"

# Tornar permanente
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)
```

### Problema: virtualenv não cria ambiente

**Solução:**
```powershell
# Tentar com módulo venv do Python
python -m venv venv

# Se ainda falhar, reinstalar Python
```

---

**Última atualização:** 2025-10-04
**Tempo médio de execução:** 30-40 minutos
**Próxima fase:** Instalação de Chrome + Web Signer
