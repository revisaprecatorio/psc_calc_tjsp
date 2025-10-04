# 🚀 Plano de Deployment - Windows Server

**Objetivo:** Migrar crawler TJSP de Linux para Windows Server para resolver bloqueio do Native Messaging Protocol

**Tempo Total Estimado:** 8-12 horas
**Complexidade:** Moderada
**Prioridade:** Alta

---

## 📋 Pré-requisitos

### Antes de Começar

- [ ] Credenciais de acesso recebidas da Contabo (IP, usuário, senha)
- [ ] Certificado digital A1 (.pfx) disponível
- [ ] Senha do certificado A1 documentada
- [ ] Cliente RDP instalado (Windows Remote Desktop / Microsoft Remote Desktop)
- [ ] Cliente SSH (PuTTY / Windows Terminal)
- [ ] Backup do código atual do repositório GitHub

### Informações Necessárias

```bash
# Servidor
SERVIDOR_IP=<IP fornecido pela Contabo>
SERVIDOR_USER=Administrator
SERVIDOR_SENHA=<senha fornecida>

# PostgreSQL (pode ser remoto ou local)
POSTGRES_HOST=<IP ou localhost>
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=<senha segura>

# Certificado Digital
CERT_PATH=C:\certs\certificado.pfx
CERT_PASSWORD=<senha do certificado>
```

---

## 🎯 Fase 1: Acesso Inicial ao Servidor

### 1.1 Primeiro Acesso via RDP

**Tempo estimado:** 15 minutos

```powershell
# No seu computador local (Windows)
# Abrir "Remote Desktop Connection" (mstsc.exe)
# Inserir:
#   Computer: <SERVIDOR_IP>
#   Username: Administrator
#   Password: <SERVIDOR_SENHA>
```

**Validações:**
- [ ] Desktop do Windows Server carregou
- [ ] Consegue abrir PowerShell como Administrator
- [ ] Internet funcionando (testar: `ping google.com`)

### 1.2 Configurar OpenSSH Server (Opcional)

**Tempo estimado:** 10 minutos

```powershell
# No PowerShell do servidor (como Administrator)

# Instalar OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Iniciar serviço SSH
Start-Service sshd

# Configurar para iniciar automaticamente
Set-Service -Name sshd -StartupType 'Automatic'

# Configurar firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Testar do seu computador local
# ssh Administrator@<SERVIDOR_IP>
```

**Validações:**
- [ ] SSH conecta via PuTTY ou terminal
- [ ] Pode executar comandos via SSH
- [ ] Firewall permite porta 22

### 1.3 Configurar Windows Firewall

**Tempo estimado:** 10 minutos

```powershell
# Permitir RDP (porta 3389) - geralmente já habilitado
New-NetFirewallRule -DisplayName "RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow

# Permitir PostgreSQL (porta 5432) se for usar banco local
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow

# Verificar regras
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*RDP*" -or $_.DisplayName -like "*SSH*" -or $_.DisplayName -like "*PostgreSQL*"}
```

**Validações:**
- [ ] RDP acessível externamente
- [ ] SSH acessível (se configurado)
- [ ] PostgreSQL acessível (se necessário)

### 1.4 Criar Snapshot Inicial

**Tempo estimado:** 5 minutos

**No painel da Contabo:**
1. Acessar painel de VPS
2. Localizar "Cloud VPS 10"
3. Criar snapshot com nome: `initial-clean-windows-2025-10-04`

**Validações:**
- [ ] Snapshot criado com sucesso
- [ ] Data e hora corretas

---

## 🔧 Fase 2: Instalação de Software Base

### 2.1 Instalar Python 3.12

**Tempo estimado:** 15 minutos

```powershell
# Download Python 3.12.x (usar navegador ou Invoke-WebRequest)
$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath

# Instalar silenciosamente
Start-Process -FilePath $installerPath -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

# Verificar instalação
python --version
pip --version
```

**Validações:**
- [ ] `python --version` retorna 3.12.x
- [ ] `pip --version` funciona
- [ ] Python está no PATH (`where python`)

**Script automatizado:** [scripts/install_python.ps1](scripts/install_python.ps1)

### 2.2 Instalar Git para Windows

**Tempo estimado:** 10 minutos

