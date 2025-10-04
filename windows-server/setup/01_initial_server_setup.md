# 🔐 Configuração Inicial do Servidor Windows

**Fase 1 do Deployment Plan**
**Tempo estimado:** 30-45 minutos

---

## 📋 Pré-requisitos

- [ ] Email da Contabo com credenciais recebido
- [ ] Cliente RDP instalado no computador local
- [ ] Informações anotadas:
  - IP do servidor
  - Usuário (geralmente `Administrator`)
  - Senha inicial

---

## 1️⃣ Primeiro Acesso via RDP

### 1.1 Conectar via Remote Desktop

**Windows:**
```
1. Abrir "Conexão de Área de Trabalho Remota" (mstsc.exe)
2. Computador: <IP_DO_SERVIDOR>
3. Usuário: Administrator
4. Conectar
5. Inserir senha quando solicitado
6. Aceitar certificado (se aparecer aviso)
```

**macOS:**
```
1. Abrir "Microsoft Remote Desktop"
2. Add PC → IP do servidor
3. User account → Administrator
4. Conectar
```

**Linux:**
```bash
rdesktop <IP_DO_SERVIDOR> -u Administrator
# ou
xfreerdp /u:Administrator /v:<IP_DO_SERVIDOR>
```

### 1.2 Validações Iniciais

Após conectar, verificar:

```powershell
# Abrir PowerShell como Administrator
# Clique direito no botão Iniciar → "Windows PowerShell (Admin)"

# Verificar versão do Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
# Esperado: Windows Server 2016 Datacenter

# Verificar conectividade
ping google.com -n 4

# Verificar especificações
Get-ComputerInfo | Select-Object CsProcessors, CsTotalPhysicalMemory, CsNumberOfProcessors

# Verificar espaço em disco
Get-PSDrive C
```

**Checklist:**
- [ ] Desktop do Windows Server carregou
- [ ] PowerShell abre como Administrator
- [ ] Internet funcionando (ping google.com)
- [ ] Especificações batem com o contratado (3 vCPU, 8 GB RAM)

---

## 2️⃣ Configuração de Segurança Básica

### 2.1 Alterar Senha Padrão

```powershell
# Alterar senha do Administrator
net user Administrator *
# Inserir nova senha forte quando solicitado

# Dica de senha forte:
# - Mínimo 16 caracteres
# - Letras maiúsculas, minúsculas, números, símbolos
# - Exemplo: R3v!sa#Cr@wl3r2025$TjSP
```

### 2.2 Criar Usuário Secundário (Opcional)

```powershell
# Criar usuário para operações do dia-a-dia
net user CrawlerUser SenhaForte123! /add

# Adicionar ao grupo Administrators
net localgroup Administrators CrawlerUser /add

# Verificar
net user CrawlerUser
```

### 2.3 Configurar Windows Firewall

```powershell
# Habilitar firewall (geralmente já vem habilitado)
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# Permitir RDP (porta 3389) - geralmente já permitido
New-NetFirewallRule -DisplayName "Allow RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow -Enabled True

# Permitir ping (ICMP)
New-NetFirewallRule -DisplayName "Allow Ping" -Direction Inbound -Protocol ICMPv4 -Action Allow -Enabled True

# Verificar regras ativas
Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True" -and $_.Direction -eq "Inbound"} | Select-Object DisplayName, LocalPort
```

### 2.4 Desabilitar Recursos Desnecessários

```powershell
# Desabilitar IPv6 (se não for usar)
Disable-NetAdapterBinding -Name "*" -ComponentID ms_tcpip6

# Desabilitar Windows Defender Real-Time Protection (opcional - pode impactar performance)
# ATENÇÃO: Fazer isso apenas se tiver outro antivírus ou se for ambiente isolado
Set-MpPreference -DisableRealtimeMonitoring $true

# Desabilitar Server Manager ao login (opcional)
Get-ScheduledTask -TaskName "ServerManager" | Disable-ScheduledTask
```

