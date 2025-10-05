# 🚀 EXECUTE AGORA - Comandos para o Servidor Windows

**Status:** ✅ RDP conectado com sucesso!
**Servidor:** 62.171.143.88
**Usuário:** Administrator
**Próximo passo:** Executar comandos abaixo no PowerShell do servidor

---

## 📋 INSTRUÇÕES

1. No servidor Windows, **clique direito no botão Iniciar**
2. Selecione **"Windows PowerShell (Admin)"**
3. Copie e cole os comandos abaixo **UM POR VEZ**

---

## 🔧 PASSO 1: Criar Estrutura de Diretórios (1 min)

```powershell
# Criar diretórios principais
New-Item -ItemType Directory -Path "C:\projetos","C:\certs","C:\temp","C:\backups","C:\logs","C:\chromedriver" -Force

# Verificar criação
Get-ChildItem C:\ -Directory | Where-Object {$_.Name -in @('projetos','certs','temp','backups','logs','chromedriver')}
```

**✅ Esperado:** Deve listar as 6 pastas criadas

---

## 🔧 PASSO 2: Configurar PowerShell ExecutionPolicy (30 seg)

```powershell
# Permitir execução de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Verificar
Get-ExecutionPolicy -Scope CurrentUser
```

**✅ Esperado:** `RemoteSigned`

---

## 🔧 PASSO 3: Clonar Repositório (2 min)

```powershell
# Navegar para C:\projetos
cd C:\projetos

# Clonar repositório
git clone https://github.com/revisaprecatorio/crawler_tjsp.git

# Verificar clonagem
if (Test-Path "C:\projetos\crawler_tjsp") {
    Write-Host "✅ Repositório clonado com sucesso!" -ForegroundColor Green
    Get-ChildItem C:\projetos\crawler_tjsp
} else {
    Write-Host "❌ Erro ao clonar repositório!" -ForegroundColor Red
}
```

**✅ Esperado:**
- Mensagem "✅ Repositório clonado com sucesso!"
- Lista de arquivos do projeto

**❌ Se Git não estiver instalado:**
```powershell
# Download Git
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe"
Invoke-WebRequest -Uri $gitUrl -OutFile "C:\temp\git-installer.exe"

# Instalar
Start-Process -FilePath "C:\temp\git-installer.exe" -Args "/VERYSILENT /NORESTART" -Wait

# Aguardar 30 segundos
Start-Sleep -Seconds 30

# Fechar e reabrir PowerShell, depois repetir o clone
```

---

## 🔧 PASSO 4: Executar Script de Setup Automático (60-90 min)

**⚠️ IMPORTANTE:** Este script vai instalar Python, Chrome, ChromeDriver e todas as dependências. Vai demorar!

```powershell
# Navegar para scripts
cd C:\projetos\crawler_tjsp\windows-server\scripts

# Executar setup completo
.\setup-complete.ps1
```

**O script vai:**
1. ⏳ Baixar e instalar Python 3.12.3 (~5 min)
2. ⏳ Baixar e instalar Git (se não instalado) (~5 min)
3. ⏳ Baixar e instalar Chrome (~5 min)
4. ⏳ Baixar ChromeDriver (~2 min)
5. ⏳ Criar venv e instalar dependências (~10 min)

**Total:** ~30-40 minutos de instalação automatizada

**✅ Ao final, o script mostrará:**
```
========================================
  ✅ SETUP CONCLUÍDO COM SUCESSO!
========================================

📋 Próximos Passos:
1. Transferir certificado .pfx para C:\certs\certificado.pfx
2. Importar certificado no Windows Certificate Store
3. Configurar arquivo .env
4. Testar autenticação
```

---

## 🔧 PASSO 5: Instalação Manual do Web Signer (10 min)

**Durante ou após o setup-complete.ps1, instale o Web Signer:**

1. **Abrir navegador no servidor Windows**
2. **Acessar:** https://websigner.softplan.com.br/downloads
3. **Baixar:** websigner-X.X.X-win64.exe (versão Windows)
4. **Executar instalador** (seguir wizard)
5. **Iniciar Web Signer** (ícone deve aparecer na bandeja do sistema)

