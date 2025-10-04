# 🌐 Instalação Chrome, ChromeDriver e Web Signer

**Fase 3 do Deployment Plan**
**Tempo estimado:** 45-60 minutos

---

## 📋 Pré-requisitos

- [ ] Fases 1 e 2 concluídas
- [ ] PowerShell como Administrator
- [ ] Certificado digital A1 (.pfx) disponível

---

## 1️⃣ Instalação do Google Chrome

### 1.1 Download e Instalação

```powershell
# Download Chrome Enterprise (versão standalone)
$chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$installerPath = "C:\temp\chrome-installer.msi"

New-Item -ItemType Directory -Path "C:\temp" -Force
Invoke-WebRequest -Uri $chromeUrl -OutFile $installerPath

# Instalar silenciosamente
Start-Process -FilePath "msiexec.exe" -Args "/i $installerPath /quiet /norestart" -Wait

# Verificar instalação
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    $chromeVersion = (Get-Item $chromePath).VersionInfo.FileVersion
    Write-Host "✅ Chrome instalado: versão $chromeVersion" -ForegroundColor Green
}
```

### 1.2 Verificar Versão do Chrome

```powershell
# Obter versão exata
$chromeVersion = (Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
Write-Host "Chrome versão: $chromeVersion"

# Anotar major version (exemplo: 122 de 122.0.6261.94)
$chromeMajorVersion = $chromeVersion.Split('.')[0]
Write-Host "Chrome major version: $chromeMajorVersion"
```

**Checklist:**
- [ ] Chrome instalado em `C:\Program Files\Google\Chrome\Application\chrome.exe`
- [ ] Versão anotada (necessário para ChromeDriver compatível)

---

## 2️⃣ Instalação do ChromeDriver

### 2.1 Determinar Versão Compatível

```powershell
# Versões recentes do Chrome (115+) usam ChromeDriver for Testing
# URL: https://googlechromelabs.github.io/chrome-for-testing/

# Para Chrome 122, por exemplo:
$chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/win64/chromedriver-win64.zip"

# Se Chrome for versão diferente, ajustar URL conforme:
# https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
```

### 2.2 Download e Instalação

```powershell
# Criar pasta para ChromeDriver
New-Item -ItemType Directory -Path "C:\chromedriver" -Force

# Download (AJUSTAR URL conforme versão do Chrome)
$chromedriverUrl = "https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/win64/chromedriver-win64.zip"
$zipPath = "C:\temp\chromedriver.zip"

Invoke-WebRequest -Uri $chromedriverUrl -OutFile $zipPath

# Extrair
Expand-Archive -Path $zipPath -DestinationPath "C:\temp\chromedriver-temp" -Force

# Mover executável para C:\chromedriver
Move-Item -Path "C:\temp\chromedriver-temp\chromedriver-win64\chromedriver.exe" -Destination "C:\chromedriver\chromedriver.exe" -Force

# Adicionar ao PATH
$env:Path += ";C:\chromedriver"
[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\chromedriver", [EnvironmentVariableTarget]::Machine)

# Verificar
chromedriver --version
```

**Checklist:**
- [ ] ChromeDriver em `C:\chromedriver\chromedriver.exe`
- [ ] `chromedriver --version` funciona
- [ ] Versão compatível com Chrome instalado

---

## 3️⃣ Instalação do Web Signer (Softplan)

### 3.1 Download do Web Signer

**Acessar site oficial:**
- URL: https://websigner.softplan.com.br/downloads

**Download manual via navegador no servidor:**
1. Abrir Chrome no servidor
2. Acessar https://websigner.softplan.com.br/downloads
3. Baixar versão Windows (websigner-X.X.X-win64.exe)
4. Salvar em `C:\temp\websigner-installer.exe`

**Ou via PowerShell (se URL direta disponível):**
```powershell
# Exemplo (URL pode mudar):
$webSignerUrl = "https://websigner.softplan.com.br/downloads/websigner-2.12.1-win64.exe"
$installerPath = "C:\temp\websigner-installer.exe"

Invoke-WebRequest -Uri $webSignerUrl -OutFile $installerPath
```

### 3.2 Instalação do Web Signer

```powershell
# Instalar (pode abrir wizard - seguir instruções)
Start-Process -FilePath "C:\temp\websigner-installer.exe" -Wait

# Caminho padrão de instalação
$webSignerPath = "C:\Program Files\Softplan\WebSigner\websigner.exe"

# Verificar instalação
if (Test-Path $webSignerPath) {
    Write-Host "✅ Web Signer instalado!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Web Signer não encontrado. Verificar instalação manual." -ForegroundColor Yellow
}
```

