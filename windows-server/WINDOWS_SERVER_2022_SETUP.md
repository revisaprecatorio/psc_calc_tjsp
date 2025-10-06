# Setup Windows Server 2022 - Crawler TJSP

**Data:** 2025-10-06
**Servidor:** Contabo Cloud VPS 10
**IP:** 62.171.143.88
**OS:** Windows Server 2022 Datacenter
**Status:** ✅ Configurado para testes e automação

---

## 🎯 OBJETIVO

Configurar Windows Server 2022 como **ambiente de execução totalmente livre de restrições** para:
- Web scraping automatizado
- Execução de Chrome com extensões (Web Signer)
- Automação contínua sem bloqueios de segurança

**IMPORTANTE:** Este servidor é **EXCLUSIVO para testes e automação**. Não contém dados sensíveis.

---

## 🔓 DESBLOQUEIO COMPLETO DO SISTEMA

### Motivação

Para eliminar interferências como:
- Bloqueios de execução de scripts
- Prompts de confirmação UAC
- Restrições de política de grupo
- Firewall bloqueando portas (incluindo 9222 para Remote Debugging)
- Antivírus bloqueando ChromeDriver

### Ações Executadas

#### 1. **Elevação Total de Privilégios**
- Uso de **PsExec (Sysinternals)** para executar comandos em nível SYSTEM

#### 2. **Políticas de Execução PowerShell**
```powershell
Set-ExecutionPolicy Unrestricted -Scope LocalMachine -Force
```
✅ **Resultado:** Nenhum script bloqueado

#### 3. **Serviços de Segurança Desativados**

| Serviço | Nome | Status |
|---------|------|--------|
| Application Identity | AppIDSvc | Disabled (Start=4) |
| AppLocker | AppLocker | Disabled (Start=4) |
| Group Policy | gpsvc | Disabled (Start=4) |
| Security Health | SecurityHealthService | Disabled (Start=4) |
| Windows Defender ATP | Sense | Disabled (Start=4) |
| Windows Defender | WinDefend | Disabled (Start=4) |

```powershell
# Comandos executados
sc config AppIDSvc start= disabled
sc config gpsvc start= disabled
sc config SecurityHealthService start= disabled
sc config Sense start= disabled
sc config WinDefend start= disabled

# Parar serviços
Stop-Service AppIDSvc -Force
Stop-Service gpsvc -Force
Stop-Service SecurityHealthService -Force
Stop-Service Sense -Force
Stop-Service WinDefend -Force
```

✅ **Resultado:** Nenhum serviço de segurança interferindo

#### 4. **Firewall Desativado**

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False
```

**Status Atual:**
```
Domain   False
Private  False
Public   False
```

✅ **Resultado:** Nenhuma porta bloqueada (crítico para Remote Debugging porta 9222)

#### 5. **UAC (User Account Control) Desativado**

```powershell
Set-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name EnableLUA -Value 0
Set-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name ConsentPromptBehaviorAdmin -Value 0
```

✅ **Resultado:** Nenhum prompt de confirmação

#### 6. **Windows Defender - Desativação Permanente**

```powershell
# Registro
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WinDefend" /v Start /t REG_DWORD /d 4 /f
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f
```

✅ **Resultado:** Defender não inicia, não bloqueia executáveis

---

## 📊 ESTADO ATUAL DO SERVIDOR

| Componente | Status | Observação |
|------------|--------|------------|
| **Execução PowerShell** | Unrestricted | Scripts executam livremente |
| **Firewall** | Desativado (todos perfis) | Porta 9222 acessível |
| **Windows Defender** | Desativado permanentemente | ChromeDriver não bloqueado |
| **AppLocker** | Desativado | Nenhum bloqueio de executável |
| **Group Policy** | Desativado | Sem políticas impostas |
| **UAC** | Desativado | Acesso administrativo pleno |
| **Persistência** | ✅ Configurado | Sobrevive a reboots |

---

## ✅ VALIDAÇÃO

Execute estes comandos para validar:

```powershell
# 1. Políticas de Execução
Get-ExecutionPolicy -List