**Verificar instalação:**
```powershell
# Verificar se Web Signer está instalado
$webSignerPath = "C:\Program Files\Softplan\WebSigner\websigner.exe"
if (Test-Path $webSignerPath) {
    Write-Host "✅ Web Signer instalado!" -ForegroundColor Green

    # Iniciar Web Signer
    Start-Process -FilePath $webSignerPath

    # Verificar processo
    Start-Sleep -Seconds 5
    Get-Process | Where-Object {$_.Name -like "*websigner*"}
} else {
    Write-Host "❌ Web Signer não encontrado!" -ForegroundColor Red
}
```

**✅ Esperado:** Ícone do Web Signer na bandeja do sistema (canto inferior direito)

---

## 🔧 PASSO 6: Transferir Certificado do Mac para Servidor (5 min)

**No seu Mac (NÃO no servidor):**

Você tem duas opções:

### Opção A: Arrastar e Soltar via RDP (MAIS FÁCIL)

1. **No Mac:** Localizar arquivo no Finder:
   ```
   /Users/persivalballeste/Documents/@IANIA/PROJECTS/revisa/revisa/2_Crawler/crawler_tjsp/25424636_pf.pfx
   ```

2. **Arrastar** o arquivo `25424636_pf.pfx` do Finder do Mac

3. **Soltar** no desktop do Windows Server (dentro da janela RDP)

4. **No servidor:** Mover arquivo para C:\certs\
   ```powershell
   # No PowerShell do servidor
   Move-Item -Path "C:\Users\Administrator\Desktop\25424636_pf.pfx" -Destination "C:\certs\certificado.pfx" -Force

   # Verificar
   Get-Item "C:\certs\certificado.pfx"
   ```

### Opção B: Via SCP (se preferir)

**No Mac (terminal local):**
```bash
scp /Users/persivalballeste/Documents/@IANIA/PROJECTS/revisa/revisa/2_Crawler/crawler_tjsp/25424636_pf.pfx Administrator@62.171.143.88:/certs/certificado.pfx
# Senha: 31032025
```

**✅ Verificar no servidor:**
```powershell
# No PowerShell do servidor
if (Test-Path "C:\certs\certificado.pfx") {
    Write-Host "✅ Certificado transferido!" -ForegroundColor Green
    Get-Item "C:\certs\certificado.pfx" | Select-Object Name, Length
} else {
    Write-Host "❌ Certificado não encontrado!" -ForegroundColor Red
}
```

---

## 🔧 PASSO 7: Importar Certificado no Windows (2 min)

**No servidor Windows (PowerShell):**

```powershell
# Importar certificado
$certPath = "C:\certs\certificado.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $certPassword

# Verificar importação
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*CPF*" -or $_.Subject -like "*517.648.902-30*"}

if ($cert) {
    Write-Host "✅ Certificado importado com sucesso!" -ForegroundColor Green
    Write-Host "Subject: $($cert.Subject)" -ForegroundColor Cyan
    Write-Host "Thumbprint: $($cert.Thumbprint)" -ForegroundColor Cyan
    Write-Host "Válido até: $($cert.NotAfter)" -ForegroundColor Cyan
} else {
    Write-Host "❌ Certificado não encontrado no Certificate Store!" -ForegroundColor Red
}
```

**✅ Validação visual:**
```powershell
# Abrir Certificate Manager
certmgr.msc
```

1. Expandir **"Personal"**
2. Clicar em **"Certificates"**
3. **Verificar:** Certificado com CPF 517.648.902-30 deve aparecer
4. **Verificar:** Ícone de chave (indica que tem chave privada)

---

## 🔧 PASSO 8: Configurar Arquivo .env (3 min)

```powershell
# Navegar para projeto
cd C:\projetos\crawler_tjsp

# Copiar template
Copy-Item .env.example .env

# Editar .env
notepad .env
```

**No Notepad, preencher:**