```powershell
# Download Git
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$installerPath = "$env:TEMP\git-installer.exe"

Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath

# Instalar silenciosamente
Start-Process -FilePath $installerPath -Args "/VERYSILENT /NORESTART" -Wait

# Verificar
git --version
```

**Validações:**
- [ ] `git --version` funciona
- [ ] Git está no PATH

### 2.3 Instalar Google Chrome

**Tempo estimado:** 10 minutos

```powershell
# Download Chrome
$chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$installerPath = "$env:TEMP\chrome-installer.msi"

Invoke-WebRequest -Uri $chromeUrl -OutFile $installerPath

# Instalar silenciosamente
Start-Process -FilePath "msiexec.exe" -Args "/i $installerPath /quiet /norestart" -Wait

# Verificar instalação
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    Write-Host "Chrome instalado com sucesso: $chromePath"
}
```

**Validações:**
- [ ] Chrome está em `C:\Program Files\Google\Chrome\Application\chrome.exe`
- [ ] Chrome abre manualmente
- [ ] Versão do Chrome compatível com Selenium

**Script automatizado:** [scripts/install_chrome.ps1](scripts/install_chrome.ps1)

### 2.4 Instalar ChromeDriver

**Tempo estimado:** 10 minutos

```powershell
# Verificar versão do Chrome
$chromeVersion = (Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
Write-Host "Chrome versão: $chromeVersion"

# Download ChromeDriver compatível (exemplo para versão 122)
$chromedriverUrl = "https://chromedriver.storage.googleapis.com/122.0.6261.94/chromedriver_win32.zip"
$zipPath = "$env:TEMP\chromedriver.zip"
$extractPath = "C:\chromedriver"

Invoke-WebRequest -Uri $chromedriverUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Adicionar ao PATH
$env:Path += ";$extractPath"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)

# Verificar
chromedriver --version
```

**Validações:**
- [ ] `chromedriver --version` funciona
- [ ] Versão compatível com Chrome instalado

### 2.5 Instalar PostgreSQL 15

**Tempo estimado:** 20 minutos

**Opção A: PostgreSQL Local (recomendado para testes)**

```powershell
# Download PostgreSQL 15
$pgUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.6-1-windows-x64.exe"
$installerPath = "$env:TEMP\postgresql-installer.exe"

Invoke-WebRequest -Uri $pgUrl -OutFile $installerPath

# Instalar (abrirá wizard - configurar senha do postgres)
Start-Process -FilePath $installerPath -Wait

# Após instalação, criar database e usuário
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE revisa_db;"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER revisa_user WITH PASSWORD 'senha_segura';"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE revisa_db TO revisa_user;"
```

**Opção B: PostgreSQL Remoto (produção)**

Se já existe banco PostgreSQL em outra máquina, apenas configurar .env para apontar para ele.

**Validações:**
- [ ] PostgreSQL rodando (`Get-Service postgresql-x64-15`)
- [ ] Porta 5432 listening (`netstat -an | findstr 5432`)
- [ ] Conexão funciona: `psql -U revisa_user -d revisa_db -h localhost`

**Script automatizado:** [scripts/install_postgresql.ps1](scripts/install_postgresql.ps1)

---

## 📦 Fase 3: Instalação do Web Signer

### 3.1 Download e Instalação

**Tempo estimado:** 15 minutos

```powershell
# Criar pasta para downloads
New-Item -ItemType Directory -Path "C:\softplan" -Force

# Download Web Signer (versão Windows)
# URL oficial: https://websigner.softplan.com.br/downloads
# Baixar manualmente via navegador ou usar link direto se disponível

# Exemplo (URL pode mudar):
$webSignerUrl = "https://websigner.softplan.com.br/downloads/websigner-2.12.1-win64.exe"
$installerPath = "C:\softplan\websigner-installer.exe"

Invoke-WebRequest -Uri $webSignerUrl -OutFile $installerPath

# Instalar
Start-Process -FilePath $installerPath -Wait

# Verificar instalação
$webSignerPath = "C:\Program Files\Softplan\WebSigner\websigner.exe"
if (Test-Path $webSignerPath) {
    Write-Host "Web Signer instalado: $webSignerPath"
}
```