**Checklist:**
- [ ] Senha do Administrator alterada
- [ ] Firewall configurado
- [ ] RDP acessível remotamente

---

## 3️⃣ Configuração de SSH (Opcional)

SSH no Windows é útil para automação e transferência de arquivos via SCP.

### 3.1 Instalar OpenSSH Server

```powershell
# Verificar se OpenSSH está disponível
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'

# Instalar OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Iniciar serviço
Start-Service sshd

# Configurar para iniciar automaticamente
Set-Service -Name sshd -StartupType 'Automatic'

# Verificar status
Get-Service sshd
```

### 3.2 Configurar Firewall para SSH

```powershell
# Permitir porta 22
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Verificar
Get-NetFirewallRule -Name sshd
```

### 3.3 Testar SSH

**Do seu computador local:**

```bash
# Linux/macOS
ssh Administrator@<IP_DO_SERVIDOR>

# Windows (PowerShell)
ssh Administrator@<IP_DO_SERVIDOR>
```

**Primeiro acesso:**
- Aceitar fingerprint (yes)
- Inserir senha

**Transferir arquivos via SCP:**

```bash
# Enviar arquivo local para servidor
scp /caminho/local/arquivo.txt Administrator@<IP_DO_SERVIDOR>:C:/temp/

# Baixar arquivo do servidor
scp Administrator@<IP_DO_SERVIDOR>:C:/temp/arquivo.txt /caminho/local/
```

**Checklist:**
- [ ] OpenSSH Server instalado
- [ ] Porta 22 liberada no firewall
- [ ] Conexão SSH funciona do computador local
- [ ] SCP funciona (testar envio de arquivo de teste)

---

## 4️⃣ Configuração de Timezone e Regionalização

```powershell
# Verificar timezone atual
Get-TimeZone

# Configurar para horário de Brasília
Set-TimeZone -Id "E. South America Standard Time"

# Verificar
Get-Date

# Configurar formato de data/hora (opcional)
Set-Culture pt-BR
```

**Checklist:**
- [ ] Timezone configurado para Brasília (GMT-3)
- [ ] Data/hora corretas

---

## 5️⃣ Atualizações do Windows

### 5.1 Verificar Atualizações Pendentes

```powershell
# Instalar módulo PSWindowsUpdate (se não tiver)
Install-Module PSWindowsUpdate -Force

# Verificar atualizações disponíveis
Get-WindowsUpdate

# Instalar atualizações críticas
Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot
```

**ATENÇÃO:** O servidor pode reiniciar automaticamente após instalar atualizações. Aguarde alguns minutos e reconecte via RDP.

### 5.2 Configurar Windows Update Automático (Recomendado)

```powershell
# Configurar para baixar e instalar atualizações automaticamente
$AU = New-Object -ComObject Microsoft.Update.AutoUpdate
$AU.Settings.NotificationLevel = 4  # 4 = Download and install automatically

# Ou via GPO (interface gráfica):
# 1. gpedit.msc
# 2. Computer Configuration > Administrative Templates > Windows Components > Windows Update
# 3. Configure Automatic Updates → Enabled → Auto download and schedule the install
```

**Checklist:**
- [ ] Atualizações críticas instaladas
- [ ] Windows Update configurado para automático
- [ ] Servidor reiniciado após atualizações

---

## 6️⃣ Criar Estrutura de Diretórios

```powershell
# Criar pastas principais
New-Item -ItemType Directory -Path "C:\projetos" -Force
New-Item -ItemType Directory -Path "C:\certs" -Force
New-Item -ItemType Directory -Path "C:\temp" -Force
New-Item -ItemType Directory -Path "C:\backups" -Force
New-Item -ItemType Directory -Path "C:\logs" -Force

# Verificar
Get-ChildItem C:\ -Directory | Where-Object {$_.Name -in @('projetos','certs','temp','backups','logs')}
```