### 3.3 Iniciar Web Signer

```powershell
# Iniciar Web Signer (ficará rodando na bandeja do sistema)
Start-Process -FilePath "C:\Program Files\Softplan\WebSigner\websigner.exe"

# Aguardar alguns segundos
Start-Sleep -Seconds 5

# Verificar processo
Get-Process | Where-Object {$_.Name -like "*websigner*"}

# Deve aparecer ícone na bandeja do sistema (system tray)
```

**Checklist:**
- [ ] Web Signer instalado em `C:\Program Files\Softplan\WebSigner\`
- [ ] Web Signer rodando (ícone na bandeja)
- [ ] Processo `websigner.exe` aparece no Task Manager

---

## 4️⃣ Importar Certificado Digital A1

### 4.1 Transferir Certificado para Servidor

**Opção A: Via RDP (arrastar e soltar)**
1. Conectar via RDP ao servidor
2. Arrastar arquivo `.pfx` do computador local para desktop do servidor
3. Mover para `C:\certs\certificado.pfx`

**Opção B: Via SCP (se SSH configurado)**
```bash
# Do computador local
scp /caminho/local/certificado.pfx Administrator@<IP_SERVIDOR>:C:/certs/
```

**Opção C: Via navegador (upload para cloud)**
1. Fazer upload para Google Drive / Dropbox
2. Baixar no servidor via navegador
3. Mover para `C:\certs\`

```powershell
# Criar pasta certs se não existir
New-Item -ItemType Directory -Path "C:\certs" -Force

# Verificar certificado
if (Test-Path "C:\certs\certificado.pfx") {
    Write-Host "✅ Certificado presente em C:\certs\" -ForegroundColor Green
    Get-Item "C:\certs\certificado.pfx" | Select-Object Name, Length
} else {
    Write-Host "❌ Certificado não encontrado!" -ForegroundColor Red
}
```

### 4.2 Importar Certificado no Windows Certificate Store

**Opção A: Via PowerShell**

```powershell
# Importar certificado
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "SENHA_DO_CERTIFICADO" -Force -AsPlainText

# Importar para Personal store do usuário atual
Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar importação
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*CPF*"} | Select-Object Subject, Thumbprint, NotAfter

Write-Host "✅ Certificado importado!" -ForegroundColor Green
```

**Opção B: Via Interface Gráfica**

1. Duplo-clique em `C:\certs\certificado.pfx`
2. Wizard de importação:
   - Store Location: **Current User**
   - File: (já preenchido)
   - Password: **inserir senha do certificado**
   - Certificate Store: **Personal**
3. Finish

### 4.3 Verificar Certificado no Certificate Manager

```powershell
# Abrir Certificate Manager
certmgr.msc
```

**Navegação:**
1. Expandir "Personal"
2. Clicar em "Certificates"
3. Verificar se certificado com CPF aparece na lista

**Checklist:**
- [ ] Certificado em `C:\certs\certificado.pfx`
- [ ] Certificado importado no Windows Certificate Store
- [ ] Certificado visível em `certmgr.msc` → Personal → Certificates
- [ ] Certificado tem chave privada (ícone de chave na lista)

---

## 5️⃣ Configurar Web Signer com Certificado

### 5.1 Associar Certificado ao Web Signer

1. Clicar no ícone do Web Signer na bandeja (system tray)
2. Abrir configurações
3. Verificar se certificado aparece na lista
4. Selecionar certificado

**Se certificado não aparecer:**
- Reiniciar Web Signer
- Reimportar certificado
- Verificar logs: `C:\Program Files\Softplan\WebSigner\logs\`

### 5.2 Testar Web Signer Manual

```powershell
# Abrir Chrome manualmente
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "https://esaj.tjsp.jus.br/esaj/portal.do"

# No navegador:
# 1. Clicar em "Certificado Digital"
# 2. Web Signer deve abrir modal de seleção
# 3. Selecionar certificado
# 4. Login deve ser bem-sucedido
```

**Checklist:**
- [ ] Web Signer reconhece certificado
- [ ] Modal de seleção abre ao clicar "Certificado Digital"
- [ ] Login manual com certificado funciona

---

## 6️⃣ Instalar Extensão Chrome do Web Signer

### 6.1 Verificar Extensão na Chrome Web Store

**Método Recomendado: Chrome Web Store**

1. Abrir Chrome
2. Acessar Chrome Web Store
3. Procurar "Web Signer Softplan"
4. Clicar "Adicionar ao Chrome"

**URL:** `https://chrome.google.com/webstore` (procurar "Web Signer")