**Validações:**
- [ ] Web Signer instalado em `C:\Program Files\Softplan\WebSigner\`
- [ ] Executável `websigner.exe` existe
- [ ] Serviço do Web Signer iniciado (verificar Task Manager)

### 3.2 Importar Certificado Digital A1

**Tempo estimado:** 10 minutos

**Transferir certificado via RDP:**
1. Copiar arquivo `.pfx` do computador local para o servidor
2. Salvar em `C:\certs\certificado.pfx`

**Ou via SCP (se SSH configurado):**
```bash
# Do seu computador local
scp /caminho/local/certificado.pfx Administrator@<SERVIDOR_IP>:C:\certs\
```

**Importar no Windows Certificate Store:**

```powershell
# Via PowerShell
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "SENHA_DO_CERTIFICADO" -Force -AsPlainText

Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar certificado importado
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*CPF*"}
```

**Ou via interface gráfica:**
1. Duplo-clique no arquivo `.pfx`
2. Seguir wizard de importação
3. Inserir senha do certificado
4. Selecionar "Current User" → "Personal" store

**Validações:**
- [ ] Certificado aparece em `certmgr.msc` (Certificate Manager)
- [ ] Certificado tem chave privada associada
- [ ] Web Signer consegue listar o certificado

### 3.3 Instalar Extensão Chrome do Web Signer

**Tempo estimado:** 10 minutos

**Método 1: Via Chrome Web Store (Recomendado)**
1. Abrir Chrome
2. Acessar: https://chrome.google.com/webstore/detail/web-signer/[ID_DA_EXTENSAO]
3. Clicar "Adicionar ao Chrome"

**Método 2: Carregar extensão local (desenvolvimento)**
```powershell
# Copiar extensão do repositório
$extensionPath = "C:\crawler_tjsp\chrome_extension"

# Abrir Chrome e carregar extensão:
# 1. chrome://extensions/
# 2. Habilitar "Modo do desenvolvedor"
# 3. Clicar "Carregar sem compactação"
# 4. Selecionar pasta: C:\crawler_tjsp\chrome_extension
```

**Validações:**
- [ ] Extensão aparece em `chrome://extensions/`
- [ ] Extensão está habilitada
- [ ] Web Signer detecta a extensão (ícone verde na bandeja)

---

## 🐍 Fase 4: Deploy do Código do Crawler

### 4.1 Clonar Repositório

**Tempo estimado:** 5 minutos

```powershell
# Criar pasta de projetos
New-Item -ItemType Directory -Path "C:\projetos" -Force
cd C:\projetos

# Clonar repositório
git clone https://github.com/revisaprecatorio/crawler_tjsp.git
cd crawler_tjsp

# Verificar branch
git branch
git status
```

**Validações:**
- [ ] Repositório clonado em `C:\projetos\crawler_tjsp`
- [ ] Branch `main` ativa
- [ ] Todos os arquivos presentes

### 4.2 Criar Virtual Environment

**Tempo estimado:** 5 minutos

```powershell
# Criar venv
python -m venv venv

# Ativar venv
.\venv\Scripts\Activate.ps1

# Verificar
python --version
pip --version
```

**Se erro de ExecutionPolicy:**
```powershell
# Liberar execução de scripts (como Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Validações:**
- [ ] Venv criado em `C:\projetos\crawler_tjsp\venv`
- [ ] Prompt mostra `(venv)`
- [ ] `which python` aponta para venv

### 4.3 Instalar Dependências

**Tempo estimado:** 10 minutos

```powershell
# Ainda com venv ativado
pip install --upgrade pip
pip install -r requirements.txt

# Verificar pacotes críticos
pip show selenium
pip show psycopg2
pip show requests
```

**Possíveis problemas:**
- `psycopg2` pode precisar do Microsoft C++ Build Tools
  - Solução: `pip install psycopg2-binary` (versão standalone)

**Validações:**
- [ ] Todos os pacotes instalados sem erros
- [ ] `pip list` mostra selenium, psycopg2, requests, etc.

**Script automatizado:** [scripts/install_dependencies.ps1](scripts/install_dependencies.ps1)

### 4.4 Configurar .env

**Tempo estimado:** 5 minutos

```powershell
# Copiar template
Copy-Item .env.example .env

# Editar .env (usar notepad ou VS Code)
notepad .env
```

**Conteúdo do .env (exemplo):**
```ini
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=senha_segura

# Crawler
SELENIUM_REMOTE_URL=
CHROME_BINARY_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe

# Certificado
CERT_PATH=C:\certs\certificado.pfx
CERT_PASSWORD=senha_do_certificado