```ini
# PostgreSQL (ajustar depois se necessário)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=revisa_db
POSTGRES_USER=revisa_user
POSTGRES_PASSWORD=Rv!s@Pg2025#Cr@wl3r

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

# Selenium (deixar vazio para usar ChromeDriver local)
SELENIUM_REMOTE_URL=
```

**Salvar e fechar** (Ctrl+S, Alt+F4)

**Verificar:**
```powershell
# Verificar se .env foi criado
Get-Item .env

# Mostrar conteúdo (para conferir)
Get-Content .env
```

---

## 🔧 PASSO 9: TESTE DE AUTENTICAÇÃO (15 min) 🎯

**Este é o teste MAIS IMPORTANTE!** Se passar, a migração foi bem-sucedida!

```powershell
# Navegar para projeto
cd C:\projetos\crawler_tjsp

# Ativar virtual environment
.\venv\Scripts\Activate.ps1

# Executar teste de autenticação
python windows-server\scripts\test_authentication.py
```

**O que vai acontecer:**

1. ✅ Chrome abre via Selenium
2. ✅ e-SAJ carrega
3. ✅ Script clica em "Certificado Digital"
4. ✅ **WEB SIGNER ABRE MODAL DE SELEÇÃO** ← MOMENTO CRÍTICO!
5. ✅ Você seleciona o certificado manualmente
6. ✅ Login bem-sucedido!

**⚠️ IMPORTANTE:**
- Quando o modal do Web Signer aparecer, **SELECIONE O CERTIFICADO**
- O script aguarda 30 segundos para você selecionar
- Após seleção, aguarde o redirecionamento

**✅ SUCESSO - Você verá:**
```
========================================
✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO! ✅✅✅
========================================

🎉 RESULTADO DO TESTE: SUCESSO! 🎉
✅ Native Messaging Protocol funcionou corretamente!
✅ Web Signer comunicou com extensão Chrome!
✅ Autenticação via certificado digital operacional!
```

**📸 Screenshots salvos em:** `C:\projetos\crawler_tjsp\screenshots\`
**📝 Log detalhado em:** `C:\projetos\crawler_tjsp\logs\test_auth.log`

---

## 🎉 SE O TESTE PASSOU:

**PARABÉNS! BLOQUEIO RESOLVIDO!** 🎉🎉🎉

**Deploy #31: SUCESSO após 30 tentativas!**

**Próximos passos:**
1. Configurar PostgreSQL (local ou remoto)
2. Testar crawler_full.py com processo real
3. Configurar orchestrator como Windows Service
4. Iniciar produção!

---

## ❌ SE O TESTE FALHOU:

**Troubleshooting:**

1. **Verificar Web Signer rodando:**
   ```powershell
   Get-Process | Where-Object {$_.Name -like "*websigner*"}
   ```
   - Se não aparecer, iniciar: `Start-Process "C:\Program Files\Softplan\WebSigner\websigner.exe"`

2. **Verificar certificado importado:**
   ```powershell
   Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*CPF*"}
   ```

3. **Verificar extensão Chrome:**
   - Abrir Chrome manualmente
   - Ir para `chrome://extensions/`
   - Verificar se "Web Signer" está habilitada

4. **Teste manual:**
   - Abrir Chrome
   - Ir para https://esaj.tjsp.jus.br/esaj/portal.do
   - Clicar "Certificado Digital"
   - Verificar se modal abre

5. **Ver logs:**
   ```powershell
   Get-Content C:\projetos\crawler_tjsp\logs\test_auth.log -Tail 50
   ```

---

## 📞 Suporte

- **Documentação completa:** `C:\projetos\crawler_tjsp\windows-server\DEPLOYMENT_PLAN.md`
- **Checklist detalhado:** `C:\projetos\crawler_tjsp\windows-server\MIGRATION_CHECKLIST.md`
- **Credenciais:** `C:\projetos\crawler_tjsp\windows-server\CREDENTIALS.md`

---

**Última atualização:** 2025-10-04
**Executar a partir de:** Passo 1 (você já conectou via RDP ✅)
