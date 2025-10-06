# 🔄 Guia de Restore - Recuperação do Sistema

**Data:** 2025-10-06  
**Versão:** 1.0  
**Objetivo:** Restaurar sistema após problema no upgrade ou necessidade de rollback  

---

## 📋 Quando Usar Este Guia

Use este guia se:

✅ Upgrade para Windows Server 2025 falhou  
✅ Sistema ficou instável após upgrade  
✅ Certificado/Web Signer parou de funcionar  
✅ Precisa voltar para estado anterior  
✅ Precisa restaurar em nova máquina  

---

## 🎯 Métodos de Restore (Escolha Um)

### **Método 1: Restore via Snapshot Contabo** ⭐ RECOMENDADO
- ✅ Mais rápido (10-20 minutos)
- ✅ Restaura TUDO exatamente como estava
- ✅ Zero configuração manual
- ✅ Sistema 100% funcional após restore
- ❌ Requer que snapshot exista

### **Método 2: Restore Manual via Backup ZIP**
- ✅ Funciona mesmo sem snapshot
- ✅ Pode restaurar em outra máquina
- ✅ Permite customização durante restore
- ❌ Mais demorado (2-4 horas)
- ❌ Requer instalação manual de software

---

## 🔵 MÉTODO 1: Restore via Snapshot Contabo

### Pré-requisitos:
- [ ] Snapshot `pre-upgrade-to-ws2025-2025-10-06` existe
- [ ] Acesso ao painel Contabo
- [ ] Servidor pode ficar offline por 10-20 minutos

### Passo a Passo:

#### 1. Acessar Painel Contabo
```
URL: https://my.contabo.com
Login: [suas credenciais]
```

#### 2. Navegar até Snapshots
```
1. Dashboard → Cloud VPS
2. Selecionar servidor: 62.171.143.88
3. Menu lateral → Snapshots
4. Localizar: pre-upgrade-to-ws2025-2025-10-06
```

#### 3. Iniciar Restore
```
1. Clicar em "Restore" no snapshot desejado
2. Confirmar: "Yes, restore this snapshot"
3. ⚠️ AVISO: Servidor será reiniciado!
4. Aguardar processo (10-20 minutos)
```

#### 4. Validar Restore
```powershell
# Conectar via RDP
# IP: 62.171.143.88
# User: Administrator
# Pass: 31032025

# Verificar versão do Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Deve mostrar: Windows Server 2016 (não 2025)

# Verificar Python
python --version
# Esperado: Python 3.12.3

# Verificar Chrome
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
(Get-Item $chromePath).VersionInfo.FileVersion
# Esperado: 131.0.6778.86

# Verificar certificado
Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
# Deve aparecer certificado válido

# Verificar código
Test-Path "C:\projetos\crawler_tjsp"
# Deve retornar: True

# Verificar .env
Test-Path "C:\projetos\crawler_tjsp\.env"
# Deve retornar: True
```

#### 5. Testar Funcionalidade
```powershell
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1
python windows-server\scripts\test_authentication.py
```

✅ **Se teste passar: Sistema 100% restaurado!**

---

## 🟢 MÉTODO 2: Restore Manual via Backup ZIP

### Cenários de Uso:
- Snapshot não disponível
- Restaurar em máquina diferente
- Upgrade para Windows Server 2025 + restore de dados

### Tempo Estimado: 2-4 horas

---

### FASE 1: Preparar Sistema Base

#### 1.1 Instalar Windows Server (2016 ou 2025)
```
- Instalar Windows Server limpo
- Configurar rede (IP estático ou DHCP)
- Configurar RDP
- Atualizar Windows Updates
- Reiniciar
```

#### 1.2 Configurar OpenSSH (opcional)
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

#### 1.3 Criar Estrutura de Diretórios
```powershell
New-Item -ItemType Directory -Path "C:\projetos" -Force
New-Item -ItemType Directory -Path "C:\certs" -Force
New-Item -ItemType Directory -Path "C:\temp" -Force
New-Item -ItemType Directory -Path "C:\backups" -Force
New-Item -ItemType Directory -Path "C:\chromedriver" -Force
```

---