# Web Signer
WEBSIGNER_PATH=C:\Program Files\Softplan\WebSigner\websigner.exe

# Logs
LOG_LEVEL=INFO
LOG_PATH=C:\projetos\crawler_tjsp\logs
```

**Validações:**
- [ ] `.env` existe e está preenchido
- [ ] Todos os caminhos (paths) estão corretos
- [ ] Credenciais do PostgreSQL corretas

### 4.5 Adaptar Código para Windows

**Tempo estimado:** 20 minutos

**Principais mudanças necessárias:**

1. **Paths (barras invertidas)**
   ```python
   # Antes (Linux)
   cert_path = "/root/certs/certificado.pfx"

   # Depois (Windows)
   cert_path = r"C:\certs\certificado.pfx"
   # ou
   cert_path = "C:\\certs\\certificado.pfx"
   # ou (melhor - multiplataforma)
   import os
   cert_path = os.path.join("C:", "certs", "certificado.pfx")
   ```

2. **User Data Directory do Chrome**
   ```python
   # Antes
   user_data_dir = "/tmp/chrome-profile"

   # Depois
   user_data_dir = r"C:\temp\chrome-profile"
   ```

3. **ChromeDriver Path**
   ```python
   # Explicitamente especificar caminho no Windows
   from selenium import webdriver
   from selenium.webdriver.chrome.service import Service

   service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")
   driver = webdriver.Chrome(service=service, options=chrome_options)
   ```

4. **Subprocess (se usado)**
   ```python
   # Antes
   subprocess.run(["bash", "script.sh"])

   # Depois
   subprocess.run(["powershell", "-File", "script.ps1"])
   ```

**Arquivos que precisam ser revisados:**
- `crawler_full.py` (principalmente função `_build_chrome()`)
- `orchestrator_subprocess.py`
- `websocket_cert_server.py`

**Validações:**
- [ ] Código adaptado para Windows paths
- [ ] Imports funcionam sem erros
- [ ] `python crawler_full.py --help` funciona

---

## 🧪 Fase 5: Testes de Validação

### 5.1 Teste Manual do Chrome + Selenium

**Tempo estimado:** 15 minutos

**Criar script de teste:** `test_chrome_windows.py`

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# ChromeDriver
service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")

# Iniciar Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Testar navegação
    driver.get("https://www.google.com")
    print("✅ Chrome abriu Google com sucesso!")

    # Screenshot
    driver.save_screenshot(r"C:\projetos\crawler_tjsp\test_screenshot.png")
    print("✅ Screenshot salvo!")

    time.sleep(3)

finally:
    driver.quit()
    print("✅ Chrome fechado!")
```

**Executar:**
```powershell
python test_chrome_windows.py
```

**Validações:**
- [ ] Chrome abre via Selenium
- [ ] Google carrega corretamente
- [ ] Screenshot salvo em `C:\projetos\crawler_tjsp\test_screenshot.png`
- [ ] Chrome fecha sem erros

### 5.2 Teste de Extensão Web Signer

**Tempo estimado:** 15 minutos

**Criar script:** `test_websigner_extension.py`

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# Configurar Chrome com extensão
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Carregar extensão
extension_path = r"C:\projetos\crawler_tjsp\chrome_extension"
chrome_options.add_argument(f"--load-extension={extension_path}")

# ChromeDriver
service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")

# Iniciar Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Ir para página de teste do Web Signer
    driver.get("chrome://extensions/")
    time.sleep(2)

    # Verificar se extensão carregou
    print("✅ Verificar visualmente se a extensão 'Web Signer' aparece na lista")

    # Ir para e-SAJ
    driver.get("https://esaj.tjsp.jus.br/esaj/portal.do")
    time.sleep(5)

    print("✅ Verificar se Web Signer está ativo (ícone verde na bandeja)")

    input("Pressione Enter para fechar...")

finally:
    driver.quit()
```

**Executar:**
```powershell
python test_websigner_extension.py
```

**Validações:**
- [ ] Extensão carrega em `chrome://extensions/`
- [ ] Web Signer mostra ícone verde (ativo)
- [ ] e-SAJ abre corretamente

### 5.3 Teste de Autenticação com Certificado

**Tempo estimado:** 20 minutos

**Criar script:** `test_esaj_auth.py`

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Carregar extensão
extension_path = r"C:\projetos\crawler_tjsp\chrome_extension"
chrome_options.add_argument(f"--load-extension={extension_path}")

