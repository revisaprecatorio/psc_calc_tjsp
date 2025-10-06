# 🤖 Instruções - Script de Instalação Automática

**Script:** `auto-install-complete.ps1`  
**Sistema:** Windows Server 2022  
**Tempo:** 2-3 horas (90% automatizado)  
**Data:** 2025-10-06

---

## 📋 O Que o Script Faz Automaticamente

### ✅ ETAPA 1: Configuração Base (5 min)
- Habilita TLS 1.2
- Configura Execution Policy
- Define timezone para Brasília
- Cria estrutura de diretórios

### ✅ ETAPA 2: Python 3.12.3 (10 min)
- Baixa instalador (70 MB)
- Instala Python silenciosamente
- Atualiza pip
- Instala virtualenv, wheel, setuptools

### ✅ ETAPA 3: Git (5 min)
- Baixa Git 2.44.0 (50 MB)
- Instala silenciosamente
- Configura usuário e email

### ✅ ETAPA 4: Chrome + ChromeDriver (10 min)
- Baixa Chrome Enterprise (100 MB)
- Instala silenciosamente
- Detecta versão do Chrome
- Baixa ChromeDriver compatível automaticamente

### ✅ ETAPA 5: Visual C++ Build Tools (15 min)
- Baixa instalador (1-2 GB)
- Instala ferramentas C++ (para psycopg2)
- **ETAPA MAIS DEMORADA!**

### ✅ ETAPA 6: Projeto Python (10 min)
- Cria pasta C:\projetos\crawler_tjsp
- Cria virtual environment
- Instala dependências (selenium, fastapi, etc)
- Cria arquivo .env
- Cria script quickstart.ps1

### ✅ ETAPA 7: Relatório Final (1 min)
- Gera relatório de instalação
- Lista software instalado
- Mostra próximas etapas manuais

---

## 🚀 COMO USAR O SCRIPT

### **PASSO 1: Copiar o Script**

1. Abra este arquivo no seu Mac/PC:
   ```
   windows-server/scripts/auto-install-complete.ps1
   ```

2. Selecione TODO o conteúdo (Cmd+A / Ctrl+A)

3. Copie (Cmd+C / Ctrl+C)

---

### **PASSO 2: Preparar no Servidor**

1. Conectar via RDP ao servidor:
   - IP: `62.171.143.88`
   - User: `Administrator`
   - Pass: `31032025`

2. Abrir **Notepad** no servidor:
   - Clique no botão Iniciar
   - Digite: `notepad`
   - Enter

3. Colar o script no Notepad (Ctrl+V)

4. Salvar arquivo:
   - File → Save As
   - Local: `C:\temp\auto-install.ps1`
   - **IMPORTANTE:** Em "Save as type" escolher **"All Files (*.*)"**
   - Clicar em "Save"

---

### **PASSO 3: Executar o Script**

1. Abrir **PowerShell como Administrator**:
   - Clique direito no botão Iniciar
   - Selecione: **"Windows PowerShell (Admin)"**
   - Se perguntar "Permitir alterações?", clique **"Sim"**

2. Navegar até o script:
   ```powershell
   cd C:\temp
   ```

3. Executar o script:
   ```powershell
   .\auto-install.ps1
   ```

4. **AGUARDAR 2-3 HORAS**
   - Janela do PowerShell vai mostrar progresso
   - **NÃO FECHE a janela!**
   - Pode minimizar e fazer outras coisas
   - Servidor pode ficar lento durante instalação

---

## 📊 O Que Você Vai Ver Durante a Execução

```
=====================================================
  AUTO INSTALACAO COMPLETA - CRAWLER TJSP
  Windows Server 2022
=====================================================

[INFO] Iniciando pre-validacoes...
[SUCCESS] Executando como Administrator
[SUCCESS] Conexao com internet OK

============================================
  ETAPA 1/7: Configuracao Base do Sistema
============================================

[SUCCESS] Execution Policy configurado
[SUCCESS] Timezone: E. South America Standard Time
[SUCCESS] Criado: C:\projetos
[SUCCESS] Criado: C:\certs
...

============================================
  ETAPA 2/7: Instalacao do Python 3.12.3
============================================

[INFO] Baixando Python 3.12.3...
[SUCCESS] Download concluido
[INFO] Instalando Python (pode levar 3-5 minutos)...
[SUCCESS] Python instalado
...
```

---

## ⏱️ Tempo Estimado Por Etapa

