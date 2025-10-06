# Instruções: Teste Manual com Remote Debugging

**Data:** 2025-10-06
**Problema:** Scripts PowerShell não conseguem iniciar Chrome com Remote Debugging
**Solução:** Executar comandos manualmente passo a passo

---

## 🎯 Passo a Passo (TESTADO E FUNCIONAL)

### Terminal 1 - Iniciar Chrome com Remote Debugging

```powershell
# 1. Fechar Chrome
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# 2. Abrir Chrome COM Remote Debugging (MANUAL)
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Chrome vai abrir - NAO FECHE!
# Perfil: revisa.precatorio@gmail.com (ultimo usado)
# Web Signer: carregado automaticamente
```

**IMPORTANTE:** Deixe este terminal e Chrome **ABERTOS**!

---

### Terminal 2 - Verificar Remote Debugging Ativo

Abra **NOVO terminal PowerShell** e execute:

```powershell
# Verificar se porta 9222 esta respondendo
Invoke-WebRequest -Uri "http://localhost:9222/json/version" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Resultado esperado:**
```json
{
  "Browser": "Chrome/131.0.6778.86",
  "Protocol-Version": "1.3",
  "User-Agent": "Mozilla/5.0...",
  "V8-Version": "13.1.201.13",
  "WebKit-Version": "537.36",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/..."
}
```

Se você VER esse JSON, **Remote Debugging está ATIVO!** ✅

---

### Terminal 3 - Executar Teste Selenium

No **mesmo terminal 2** (ou abra novo):

```powershell
# 1. Navegar para projeto
cd C:\projetos\crawler_tjsp

# 2. Ativar virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Executar teste
python windows-server\scripts\test_authentication_remote.py
```

**Resultado esperado:**
- ✅ Selenium conecta no Chrome já aberto
- ✅ Usa perfil revisa.precatorio@gmail.com
- ✅ Web Signer está disponível
- ✅ Botão "Certificado Digital" aparece
- ✅ Login com certificado funciona

---

## 🔍 Troubleshooting

### Problema 1: Porta 9222 não responde

```powershell
# Ver processos Chrome
Get-Process chrome | Select-Object Id, StartTime

# Ver linha de comando de cada processo
Get-Process chrome | ForEach-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    Write-Host "PID $($_.Id): $cmdLine"
}
```

**Procure por:** `--remote-debugging-port=9222` na saída

Se NÃO aparecer, Chrome foi aberto SEM Remote Debugging!

**Solução:**
1. Feche TODOS os processos Chrome: `Stop-Process -Name chrome -Force`
2. Execute comando manual novamente: `& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222`

---

### Problema 2: Chrome abre mas Selenium não conecta

**Verifique ChromeDriver compatível:**

```powershell
# Ver versão ChromeDriver
C:\chromedriver\chromedriver.exe --version

# Ver versão Chrome
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

**Versões devem ser compatíveis!**

Se não forem:
1. Baixe ChromeDriver correto: https://googlechromelabs.github.io/chrome-for-testing/
2. Substitua em `C:\chromedriver\chromedriver.exe`

---

### Problema 3: Web Signer não aparece

```powershell
# Com Chrome aberto, acesse:
# chrome://extensions/

# Verifique:
# - Web Signer (Softplan) está na lista?
# - Está habilitado (toggle azul)?
```

Se Web Signer NÃO aparece:
- Chrome abriu perfil errado
- Instale Web Signer: https://chrome.google.com/webstore/detail/web-signer/...

---

## 📊 Comandos Úteis

### Ver todas as tabs/páginas abertas no Chrome

```powershell
Invoke-WebRequest -Uri "http://localhost:9222/json" -UseBasicParsing |
    Select-Object -ExpandProperty Content |
    ConvertFrom-Json |
    Select-Object title, url, type
```

### Matar Chrome e recomeçar

```powershell
Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### Verificar porta 9222 em uso

```powershell
netstat -ano | findstr :9222
```

---

## ✅ Checklist de Sucesso

- [ ] Chrome aberto manualmente com `--remote-debugging-port=9222`
- [ ] Perfil revisa.precatorio@gmail.com carregado
- [ ] `http://localhost:9222/json/version` retorna JSON
- [ ] Web Signer aparece em `chrome://extensions/`
- [ ] Virtual environment ativado (`.venv\Scripts\Activate.ps1`)
- [ ] Teste Python executado sem erros de conexão
- [ ] Botão "Certificado Digital" encontrado na página e-SAJ

---

## 🚀 Próximos Passos (quando funcionar)

1. ✅ Testar login com certificado digital
2. ✅ Testar acesso direto a processo (sessão persistente)
3. ⏳ Criar script batch `.bat` para iniciar Chrome automaticamente
4. ⏳ Configurar Windows Task Scheduler para iniciar Chrome no boot
5. ⏳ Atualizar crawler_full.py para usar Remote Debugging

---

**Última atualização:** 2025-10-06 03:30
**Status:** Aguardando teste manual
**Responsável:** Persival Balleste