# User data dir (perfil persistente)
user_data_dir = r"C:\temp\chrome-profile-test"
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

# ChromeDriver
service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")

# Iniciar Chrome
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("🔵 Abrindo e-SAJ...")
    driver.get("https://esaj.tjsp.jus.br/esaj/portal.do")
    time.sleep(3)

    print("🔵 Clicando em 'Certificado Digital'...")
    cert_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
    )
    cert_button.click()
    time.sleep(3)

    print("✅ Native Messaging deve acionar Web Signer agora!")
    print("⏳ Aguardando seleção de certificado...")

    # Aguardar modal do Web Signer (janela nativa)
    time.sleep(10)

    # Se login bem-sucedido, verificar URL
    if "portal.do?servico=" in driver.current_url:
        print("✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO!")

        # Screenshot de sucesso
        driver.save_screenshot(r"C:\projetos\crawler_tjsp\login_success.png")
        print("📸 Screenshot salvo: login_success.png")
    else:
        print("❌ Login falhou ou ainda na tela de autenticação")
        driver.save_screenshot(r"C:\projetos\crawler_tjsp\login_failed.png")

    input("Pressione Enter para fechar...")

except Exception as e:
    print(f"❌ Erro: {e}")
    driver.save_screenshot(r"C:\projetos\crawler_tjsp\error.png")

finally:
    driver.quit()
```

**Executar:**
```powershell
python test_esaj_auth.py
```

**Validações:**
- [ ] e-SAJ abre
- [ ] Botão "Certificado Digital" clicado
- [ ] Web Signer abre modal de seleção de certificado
- [ ] Login bem-sucedido após selecionar certificado
- [ ] Screenshot `login_success.png` salvo

**🎯 SE ESTE TESTE PASSAR = PROBLEMA RESOLVIDO!**

### 5.4 Teste do Crawler Completo

**Tempo estimado:** 15 minutos

```powershell
# Executar crawler em modo debug
python crawler_full.py --debug --processo=1234567-89.2020.8.26.0100
```

**Validações:**
- [ ] Crawler inicia sem erros
- [ ] Login com certificado funciona
- [ ] Processo é localizado
- [ ] Dados são extraídos
- [ ] JSON de saída gerado

---

## 🔄 Fase 6: Configuração do Worker (Orchestrator)

### 6.1 Testar Orchestrator Manualmente

**Tempo estimado:** 10 minutos

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Executar orchestrator em foreground (teste)
python orchestrator_subprocess.py
```

**O que deve acontecer:**
1. Conecta ao PostgreSQL
2. Consulta tabela `consultas_esaj`
3. Processa jobs pendentes
4. Chama `crawler_full.py` via subprocess
5. Atualiza status no banco

**Validações:**
- [ ] Conecta ao PostgreSQL
- [ ] Lê jobs da fila
- [ ] Executa crawler para cada job
- [ ] Atualiza status após conclusão
- [ ] Logs são gerados

### 6.2 Criar Windows Service (Auto-start)

**Tempo estimado:** 20 minutos

**Opção A: Usar NSSM (Non-Sucking Service Manager)**

```powershell
# Download NSSM
$nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$zipPath = "$env:TEMP\nssm.zip"
$extractPath = "C:\nssm"

Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Adicionar ao PATH
$env:Path += ";$extractPath\nssm-2.24\win64"

# Instalar serviço
nssm install CrawlerTJSP "C:\projetos\crawler_tjsp\venv\Scripts\python.exe" "C:\projetos\crawler_tjsp\orchestrator_subprocess.py"

# Configurar working directory
nssm set CrawlerTJSP AppDirectory "C:\projetos\crawler_tjsp"

# Configurar stdout/stderr
nssm set CrawlerTJSP AppStdout "C:\projetos\crawler_tjsp\logs\service_stdout.log"
nssm set CrawlerTJSP AppStderr "C:\projetos\crawler_tjsp\logs\service_stderr.log"

# Iniciar serviço
nssm start CrawlerTJSP

# Verificar status
nssm status CrawlerTJSP
```

**Opção B: Task Scheduler (mais simples)**

