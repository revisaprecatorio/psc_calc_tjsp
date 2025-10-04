# 🚀 Guia Rápido - Setup Windows Server

**Tempo estimado total:** 90-120 minutos
**Última atualização:** 2025-10-04

---

## 📋 Informações do Servidor

### Credenciais de Acesso
- **IP:** `62.171.143.88`
- **Usuário:** `Administrator`
- **Senha:** [definida durante o pedido]
- **VNC (emergência):** `144.91.83.202:63090` (senha: `gvE8kTgs`)

### Especificações
- **CPU:** 3 vCPU Cores
- **RAM:** 8 GB
- **Storage:** 75 GB NVMe + 150 GB SSD
- **OS:** Windows Server 2016 Datacenter
- **Região:** European Union

---

## ⚡ Início Rápido (5 Passos)

### 1️⃣ Conectar via RDP (5 min)

**macOS:**
```bash
# Abrir Microsoft Remote Desktop
# Adicionar PC:
#   - Host: 62.171.143.88
#   - User: Administrator
#   - Password: [sua senha]
# Conectar
```

**Windows:**
```cmd
# Executar (Win + R):
mstsc.exe

# Inserir:
#   Computer: 62.171.143.88
#   Username: Administrator
# Conectar e inserir senha
```

**Validação:**
- [ ] Desktop do Windows Server carregou
- [ ] Pode abrir PowerShell como Administrator

---

### 2️⃣ Executar Script de Setup Automático (60-90 min)

**No servidor (PowerShell como Administrator):**

```powershell
# Criar pasta temporária e baixar script
New-Item -ItemType Directory -Path "C:\temp" -Force
cd C:\temp

# Baixar repositório
Invoke-WebRequest -Uri "https://github.com/revisaprecatorio/crawler_tjsp/archive/refs/heads/main.zip" -OutFile "repo.zip"
Expand-Archive -Path "repo.zip" -DestinationPath "." -Force

# Ou clonar via Git (se preferir)
# git clone https://github.com/revisaprecatorio/crawler_tjsp.git C:\projetos\crawler_tjsp

# Navegar para scripts
cd crawler_tjsp-main\windows-server\scripts

# Liberar execução de scripts PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Executar setup completo
.\setup-complete.ps1
```

**O script instalará:**
- ✅ Python 3.12.3
- ✅ Git para Windows
- ✅ Google Chrome
- ✅ ChromeDriver (compatível com Chrome instalado)
- ✅ Estrutura de diretórios (C:\projetos, C:\certs, etc.)
- ✅ Virtual environment Python
- ✅ Dependências do projeto

**⚠️ Ações manuais necessárias:**
1. **Web Signer:** Baixar e instalar de https://websigner.softplan.com.br/downloads
2. **ChromeDriver:** Se download automático falhar, baixar manualmente de https://googlechromelabs.github.io/chrome-for-testing/

---

### 3️⃣ Transferir e Importar Certificado (10 min)

**Transferir certificado do seu Mac para o servidor:**

**Opção A: Via RDP (arrastar e soltar)**
1. Conectar via RDP
2. Arrastar arquivo `25424636_pf.pfx` do Mac para desktop do servidor
3. Mover para `C:\certs\certificado.pfx`

**Opção B: Via SCP (se SSH configurado)**
```bash
# Do seu Mac
scp /Users/persivalballeste/Documents/@IANIA/PROJECTS/revisa/revisa/2_Crawler/crawler_tjsp/25424636_pf.pfx Administrator@62.171.143.88:C:/certs/certificado.pfx
```

**Importar certificado no Windows:**

```powershell
# No servidor (PowerShell)
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar importação
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*CPF*"}
```

**Validação:**
- [ ] Arquivo em `C:\certs\certificado.pfx`
- [ ] Certificado aparece em `certmgr.msc` → Personal → Certificates
- [ ] Certificado tem chave privada (ícone de chave)

---

### 4️⃣ Configurar .env (5 min)

```powershell
# Navegar para projeto
cd C:\projetos\crawler_tjsp

# Copiar template
Copy-Item .env.example .env

# Editar .env (usar notepad ou editor de preferência)
notepad .env
```

**Conteúdo mínimo do .env:**

```ini
# PostgreSQL (ajustar conforme necessário)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=SuaSenhaSegura123!

# Chrome
CHROME_BINARY_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe

# Certificado
CERT_PATH=C:\certs\certificado.pfx
CERT_PASSWORD=903205

# Logs
LOG_LEVEL=INFO
LOG_PATH=C:\projetos\crawler_tjsp\logs
```

**Validação:**
- [ ] Arquivo `.env` criado
- [ ] Todas as variáveis preenchidas
- [ ] Paths do Chrome e ChromeDriver corretos

---

### 5️⃣ Testar Autenticação (15 min)

**TESTE CRÍTICO: Validar se Native Messaging funciona**

```powershell
# Navegar para projeto
cd C:\projetos\crawler_tjsp

# Ativar virtual environment
.\venv\Scripts\Activate.ps1

# Executar teste de autenticação
python windows-server\scripts\test_authentication.py
```

**O que deve acontecer:**
1. ✅ Chrome abre via Selenium
2. ✅ e-SAJ carrega
3. ✅ Script clica em "Certificado Digital"
4. ✅ **Web Signer abre modal de seleção** (Native Messaging funcionando!)
5. ✅ Você seleciona o certificado
6. ✅ Login bem-sucedido!