**Checklist:**
- [ ] Pastas criadas: `C:\projetos`, `C:\certs`, `C:\temp`, `C:\backups`, `C:\logs`

---

## 7️⃣ Configurar PowerShell Execution Policy

```powershell
# Permitir execução de scripts PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine -Force

# Verificar
Get-ExecutionPolicy -List
```

**Checklist:**
- [ ] Execution Policy configurado para `RemoteSigned`

---

## 8️⃣ Instalar Chocolatey (Package Manager)

Chocolatey facilita instalação de software via linha de comando.

```powershell
# Executar como Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Verificar instalação
choco --version

# Atualizar Chocolatey
choco upgrade chocolatey -y
```

**Checklist:**
- [ ] Chocolatey instalado
- [ ] Comando `choco` funciona

---

## 9️⃣ Configurar Acesso Remoto Seguro (Opcional)

### 9.1 Alterar Porta RDP Padrão (Segurança)

**ATENÇÃO:** Isso pode bloquear acesso se não for feito corretamente. Faça apenas se tiver experiência.

```powershell
# Alterar porta RDP de 3389 para 33890 (exemplo)
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name 'PortNumber' -Value 33890

# Atualizar firewall
New-NetFirewallRule -DisplayName "RDP Custom Port" -Direction Inbound -Protocol TCP -LocalPort 33890 -Action Allow

# Reiniciar serviço RDP
Restart-Service TermService -Force

# Conectar usando: <IP>:33890
```

### 9.2 Configurar VPN (Avançado)

Se desejar acesso via VPN (WireGuard, OpenVPN), consultar documentação específica.

---

## 🔟 Criar Snapshot Inicial

**No painel da Contabo (navegador web):**

1. Acessar: https://my.contabo.com
2. Login com credenciais Contabo
3. Ir para "Cloud VPS"
4. Selecionar "Cloud VPS 10"
5. Aba "Snapshots"
6. Clicar "Create Snapshot"
7. Nome: `initial-setup-windows-2025-10-04`
8. Aguardar criação (~5-10 minutos)

**Checklist:**
- [ ] Snapshot criado com sucesso
- [ ] Nome descritivo e com data

---

## ✅ Checklist Final da Fase 1

- [ ] Acesso via RDP funcionando
- [ ] Senha do Administrator alterada
- [ ] Windows Firewall configurado
- [ ] SSH configurado e testado (opcional)
- [ ] Timezone configurado (Brasília)
- [ ] Windows Update instalado
- [ ] Estrutura de diretórios criada
- [ ] PowerShell Execution Policy configurado
- [ ] Chocolatey instalado
- [ ] Snapshot inicial criado
- [ ] Servidor reiniciado ao menos 1x (após updates)

---

## 🚀 Próximos Passos

Após concluir esta fase, prosseguir para:

**[02_python_installation.md](02_python_installation.md)** - Instalação do Python 3.12 e dependências

---

## 📞 Troubleshooting

### Problema: Não consigo conectar via RDP

**Soluções:**
1. Verificar se IP está correto (email da Contabo)
2. Verificar se firewall local (do seu PC) não está bloqueando porta 3389
3. Testar ping para o servidor: `ping <IP_DO_SERVIDOR>`
4. Contatar suporte Contabo se servidor não responder

### Problema: Senha não funciona

**Soluções:**
1. Verificar Caps Lock
2. Verificar layout do teclado (EN vs PT-BR)
3. Resetar senha pelo painel da Contabo
4. Usar "Keyboard" do painel Contabo (VNC console)

### Problema: SSH não conecta

**Soluções:**
```powershell
# No servidor, verificar se serviço está rodando
Get-Service sshd

# Reiniciar serviço
Restart-Service sshd

# Verificar firewall
Get-NetFirewallRule -Name sshd

# Verificar logs
Get-EventLog -LogName Application -Source OpenSSH -Newest 20
```

---

**Última atualização:** 2025-10-04
**Tempo médio de execução:** 30-45 minutos
**Próxima fase:** Instalação de Python