# 2. Firewall
Get-NetFirewallProfile | Select Name, Enabled

# 3. Serviços de Segurança
Get-Service AppIDSvc, gpsvc, SecurityHealthService, Sense, WinDefend | Select Name, Status, StartType

# 4. UAC
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' | Select EnableLUA, ConsentPromptBehaviorAdmin
```

---

## 🔐 REVERSÃO (OPCIONAL)

Se futuramente precisar restaurar segurança básica:

```powershell
# Firewall
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True

# Defender
reg add "HKLM\SYSTEM\CurrentControlSet\Services\WinDefend" /v Start /t REG_DWORD /d 2 /f

# UAC
Set-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name EnableLUA -Value 1

# Group Policy
sc config gpsvc start= auto
```

---

## 📦 SOFTWARE INSTALADO

### 1. **Python 3.12.3**
```powershell
python --version
# Python 3.12.3
```

### 2. **Git para Windows**
```powershell
git --version
# git version 2.x.x
```

### 3. **Google Chrome**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
# Google Chrome 131.0.6778.86
```

### 4. **ChromeDriver**
```powershell
C:\chromedriver\chromedriver.exe --version
# ChromeDriver 131.x.x
```

### 5. **OpenSSH Server**
```powershell
Get-Service sshd
# Status: Running, StartType: Automatic
```

### 6. **Web Signer**
- Instalado no perfil Default do Chrome
- Acesso: `chrome://extensions/`

---

## 🚀 PRÓXIMOS PASSOS

### 1. Transferir e Importar Certificado
```powershell
# Criar pasta
New-Item -ItemType Directory -Path C:\certs -Force

# Transferir via SCP (do Mac)
# scp 25424636_pf.pfx Administrator@62.171.143.88:/certs/certificado.pfx

# Importar
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText
Import-PfxCertificate -FilePath C:\certs\certificado.pfx -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword
```

### 2. Clonar Repositório
```powershell
cd C:\projetos
git clone https://github.com/revisaprecatorio/crawler_tjsp.git
cd crawler_tjsp
```

### 3. Configurar Ambiente Python
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Testar Remote Debugging
```powershell
# Com Firewall DESABILITADO e segurança OFF, Remote Debugging DEVE funcionar!
.\windows-server\scripts\start_chrome_debug_v2.bat

# Testar porta
Invoke-WebRequest -Uri "http://localhost:9222/json/version" -UseBasicParsing
```

---

## 🎯 DIFERENÇAS vs Windows Server 2016

| Aspecto | Windows Server 2016 | Windows Server 2022 |
|---------|---------------------|---------------------|
| Remote Debugging | ❌ Não funciona (bug) | ✅ **DEVE funcionar** |
| TLS 1.2 | Manual | ✅ Padrão |
| OpenSSH | Instalação manual | ✅ Feature nativa |
| Chrome Stability | Crashes frequentes | ✅ Mais estável |
| Firewall bloqueando 9222 | ❌ Sim | ✅ **DESABILITADO** |

---

## ⚠️ AVISOS DE SEGURANÇA

### ❌ **NÃO USE ESTA CONFIGURAÇÃO PARA:**
- Servidores de produção
- Ambientes com dados sensíveis
- Redes corporativas
- Servidores acessíveis pela internet pública (sem VPN)

### ✅ **USE APENAS PARA:**
- Testes e desenvolvimento
- Automação controlada
- Scraping/crawling
- Ambiente isolado para robôs

---

## 📝 MANUTENÇÃO

### Atualização de Certificado
Quando sessão expirar (7-30 dias):
1. Login manual no Chrome (perfil Default)
2. Re-extrair cookies: `python extract_cookies.py`
3. Crawler volta a funcionar

### Monitoramento
- Logs: `C:\projetos\crawler_tjsp\logs\`
- Screenshots: `C:\projetos\crawler_tjsp\screenshots\`
- Cookies: `C:\projetos\crawler_tjsp\saved_cookies\` (não commitar!)

---

**Responsável:** Persival Balleste + Claude
**Última Atualização:** 2025-10-06 05:30
**Status:** ✅ Servidor desbloqueado e pronto para automação