| Etapa | Descrição | Tempo |
|-------|-----------|-------|
| 1 | Configuração base | 5 min |
| 2 | Python 3.12.3 | 10 min |
| 3 | Git | 5 min |
| 4 | Chrome + ChromeDriver | 10 min |
| 5 | **Visual C++ Build Tools** | **15-20 min** ⏳ |
| 6 | Projeto Python | 10 min |
| 7 | Relatório final | 1 min |
| **TOTAL** | | **~2 horas** |

---

## ✅ Quando o Script Terminar

Você vai ver esta mensagem:

```
=====================================================
  INSTALACAO AUTOMATIZADA CONCLUIDA!
=====================================================

[SUCCESS] Instalacao automatizada concluida com sucesso!

PROXIMAS ETAPAS MANUAIS:
  1. Instalar Web Signer
  2. Transferir certificado.pfx
  3. Importar certificado
  4. Configurar Chrome (login + extensao)
  5. Testar autenticacao

Consultar: C:\projetos\crawler_tjsp\INSTALACAO_RELATORIO.txt

Pressione Enter para finalizar
```

---

## 🔧 ETAPAS MANUAIS (Após Script Terminar)

Após o script terminar, você precisa fazer **5 etapas manuais** que não podem ser automatizadas:

---

### **📥 MANUAL 1: Instalar Web Signer (10 min)**

```powershell
# No PowerShell, abrir navegador:
Start-Process "chrome.exe" -ArgumentList "https://websigner.softplan.com.br/downloads"
```

**Passos:**
1. Chrome vai abrir a página de downloads
2. Clicar em **"Download Web Signer para Windows"**
3. Salvar em: `C:\temp\websigner-installer.exe`
4. Executar o instalador (duplo-clique)
5. Seguir wizard: Next → Next → Install → Finish
6. Web Signer vai iniciar (ícone na bandeja)

**Verificar:**
```powershell
Get-Process | Where-Object {$_.Name -like "*websigner*"}
```

---

### **📁 MANUAL 2: Transferir Certificado (5 min)**

**Opção A: Via SCP (Do seu Mac/PC local)**

```bash
# No seu Mac/PC local, executar:
scp /caminho/do/certificado.pfx Administrator@62.171.143.88:C:/certs/

# Exemplo:
scp ~/Downloads/certificado.pfx Administrator@62.171.143.88:C:/certs/
```

**Opção B: Via RDP (Arrastar e Soltar)**

1. Manter conexão RDP aberta
2. No seu Mac/PC local, localizar arquivo `certificado.pfx`
3. Arrastar arquivo para o **Desktop do servidor**
4. No servidor, mover arquivo para `C:\certs\`

**Verificar no servidor:**
```powershell
Test-Path "C:\certs\certificado.pfx"
# Deve retornar: True
```

---

### **🔐 MANUAL 3: Importar Certificado (2 min)**

No **PowerShell do servidor**:

```powershell
# Importar certificado no Windows Certificate Store
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar importação
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
```

**Resultado esperado:**
```
Subject: CN=..., OU=..., CPF=517.648.902-30
Thumbprint: ABC123...
NotAfter: 01/01/2026
HasPrivateKey: True
```

**Verificar no Web Signer:**
1. Clicar no ícone Web Signer (bandeja/system tray)
2. Abrir configurações
3. Verificar se certificado aparece na lista
4. Certificado deve ser: **CPF 517.648.902-30**

---

### **🌐 MANUAL 4: Configurar Chrome Profile (10 min)**

**No servidor:**

```powershell
# Abrir Chrome
Start-Process "chrome.exe"
```

**Passos:**
1. Chrome vai abrir (primeira vez)
2. Clicar em **"Sign in to Chrome"** ou ícone do usuário (canto superior direito)
3. Login: **revisa.precatorio@gmail.com**
4. Inserir senha do Google
5. Aguardar sincronização (2-5 minutos)
   - Chrome vai sincronizar favoritos, extensões, etc.
   - Extensão Web Signer vai aparecer automaticamente

**Verificar extensão:**
```powershell
# Abrir página de extensões
Start-Process "chrome.exe" -ArgumentList "chrome://extensions/"
```

**Na página chrome://extensions/:**
- [ ] Extensão **"Web Signer"** aparece na lista
- [ ] Extensão está **HABILITADA** (toggle azul)
- [ ] Ícone Web Signer aparece na toolbar

---

### **✅ MANUAL 5: Testar Autenticação (5 min)**

**Teste Manual:**

```powershell
# Abrir e-SAJ
Start-Process "chrome.exe" -ArgumentList "https://esaj.tjsp.jus.br/esaj/portal.do"
```

**No Chrome:**
1. e-SAJ carrega
2. Clicar em **"Certificado Digital"**
3. Web Signer abre modal de seleção
4. Selecionar certificado: **CPF 517.648.902-30**
5. Login deve ser bem-sucedido
6. URL muda para: `portal.do?servico=...`

**Se funcionou: 🎉 SISTEMA 100% OPERACIONAL!**

---

## 📊 Verificação Final (Checklist)

```powershell
# Executar no PowerShell para verificar tudo:

# 1. Python
python --version
# Esperado: Python 3.12.3

# 2. Git
git --version
# Esperado: git version 2.44.0.windows.1

# 3. Chrome
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
# Esperado: Google Chrome 131.x

# 4. ChromeDriver
chromedriver --version
# Esperado: ChromeDriver 131.x

# 5. Certificado
Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
# Esperado: Subject + Thumbprint + HasPrivateKey: True

# 6. Web Signer
Get-Process | Where-Object {$_.Name -like "*websigner*"}
# Esperado: Nome + ID do processo

# 7. Virtual environment
Test-Path "C:\projetos\crawler_tjsp\.venv\Scripts\python.exe"
# Esperado: True

# 8. Dependências Python
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1
pip list
# Esperado: selenium, fastapi, uvicorn, etc.
```

---

## 🔧 Comandos Úteis Pós-Instalação

### Iniciar Ambiente Python:

```powershell
cd C:\projetos\crawler_tjsp
.\quickstart.ps1
```

### Atualizar Código (se tiver repositório Git):

```powershell
cd C:\projetos\crawler_tjsp
git pull origin main
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Criar Snapshot Pós-Instalação:

**No painel Contabo (navegador):**
1. Acessar: https://my.contabo.com
2. Login
3. Cloud VPS → Selecionar servidor
4. Snapshots → Create Snapshot
5. Nome: `post-install-ws2022-clean-2025-10-06`
6. Aguardar criação (~10-15 min)

---

## 🚨 Troubleshooting

### Problema: Script não executa

**Erro:** "Execution of scripts is disabled"

**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\auto-install.ps1
```

---

### Problema: ChromeDriver incompatível

**Erro:** "session not created: This version of ChromeDriver only supports Chrome version X"

**Solução:**
```powershell
# Verificar versões
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
chromedriver --version

# Baixar ChromeDriver compatível:
# https://googlechromelabs.github.io/chrome-for-testing/

# Substituir C:\chromedriver\chromedriver.exe
```

---

### Problema: Web Signer não detecta certificado

**Soluções:**

1. Verificar se certificado foi importado:
```powershell
Get-ChildItem Cert:\CurrentUser\My
```

2. Reimportar se necessário:
```powershell
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText
Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword
```

3. Reiniciar Web Signer:
```powershell
Get-Process | Where-Object {$_.Name -like "*websigner*"} | Stop-Process
Start-Process "C:\Program Files\Softplan\WebSigner\websigner.exe"
```

---

### Problema: Extensão Chrome não aparece

**Soluções:**

1. Verificar se Chrome está sincronizado:
   - Abrir Chrome
   - Clicar no ícone do perfil (canto superior direito)
   - Verificar se aparece "revisa.precatorio@gmail.com"
   - Aguardar sincronização completa

2. Instalar extensão manualmente:
   - Acessar: https://chrome.google.com/webstore
   - Procurar: "Web Signer Softplan"
   - Clicar em "Adicionar ao Chrome"

---

## 📞 Contato e Suporte

**Documentação completa:** `windows-server/`
- FRESH_INSTALL_WS2025.md
- DEPLOYMENT_PLAN.md
- TROUBLESHOOTING_AUTENTICACAO.md

**Logs:**
- Script: `C:\temp\install_log_[timestamp].txt`
- Relatório: `C:\projetos\crawler_tjsp\INSTALACAO_RELATORIO.txt`

---

## ✅ Checklist Final

```markdown
INSTALAÇÃO AUTOMATIZADA:
- [ ] Script executado sem erros
- [ ] Python 3.12.3 instalado
- [ ] Git instalado e configurado
- [ ] Chrome + ChromeDriver instalados
- [ ] Build Tools instalados
- [ ] Virtual environment criado
- [ ] Dependências Python instaladas

ETAPAS MANUAIS:
- [ ] Web Signer instalado e rodando
- [ ] Certificado transferido para C:\certs\
- [ ] Certificado importado no Windows
- [ ] Web Signer detecta certificado
- [ ] Chrome logado com revisa.precatorio@gmail.com
- [ ] Extensão Web Signer habilitada
- [ ] Teste de login manual bem-sucedido

FINALIZAÇÃO:
- [ ] Snapshot pós-instalação criado
- [ ] Relatório revisado
- [ ] Sistema validado e funcional
```

---

**🎉 BOA INSTALAÇÃO!**

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Tempo total estimado:** 2-3 horas