### FASE 2: Transferir e Extrair Backup

#### 2.1 Transferir Arquivo ZIP
```bash
# Do computador local (Mac/Linux)
scp ~/Downloads/BACKUP_COMPLETO_PRE_UPGRADE_*.zip Administrator@62.171.143.88:C:/backups/

# Ou via RDP: arrastar e soltar
```

#### 2.2 Validar Hash MD5
```powershell
# No servidor
$zipFile = Get-ChildItem "C:\backups\BACKUP_COMPLETO_PRE_UPGRADE_*.zip" | Select-Object -First 1
$hash = Get-FileHash $zipFile -Algorithm MD5

Write-Host "MD5 calculado: $($hash.Hash)"
Write-Host "MD5 esperado: [copiar do arquivo .md5]"

# Devem ser IDÊNTICOS!
```

#### 2.3 Extrair Backup
```powershell
$zipFile = Get-ChildItem "C:\backups\BACKUP_COMPLETO_PRE_UPGRADE_*.zip" | Select-Object -First 1
$extractPath = "C:\backups\restore"

Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

Write-Host "✅ Backup extraído em: $extractPath"
```

---

### FASE 3: Instalar Software

#### 3.1 Instalar Python 3.12
```powershell
# Download Python 3.12.3
$pythonUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
Start-Process -FilePath $installerPath -Args "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

# Verificar
python --version
```

#### 3.2 Instalar Git
```powershell
# Habilitar TLS 1.2 primeiro (Windows Server 2016)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Download Git
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
$installerPath = "$env:TEMP\git-installer.exe"

Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath
Start-Process -FilePath $installerPath -Args "/VERYSILENT /NORESTART" -Wait

# Verificar
git --version
```

#### 3.3 Instalar Google Chrome
```powershell
# Versão específica: 131.0.6778.86
# ⚠️ IMPORTANTE: Instalar versão EXATA do backup

$chromeUrl = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
$installerPath = "$env:TEMP\chrome-installer.msi"

Invoke-WebRequest -Uri $chromeUrl -OutFile $installerPath
Start-Process -FilePath "msiexec.exe" -Args "/i $installerPath /quiet /norestart" -Wait

# Verificar versão
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
(Get-Item $chromePath).VersionInfo.FileVersion
```

#### 3.4 Instalar ChromeDriver
```powershell
# Baixar versão compatível com Chrome
# Consultar: https://chromedriver.chromium.org/downloads

# Exemplo para Chrome 131.x
$chromedriverUrl = "https://chromedriver.storage.googleapis.com/[versão]/chromedriver_win32.zip"
$zipPath = "$env:TEMP\chromedriver.zip"
$extractPath = "C:\chromedriver"

Invoke-WebRequest -Uri $chromedriverUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Adicionar ao PATH
$env:Path += ";C:\chromedriver"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)

# Verificar
chromedriver --version
```

#### 3.5 Instalar Web Signer
```powershell
# Download Web Signer
# URL: https://websigner.softplan.com.br/downloads

# Instalar manualmente (requer interface gráfica)
# Ou usar instalador silencioso se disponível

Write-Host "⚠️ Web Signer deve ser instalado manualmente"
Write-Host "  1. Baixar de: https://websigner.softplan.com.br/downloads"
Write-Host "  2. Executar instalador"
Write-Host "  3. Verificar serviço iniciado"
```

---

### FASE 4: Restaurar Certificado Digital

#### 4.1 Copiar Arquivo .pfx
```powershell
$backupCertPath = "C:\backups\restore\backup_*\03_certificados\certificado.pfx"
$destCertPath = "C:\certs\certificado.pfx"

Copy-Item $backupCertPath $destCertPath -Force

Write-Host "✅ Certificado copiado para: $destCertPath"
```

#### 4.2 Importar no Windows Certificate Store
```powershell
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

# Importar
Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}

if ($cert) {
    Write-Host "✅ Certificado importado com sucesso"
    Write-Host "   Subject: $($cert.Subject)"
    Write-Host "   Thumbprint: $($cert.Thumbprint)"
    Write-Host "   Has Private Key: $($cert.HasPrivateKey)"
} else {
    Write-Host "❌ Erro: Certificado não foi importado"
}
```