**Se o teste passar:**
```
✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO! ✅✅✅
🎉 RESULTADO DO TESTE: SUCESSO! 🎉
✅ Native Messaging Protocol funcionou corretamente!
```

**Parabéns! Migração bem-sucedida!** 🎉

---

## 🔄 Próximos Passos (Pós-Setup)

### 6️⃣ Configurar PostgreSQL (30 min)

**Opção A: PostgreSQL Local**
```powershell
# Baixar PostgreSQL 15
Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-15.6-1-windows-x64.exe" -OutFile "C:\temp\postgresql.exe"

# Instalar (seguir wizard)
C:\temp\postgresql.exe

# Criar database e usuário
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

```sql
-- No prompt do psql
CREATE DATABASE revisa_db;
CREATE USER revisa_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE revisa_db TO revisa_user;
\q
```

**Opção B: Usar PostgreSQL Remoto**
- Apenas configurar .env com IP do servidor PostgreSQL existente

### 7️⃣ Testar Crawler Completo (15 min)

```powershell
cd C:\projetos\crawler_tjsp
.\venv\Scripts\Activate.ps1

# Testar crawler com processo real
python crawler_full.py --debug --processo=1234567-89.2020.8.26.0100
```

### 8️⃣ Configurar Worker (Orchestrator) (30 min)

```powershell
# Testar orchestrator manualmente
python orchestrator_subprocess.py

# Criar Windows Service (usar NSSM)
# Download NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "C:\temp\nssm.zip"
Expand-Archive -Path "C:\temp\nssm.zip" -DestinationPath "C:\nssm" -Force

# Instalar serviço
C:\nssm\nssm-2.24\win64\nssm.exe install CrawlerTJSP "C:\projetos\crawler_tjsp\venv\Scripts\python.exe" "C:\projetos\crawler_tjsp\orchestrator_subprocess.py"

# Configurar
C:\nssm\nssm-2.24\win64\nssm.exe set CrawlerTJSP AppDirectory "C:\projetos\crawler_tjsp"
C:\nssm\nssm-2.24\win64\nssm.exe set CrawlerTJSP AppStdout "C:\projetos\crawler_tjsp\logs\service.log"

# Iniciar
C:\nssm\nssm-2.24\win64\nssm.exe start CrawlerTJSP
```

### 9️⃣ Criar Snapshot (5 min)

**No painel da Contabo:**
1. Acessar https://my.contabo.com
2. Ir para "Cloud VPS"
3. Selecionar "Cloud VPS 10"
4. Aba "Snapshots"
5. Criar snapshot: `production-ready-2025-10-04`

---

## 📞 Troubleshooting Rápido

### Problema: Não consigo conectar via RDP
**Solução:**
- Verificar se IP está correto: `62.171.143.88`
- Testar ping: `ping 62.171.143.88`
- Usar VNC como alternativa: `144.91.83.202:63090`

### Problema: Script setup-complete.ps1 não executa
**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### Problema: ChromeDriver incompatível
**Solução:**
1. Verificar versão do Chrome: `& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version`
2. Baixar ChromeDriver compatível: https://googlechromelabs.github.io/chrome-for-testing/
3. Extrair para `C:\chromedriver\`

### Problema: Web Signer não detecta certificado
**Solução:**
1. Verificar certificado importado: `certmgr.msc` → Personal → Certificates
2. Reinstalar Web Signer
3. Reiniciar Web Signer (Task Manager → Finalizar → Abrir novamente)

### Problema: Teste de autenticação falha
**Solução:**
1. Verificar Web Signer rodando (bandeja do sistema)
2. Verificar extensão em `chrome://extensions/`
3. Testar login manual primeiro:
   - Abrir Chrome
   - Ir para https://esaj.tjsp.jus.br/esaj/portal.do
   - Clicar "Certificado Digital"
   - Verificar se modal abre

---

## 📚 Documentação Completa

- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Plano detalhado de deployment (7 fases)
- **[MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md)** - Checklist completo de migração
- **[CREDENTIALS.md](CREDENTIALS.md)** - Todas as credenciais (arquivo local, não commitado)
- **[setup/01_initial_server_setup.md](setup/01_initial_server_setup.md)** - Setup inicial detalhado
- **[setup/02_python_installation.md](setup/02_python_installation.md)** - Instalação Python detalhada
- **[setup/03_chrome_websigner.md](setup/03_chrome_websigner.md)** - Chrome + Web Signer detalhado

---

## ✅ Checklist Rápido

- [ ] Conectado via RDP
- [ ] Script `setup-complete.ps1` executado com sucesso
- [ ] Web Signer instalado e rodando
- [ ] Certificado transferido e importado
- [ ] Arquivo `.env` configurado
- [ ] Teste de autenticação passou ✅
- [ ] PostgreSQL configurado
- [ ] Crawler testado manualmente
- [ ] Orchestrator configurado como serviço
- [ ] Snapshot de produção criado

---

**Se todos os itens acima estiverem ✅, o sistema está pronto para produção!**

🎉 **Migração para Windows Server concluída com sucesso!** 🎉

---

**Suporte:**
- Documentação: Ver arquivos em `/windows-server/`
- Logs: `C:\projetos\crawler_tjsp\logs\`
- Screenshots: `C:\projetos\crawler_tjsp\screenshots\`