### 6.2 Carregar Extensão Local (Desenvolvimento)

Se necessário usar extensão customizada do repositório:

```powershell
# A extensão estará em: C:\projetos\crawler_tjsp\chrome_extension

# Abrir Chrome
Start-Process "chrome.exe" -ArgumentList "--load-extension=C:\projetos\crawler_tjsp\chrome_extension"

# Ou manualmente:
# 1. chrome://extensions/
# 2. Habilitar "Modo do desenvolvedor"
# 3. Clicar "Carregar sem compactação"
# 4. Selecionar: C:\projetos\crawler_tjsp\chrome_extension
```

### 6.3 Verificar Extensão

```powershell
# Abrir Chrome em página de extensões
Start-Process "chrome.exe" -ArgumentList "chrome://extensions/"

# Verificar visualmente:
# - Extensão "Web Signer" aparece
# - Extensão está habilitada (toggle azul)
```

**Checklist:**
- [ ] Extensão Web Signer instalada
- [ ] Extensão habilitada em `chrome://extensions/`
- [ ] Ícone da extensão aparece na toolbar do Chrome

---

## 7️⃣ Testar Integração Completa

### 7.1 Teste Manual com Chrome

```powershell
# Abrir e-SAJ
Start-Process "chrome.exe" -ArgumentList "https://esaj.tjsp.jus.br/esaj/portal.do"
```

**Passos:**
1. Chrome abre e-SAJ
2. Clicar em "Certificado Digital"
3. Web Signer abre modal de seleção
4. Selecionar certificado
5. Login bem-sucedido → redireciona para portal autenticado

**Screenshot de sucesso:**
- URL após login: `https://esaj.tjsp.jus.br/esaj/portal.do?servico=...`

### 7.2 Teste com Selenium (Script Python)

Criar `test_chrome_selenium.py`:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Extensão (se usar local)
# chrome_options.add_argument("--load-extension=C:\\projetos\\crawler_tjsp\\chrome_extension")

# ChromeDriver
service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")

# Iniciar
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("🔵 Abrindo e-SAJ...")
    driver.get("https://esaj.tjsp.jus.br/esaj/portal.do")
    time.sleep(3)

    print("✅ e-SAJ carregou!")
    print(f"Título: {driver.title}")

    # Screenshot
    driver.save_screenshot(r"C:\projetos\crawler_tjsp\test_esaj.png")
    print("📸 Screenshot salvo: test_esaj.png")

    input("Pressione Enter para fechar...")

finally:
    driver.quit()
```

**Executar:**
```powershell
cd C:\projetos\crawler_tjsp
.\venv\Scripts\Activate.ps1
python test_chrome_selenium.py
```

**Checklist:**
- [ ] Chrome abre via Selenium
- [ ] e-SAJ carrega
- [ ] Screenshot salvo
- [ ] Sem erros no console

---

## ✅ Checklist Final da Fase 3

- [ ] Google Chrome instalado
- [ ] ChromeDriver instalado e no PATH
- [ ] Versões Chrome e ChromeDriver compatíveis
- [ ] Web Signer instalado e rodando
- [ ] Certificado A1 transferido para `C:\certs\`
- [ ] Certificado importado no Windows Certificate Store
- [ ] Web Signer reconhece certificado
- [ ] Extensão Chrome instalada e habilitada
- [ ] Teste manual de login com certificado bem-sucedido
- [ ] Teste Selenium básico funcionando

---

## 🚀 Próximos Passos

**[04_postgresql.md](04_postgresql.md)** - Instalação e configuração do PostgreSQL

---

## 📞 Troubleshooting

### Problema: ChromeDriver incompatível com Chrome

```powershell
# Verificar versões
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
chromedriver --version

# Baixar ChromeDriver compatível:
# https://googlechromelabs.github.io/chrome-for-testing/
```

### Problema: Web Signer não detecta certificado

**Soluções:**
1. Reimportar certificado no Certificate Store (Current User → Personal)
2. Verificar senha do certificado está correta
3. Reiniciar Web Signer
4. Verificar logs: `C:\Program Files\Softplan\WebSigner\logs\`

### Problema: Extensão não carrega no Chrome via Selenium

**Soluções:**
```python
# Especificar user-data-dir persistente
chrome_options.add_argument("--user-data-dir=C:\\temp\\chrome-profile")

# Ou carregar extensão explicitamente
chrome_options.add_argument("--load-extension=C:\\caminho\\extensao")
```

---

**Última atualização:** 2025-10-04
**Próxima fase:** PostgreSQL