#### 4.3 Validar Certificado
```powershell
# Abrir Certificate Manager
certmgr.msc

# Navegar até: Personal → Certificates
# Deve aparecer certificado com CPF 517.648.902-30
# Ícone deve indicar que tem chave privada (chave pequena)
```

---

### FASE 5: Restaurar Código e Configurações

#### 5.1 Restaurar Código do Projeto
```powershell
$backupCodePath = "C:\backups\restore\backup_*\02_codigo"
$projectPath = "C:\projetos\crawler_tjsp"

# Criar diretório
New-Item -ItemType Directory -Path $projectPath -Force

# Copiar arquivos
Copy-Item "$backupCodePath\*" $projectPath -Recurse -Force

Write-Host "✅ Código restaurado"
```

#### 5.2 Criar Virtual Environment
```powershell
cd C:\projetos\crawler_tjsp

# Criar venv
python -m venv .venv

# Ativar
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Ou usar requirements_frozen.txt do backup
if (Test-Path "requirements_frozen.txt") {
    pip install -r requirements_frozen.txt
}

Write-Host "✅ Virtual environment criado"
```

#### 5.3 Verificar Arquivo .env
```powershell
$envPath = "C:\projetos\crawler_tjsp\.env"

if (Test-Path $envPath) {
    Write-Host "✅ Arquivo .env encontrado"
    
    # Verificar conteúdo crítico
    $envContent = Get-Content $envPath -Raw
    
    $criticalVars = @(
        "CERT_PATH",
        "CERT_PASSWORD",
        "CERT_CPF",
        "CHROME_BINARY_PATH",
        "CHROMEDRIVER_PATH"
    )
    
    foreach ($var in $criticalVars) {
        if ($envContent -match $var) {
            Write-Host "  ✅ $var presente"
        } else {
            Write-Host "  ⚠️  $var AUSENTE!"
        }
    }
} else {
    Write-Host "❌ Arquivo .env NÃO encontrado!"
    Write-Host "   Criar manualmente ou restaurar do backup"
}
```

---

### FASE 6: Configurar Chrome + Web Signer

#### 6.1 Login no Chrome
```
1. Abrir Chrome manualmente
2. Fazer login com: revisa.precatorio@gmail.com
3. Aguardar sincronização (pode levar 2-5 minutos)
4. Verificar extensões instaladas: chrome://extensions/
5. Web Signer deve aparecer na lista
```

#### 6.2 Configurar Web Signer
```
1. Verificar que Web Signer está rodando (ícone na bandeja)
2. Abrir Web Signer
3. Verificar que certificado é detectado
4. Testar seleção de certificado (deve aparecer)
```

---

### FASE 7: Restaurar PostgreSQL (Se Aplicável)

#### 7.1 Instalar PostgreSQL 15
```powershell
# Download PostgreSQL
$pgUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.6-1-windows-x64.exe"
$installerPath = "$env:TEMP\postgresql-installer.exe"

Invoke-WebRequest -Uri $pgUrl -OutFile $installerPath
Start-Process -FilePath $installerPath -Wait

Write-Host "✅ PostgreSQL instalado (configurar senha durante wizard)"
```

#### 7.2 Restaurar Dump do Banco
```powershell
$backupDbPath = "C:\backups\restore\backup_*\06_database"
$pgBinPath = "C:\Program Files\PostgreSQL\15\bin"

# Restaurar dump completo
& "$pgBinPath\psql.exe" -U postgres -f "$backupDbPath\all_databases_backup.sql"

# Ou restaurar apenas revisa_db
& "$pgBinPath\psql.exe" -U postgres -c "CREATE DATABASE revisa_db;"
& "$pgBinPath\psql.exe" -U postgres -d revisa_db -f "$backupDbPath\revisa_db_backup.sql"

# Restaurar configurações
Copy-Item "$backupDbPath\postgresql.conf" "C:\Program Files\PostgreSQL\15\data\" -Force
Copy-Item "$backupDbPath\pg_hba.conf" "C:\Program Files\PostgreSQL\15\data\" -Force

# Reiniciar serviço
Restart-Service postgresql-x64-15

Write-Host "✅ PostgreSQL restaurado"
```