```powershell
# Criar tarefa agendada que executa no boot
$action = New-ScheduledTaskAction -Execute "C:\projetos\crawler_tjsp\venv\Scripts\python.exe" -Argument "C:\projetos\crawler_tjsp\orchestrator_subprocess.py" -WorkingDirectory "C:\projetos\crawler_tjsp"

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId "Administrator" -RunLevel Highest

Register-ScheduledTask -TaskName "CrawlerTJSP" -Action $action -Trigger $trigger -Principal $principal -Description "Crawler TJSP Orchestrator"

# Iniciar tarefa
Start-ScheduledTask -TaskName "CrawlerTJSP"

# Verificar
Get-ScheduledTask -TaskName "CrawlerTJSP"
```

**Validações:**
- [ ] Serviço/Tarefa aparece em Services ou Task Scheduler
- [ ] Serviço inicia automaticamente no boot
- [ ] Logs estão sendo gerados em `C:\projetos\crawler_tjsp\logs\`
- [ ] Jobs são processados continuamente

**Script automatizado:** [scripts/start_services.ps1](scripts/start_services.ps1)

---

## 📊 Fase 7: Monitoramento e Produção

### 7.1 Configurar Logs Rotativos

**Tempo estimado:** 15 minutos

**Editar código do orchestrator para usar logging:**

```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging
log_path = r"C:\projetos\crawler_tjsp\logs\orchestrator.log"
handler = RotatingFileHandler(
    log_path,
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usar logger
logger.info("Orchestrator iniciado")
logger.error("Erro ao processar job", exc_info=True)
```

**Validações:**
- [ ] Logs em `C:\projetos\crawler_tjsp\logs\orchestrator.log`
- [ ] Rotação funciona (cria `.1`, `.2`, etc após 10 MB)
- [ ] Nível de log configurável via .env

### 7.2 Configurar Alertas (Opcional)

**Tempo estimado:** 20 minutos

**Opção 1: Email via SMTP**

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'crawler@revisa.com'
    msg['To'] = 'admin@revisa.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user@gmail.com', 'senha_app')
        server.send_message(msg)

# Usar em caso de erro crítico
try:
    # processo de crawling
    pass
except Exception as e:
    send_alert("Erro no Crawler TJSP", str(e))
    raise
```

**Opção 2: Webhook (Slack, Discord, etc)**

```python
import requests

def send_webhook_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

# Usar
send_webhook_alert("⚠️ Crawler TJSP: 10 jobs falharam nas últimas 2 horas")
```

**Validações:**
- [ ] Alertas são enviados em caso de falha
- [ ] Não há spam (rate limiting)

### 7.3 Dashboard de Monitoramento (Opcional)

**Tempo estimado:** 30 minutos

**Opção 1: Grafana + PostgreSQL**
- Instalar Grafana no Windows Server
- Conectar ao PostgreSQL
- Criar dashboard com métricas:
  - Jobs processados por hora
  - Taxa de sucesso/erro
  - Tempo médio de processamento

**Opção 2: Script de Status**

```python
# status_crawler.py
import psycopg2
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost",
    database="revisa_db",
    user="revisa_user",
    password="senha"
)

cur = conn.cursor()

# Jobs nas últimas 24h
cur.execute("""
    SELECT status, COUNT(*)
    FROM consultas_esaj
    WHERE updated_at > NOW() - INTERVAL '24 hours'
    GROUP BY status
""")

print("📊 Status dos Jobs (últimas 24h):")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
```

**Executar periodicamente:**
```powershell
# Task Scheduler: executar a cada hora
python status_crawler.py
```

### 7.4 Backup e Disaster Recovery

**Tempo estimado:** 15 minutos

**Configurar backup automático no Contabo:**
1. Painel Contabo → Cloud VPS 10
2. Habilitar "Auto Backup" (já habilitado)
3. Frequência: Diária
4. Retenção: 7 dias

**Backup manual do código + banco:**

```powershell
# Script de backup: backup.ps1
$backupDir = "C:\backups\crawler_tjsp_$(Get-Date -Format 'yyyy-MM-dd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

# Backup do código
Copy-Item -Recurse "C:\projetos\crawler_tjsp" "$backupDir\codigo"

# Backup do banco PostgreSQL
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U revisa_user -d revisa_db -f "$backupDir\revisa_db.sql"

# Compactar
Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"

Write-Host "✅ Backup criado: $backupDir.zip"
```

**Agendar backup semanal:**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\projetos\crawler_tjsp\scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -TaskName "BackupCrawlerTJSP" -Action $action -Trigger $trigger
```

**Validações:**
- [ ] Auto-backup da Contabo ativo
- [ ] Script de backup manual funciona
- [ ] Backup agendado semanalmente
- [ ] Backups armazenados em local seguro

### 7.5 Documentar Procedimentos de Manutenção

**Tempo estimado:** 20 minutos

**Criar:** `windows-server/docs/maintenance.md`

**Conteúdo:**
```markdown
# Procedimentos de Manutenção - Crawler TJSP (Windows Server)

## Reiniciar Serviço
```powershell
Restart-Service CrawlerTJSP
# ou
Restart-ScheduledTask -TaskName "CrawlerTJSP"
```

## Verificar Logs
```powershell
Get-Content C:\projetos\crawler_tjsp\logs\orchestrator.log -Tail 50
```

## Atualizar Código
```powershell
cd C:\projetos\crawler_tjsp
git pull origin main
Restart-Service CrawlerTJSP
```

## Limpar Fila de Jobs
```powershell
psql -U revisa_user -d revisa_db -c "UPDATE consultas_esaj SET status='pending' WHERE status='processing';"
```

## Restaurar Backup
```powershell
# Parar serviço
Stop-Service CrawlerTJSP

# Restaurar banco
psql -U revisa_user -d revisa_db -f C:\backups\revisa_db.sql

# Reiniciar serviço
Start-Service CrawlerTJSP
```
```

---

## ✅ Checklist Final de Deployment

### Pré-Produção
- [ ] Todos os testes passaram (Fases 5.1 a 5.4)
- [ ] Autenticação com certificado funciona via Selenium
- [ ] Orchestrator processa jobs corretamente
- [ ] Logs estão sendo gerados
- [ ] Serviço configurado para auto-start
- [ ] Backup configurado
- [ ] Snapshot criado

### Produção
- [ ] Inserir jobs reais na fila (`consultas_esaj`)
- [ ] Monitorar processamento por 2-4 horas
- [ ] Validar dados extraídos
- [ ] Verificar taxa de sucesso > 95%
- [ ] Confirmar estabilidade do sistema

### Pós-Deployment
- [ ] Documentar lições aprendidas
- [ ] Atualizar DEPLOY_TRACKING.md com Deploy #31
- [ ] Atualizar DIAGNOSTIC_REPORT.md com solução final
- [ ] Comunicar sucesso para stakeholders

---

## 📈 Métricas de Sucesso

| Métrica | Meta | Como Medir |
|---------|------|------------|
| Taxa de Sucesso Login | > 98% | Logs do orchestrator |
| Tempo Médio por Job | < 2 min | Análise PostgreSQL |
| Uptime do Serviço | > 99% | Windows Event Viewer |
| Erros por Dia | < 5 | Logs de erro |
| Jobs Processados/Dia | > 100 | Query PostgreSQL |

---

## 🚨 Troubleshooting

### Problema: Serviço não inicia
**Solução:**
```powershell
# Verificar logs
Get-EventLog -LogName Application -Source CrawlerTJSP -Newest 10

# Testar manualmente
cd C:\projetos\crawler_tjsp
.\venv\Scripts\Activate.ps1
python orchestrator_subprocess.py
```

### Problema: Login com certificado falha
**Solução:**
1. Verificar certificado: `certmgr.msc`
2. Verificar Web Signer rodando: Task Manager
3. Testar manualmente: abrir Chrome, ir para e-SAJ, clicar "Certificado Digital"
4. Verificar logs do Web Signer: `C:\Program Files\Softplan\WebSigner\logs\`

### Problema: Alta taxa de erro
**Solução:**
```sql
-- Verificar erros recentes
SELECT processo_numero, error_message, updated_at
FROM consultas_esaj
WHERE status = 'failed'
ORDER BY updated_at DESC
LIMIT 20;

-- Resetar jobs falhados para retry
UPDATE consultas_esaj
SET status = 'pending', attempts = 0
WHERE status = 'failed' AND attempts < 3;
```

---

## 📞 Suporte

**Contato Contabo:** https://contabo.com/support
**Documentação Windows Server:** https://learn.microsoft.com/windows-server
**Documentação Selenium:** https://www.selenium.dev/documentation

---

**Última atualização:** 2025-10-04
**Status:** Pronto para execução
**Próximo passo:** Aguardar credenciais Contabo e iniciar Fase 1