---

### FASE 8: Testes de Validação

#### 8.1 Teste de Ambiente
```powershell
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1

# Verificar imports
python -c "import selenium; import psycopg2; import requests; print('✅ Imports OK')"

# Verificar acesso ao certificado
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CERT_PATH:', os.getenv('CERT_PATH'))"
```

#### 8.2 Teste de Autenticação
```powershell
python windows-server\scripts\test_authentication.py
```

**Resultado esperado:**
```
🔵 Iniciando teste de autenticação...
✅ Chrome aberto
✅ e-SAJ carregado
✅ Botão 'Certificado Digital' clicado
✅ Web Signer detectado
✅ Certificado selecionado
✅✅✅ LOGIN BEM-SUCEDIDO!
📸 Screenshot salvo
```

#### 8.3 Teste do Crawler
```powershell
# Teste com processo fictício
python crawler_full.py --debug --processo=1234567-89.2020.8.26.0100
```

---

## ✅ Checklist de Validação Pós-Restore

```markdown
### Software
- [ ] Python 3.12.3 instalado e funcionando
- [ ] Git instalado
- [ ] Chrome versão 131.0.6778.86 (ou compatível)
- [ ] ChromeDriver versão compatível
- [ ] Web Signer instalado e rodando
- [ ] PostgreSQL 15 (se aplicável)

### Certificado
- [ ] Arquivo .pfx em C:\certs\certificado.pfx
- [ ] Importado no Windows Certificate Store
- [ ] Aparece em certmgr.msc → Personal → Certificates
- [ ] Has Private Key: True
- [ ] Web Signer detecta certificado

### Código
- [ ] Código em C:\projetos\crawler_tjsp
- [ ] Arquivo .env presente e completo
- [ ] Virtual environment criado
- [ ] Dependências instaladas (pip list)
- [ ] Git configurado

### Chrome + Web Signer
- [ ] Chrome logado com revisa.precatorio@gmail.com
- [ ] Extensão Web Signer instalada
- [ ] Extensão habilitada e ativa
- [ ] Web Signer rodando (ícone bandeja)
- [ ] Comunicação extensão ↔ app nativo OK

### Banco de Dados
- [ ] PostgreSQL rodando (se local)
- [ ] Database revisa_db existe
- [ ] Tabelas restauradas
- [ ] Conexão funciona

### Testes
- [ ] test_authentication.py PASSOU
- [ ] Login com certificado funciona
- [ ] crawler_full.py executa sem erros
- [ ] Processo de teste processado com sucesso
```

---

## 🚨 Troubleshooting

### Problema: Certificado não importa
```powershell
# Verificar arquivo
Test-Path "C:\certs\certificado.pfx"

# Testar senha
$cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
$cert.Import("C:\certs\certificado.pfx", "903205", "Exportable")

# Se erro de senha: verificar SENHA_CERTIFICADO.txt no backup
```

### Problema: Web Signer não detecta certificado
```
1. Verificar que certificado está em Cert:\CurrentUser\My (não LocalMachine)
2. Reiniciar Web Signer
3. Verificar logs do Web Signer:
   C:\Program Files\Softplan\WebSigner\logs\
```

### Problema: Extensão Chrome não funciona
```
1. Deslogar e relogar no Chrome
2. Aguardar sincronização completa
3. Verificar em chrome://extensions/
4. Reinstalar extensão manualmente se necessário
```

### Problema: Python imports falham
```powershell
# Recriar virtual environment
cd C:\projetos\crawler_tjsp
Remove-Item .venv -Recurse -Force
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📞 Suporte

**Documentação relacionada:**
- BACKUP_GUIDE.md - Guia de backup completo
- DEPLOYMENT_PLAN.md - Plano de deployment original
- TROUBLESHOOTING_AUTENTICACAO.md - Problemas de autenticação

**Contatos:**
- Contabo: https://contabo.com/support
- Softplan Web Signer: https://websigner.softplan.com.br

---

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Status:** Pronto para uso  

