# 💾 Guia Completo de Backup - Windows Server 2016 → 2025

**Data:** 2025-10-06  
**Servidor:** Contabo Cloud VPS 10 (62.171.143.88)  
**Objetivo:** Fazer backup completo antes de upgrade para Windows Server 2025  
**Tempo Estimado:** 45-60 minutos  

---

## 📋 Sumário Executivo

Este guia documenta o processo completo de backup do Windows Server 2016 configurado com o Crawler TJSP, garantindo que:

✅ **Zero perda de dados**  
✅ **Todas as configurações preservadas**  
✅ **Restore rápido em caso de problemas**  
✅ **Documentação completa do estado atual**  

---

## 🎯 O Que Será Feito Backup

### 1. Infraestrutura
- ✅ Snapshot completo do servidor (via Contabo)
- ✅ Imagem do disco inteiro

### 2. Código e Configurações
- ✅ Repositório Git (`C:\projetos\crawler_tjsp`)
- ✅ Virtual environment Python (`.venv`)
- ✅ Arquivo `.env` com todas as variáveis
- ✅ Logs existentes

### 3. Certificado Digital
- ✅ Arquivo `.pfx` (`C:\certs\certificado.pfx`)
- ✅ Export do certificado do Windows Certificate Store
- ✅ Chave privada e pública

### 4. Software Instalado
- ✅ Chrome + versão exata
- ✅ ChromeDriver + versão
- ✅ Web Signer + configuração
- ✅ Python 3.12 + pacotes
- ✅ Git para Windows
- ✅ OpenSSH Server

### 5. Configurações do Sistema
- ✅ Variáveis de ambiente PATH
- ✅ Serviços configurados
- ✅ Firewall rules
- ✅ Perfil Chrome sincronizado
- ✅ Extensões instaladas

### 6. Banco de Dados (se local)
- ✅ PostgreSQL data directory
- ✅ Dump SQL completo
- ✅ Configuração `pg_hba.conf`

---

## 🚀 Plano de Execução

### **ORDEM RECOMENDADA:**

```
1. Criar Snapshot na Contabo (5 min) ← PRIMEIRO!
2. Executar script de backup automático (10 min)
3. Exportar certificado digital (5 min)
4. Documentar configurações manuais (15 min)
5. Fazer backup PostgreSQL (5 min, se aplicável)
6. Upload para local seguro (10 min)
7. Validar backups (10 min)
```

---

## 📸 ETAPA 1: Snapshot do Servidor na Contabo

### Por Que Fazer Isso PRIMEIRO?

🔴 **CRÍTICO:** Snapshot captura o estado EXATO do servidor. Se algo der errado durante o backup manual, você pode voltar para este ponto.

### Como Fazer:

#### Via Painel Web Contabo:
1. Acesse: https://my.contabo.com
2. Login com suas credenciais
3. Navegue até "Cloud VPS"
4. Selecione o servidor `62.171.143.88`
5. Clique em "Snapshots" → "Create Snapshot"
6. **Nome sugerido:** `pre-upgrade-to-ws2025-2025-10-06`
7. **Descrição:** `Backup completo antes de upgrade Windows Server 2016 → 2025. Crawler TJSP em Fase 5 (testes). Chrome 131.0.6778.86, Web Signer OK, certificado A1 instalado.`
8. Aguardar conclusão (pode levar 10-20 minutos)

#### Via API Contabo (opcional):
```bash
# Se tiver API token configurado
curl -X POST https://api.contabo.com/v1/compute/instances/{instanceId}/snapshots \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pre-upgrade-to-ws2025-2025-10-06",
    "description": "Backup completo antes de upgrade para Windows Server 2025"
  }'
```

### Validação:
- [ ] Snapshot aparece na lista de snapshots
- [ ] Status: "Completed"
- [ ] Tamanho: ~20-40 GB (depende do uso)
- [ ] Data/hora: 2025-10-06

### ⚠️ IMPORTANTE:
> O snapshot da Contabo é seu **SEGURO TOTAL**. Se tudo falhar no upgrade, você pode restaurar o servidor exatamente como está agora. **NÃO PULE ESTA ETAPA!**

---

## 💻 ETAPA 2: Backup Automático via PowerShell

### Script de Backup Completo

Criamos um script PowerShell que automatiza todo o processo:

**Localização:** `C:\projetos\crawler_tjsp\scripts\backup_complete_system.ps1`

### Execução:

```powershell
# 1. Conectar via RDP ao servidor
# IP: 62.171.143.88
# User: Administrator
# Pass: 31032025

# 2. Abrir PowerShell como Administrator

# 3. Navegar para o diretório
cd C:\projetos\crawler_tjsp

# 4. Executar script de backup
.\scripts\backup_complete_system.ps1
```

### O Que o Script Faz:

1. **Cria estrutura de backup timestamped:**
   ```
   C:\backups\backup_2025-10-06_HHMMSS\
   ├── 01_sistema\
   ├── 02_codigo\
   ├── 03_certificados\
   ├── 04_chrome_profile\
   ├── 05_logs\
   ├── 06_database\
   └── BACKUP_MANIFEST.txt
   ```

2. **Captura informações do sistema:**
   - Versão do Windows
   - Pacotes Python instalados
   - Versões de software
   - Variáveis de ambiente
   - Serviços configurados
   - Firewall rules

3. **Copia arquivos críticos:**
   - Código completo do projeto
   - Certificado digital
   - Perfil Chrome (se local)
   - Logs existentes

4. **Gera documentação:**
   - Lista completa de software instalado
   - Configurações de rede
   - Estrutura de diretórios

5. **Compacta tudo:**
   - Arquivo `.zip` final
   - Hash MD5 para validação

### Saída Esperada:

```
✅ Backup iniciado: 2025-10-06 14:30:00
📁 Criando estrutura de diretórios...
📋 Capturando informações do sistema...
📦 Copiando código do projeto...
🔐 Fazendo backup do certificado...
🌐 Exportando perfil Chrome...
📊 Copiando logs...
🗄️ Fazendo backup PostgreSQL (se aplicável)...
📝 Gerando manifesto...
🗜️ Compactando backup...
✅ Backup concluído: C:\backups\backup_2025-10-06_143000.zip
📊 Tamanho: 2.3 GB
🔐 MD5: a3f5e8d9c2b1a4f6e7d8c9b0a1f2e3d4
⏱️ Tempo total: 8 minutos
```

---

## 🔐 ETAPA 3: Exportar Certificado Digital

### 3.1 Export do Windows Certificate Store

```powershell
# Script: export_certificado.ps1

# Abrir Certificate Manager
certmgr.msc

# OU via PowerShell:

# 1. Listar certificados
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}

# 2. Exportar certificado com chave privada
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
$password = ConvertTo-SecureString -String "903205" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "C:\backups\certificado_backup.pfx" -Password $password

# 3. Exportar certificado público (CER)
Export-Certificate -Cert $cert -FilePath "C:\backups\certificado_public.cer"

Write-Host "✅ Certificado exportado com sucesso!"
Write-Host "   - Chave privada (.pfx): C:\backups\certificado_backup.pfx"
Write-Host "   - Chave pública (.cer): C:\backups\certificado_public.cer"
```

### 3.2 Validação do Certificado

```powershell
# Verificar integridade do certificado exportado
$certPath = "C:\backups\certificado_backup.pfx"
$certPassword = ConvertTo-SecureString -String "903205" -Force -AsPlainText

$testCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($certPath, $certPassword)

Write-Host "📋 Informações do Certificado Exportado:"
Write-Host "   Subject: $($testCert.Subject)"
Write-Host "   Issuer: $($testCert.Issuer)"
Write-Host "   Valid From: $($testCert.NotBefore)"
Write-Host "   Valid Until: $($testCert.NotAfter)"
Write-Host "   Thumbprint: $($testCert.Thumbprint)"
Write-Host "   Has Private Key: $($testCert.HasPrivateKey)"

if ($testCert.HasPrivateKey -eq $false) {
    Write-Host "⚠️ AVISO: Certificado NÃO contém chave privada!"
} else {
    Write-Host "✅ Certificado OK: Chave privada presente"
}
```

### Checklist:
- [ ] Arquivo `.pfx` exportado
- [ ] Tamanho: ~3-5 KB
- [ ] Arquivo `.cer` exportado (público)
- [ ] Validação: `HasPrivateKey = True`
- [ ] Cópia adicional em `C:\certs\certificado.pfx` intacta

---

## 📝 ETAPA 4: Documentar Configurações Manuais

### 4.1 Extensões do Chrome

```powershell
# Script: export_chrome_extensions.ps1

$profilePath = "C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default"
$extensionsPath = Join-Path $profilePath "Extensions"

if (Test-Path $extensionsPath) {
    Get-ChildItem $extensionsPath | ForEach-Object {
        Write-Host "📦 Extensão: $($_.Name)"
        
        # Tentar ler manifest.json
        $manifestPath = Get-ChildItem -Path $_.FullName -Recurse -Filter "manifest.json" | Select-Object -First 1
        if ($manifestPath) {
            $manifest = Get-Content $manifestPath.FullName -Raw | ConvertFrom-Json
            Write-Host "   Nome: $($manifest.name)"
            Write-Host "   Versão: $($manifest.version)"
        }
    }
} else {
    Write-Host "⚠️ Perfil Chrome não encontrado localmente (pode estar sincronizado)"
}

# Documentar manualmente
Write-Host "`n📋 Extensões Instaladas (documentar manualmente):"
Write-Host "1. Abrir Chrome"
Write-Host "2. Ir para chrome://extensions/"
Write-Host "3. Anotar TODAS as extensões instaladas"
Write-Host "4. Especialmente: Web Signer (ID, versão)"
```

### Template de Documentação:

```markdown
## Extensões Chrome Instaladas (2025-10-06)

Perfil: revisa.precatorio@gmail.com

| Extensão | ID | Versão | Ativa | Notas |
|----------|----|----|------|-------|
| Web Signer | [ID] | [versão] | Sim | CRÍTICO - autenticação certificado |
| [Outras] | ... | ... | ... | ... |
```

### 4.2 Variáveis de Ambiente

```powershell
# Exportar variáveis de ambiente do sistema
$envVars = @{
    "PATH" = $env:Path
    "PYTHONPATH" = $env:PYTHONPATH
    "CHROME_BINARY_PATH" = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    "CHROMEDRIVER_PATH" = "C:\chromedriver\chromedriver.exe"
    "WEBSIGNER_PATH" = "C:\Program Files\Softplan\WebSigner\websigner.exe"
}

$envVars | ConvertTo-Json | Out-File "C:\backups\environment_variables.json"

Write-Host "✅ Variáveis de ambiente exportadas"
```

### 4.3 Serviços Configurados

```powershell
# Listar serviços customizados
Get-Service | Where-Object {$_.DisplayName -like "*Crawler*" -or $_.DisplayName -like "*TJSP*"} | 
    Format-Table Name, DisplayName, Status, StartType

# Listar tarefas agendadas
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Crawler*" -or $_.TaskName -like "*TJSP*"} |
    Format-Table TaskName, State, LastRunTime, NextRunTime
```

### 4.4 Firewall Rules

```powershell
# Exportar regras de firewall relevantes
Get-NetFirewallRule | Where-Object {
    $_.DisplayName -like "*RDP*" -or 
    $_.DisplayName -like "*SSH*" -or 
    $_.DisplayName -like "*PostgreSQL*" -or
    $_.DisplayName -like "*Chrome*"
} | Select-Object DisplayName, Direction, Action, Enabled, LocalPort | 
    Export-Csv "C:\backups\firewall_rules.csv" -NoTypeInformation

Write-Host "✅ Regras de firewall exportadas"
```

---

## 🗄️ ETAPA 5: Backup PostgreSQL (Se Local)

### 5.1 Verificar Se PostgreSQL Está Instalado

```powershell
Get-Service | Where-Object {$_.Name -like "*postgresql*"}
```

### 5.2 Fazer Dump do Banco

```powershell
# Se PostgreSQL estiver instalado localmente

$pgBinPath = "C:\Program Files\PostgreSQL\15\bin"
$backupPath = "C:\backups\postgresql"
New-Item -ItemType Directory -Path $backupPath -Force

# Backup completo
& "$pgBinPath\pg_dumpall.exe" -U postgres -f "$backupPath\all_databases_backup.sql"

# Backup específico do crawler
& "$pgBinPath\pg_dump.exe" -U revisa_user -d revisa_db -f "$backupPath\revisa_db_backup.sql"

# Backup do arquivo de configuração
Copy-Item "C:\Program Files\PostgreSQL\15\data\postgresql.conf" "$backupPath\postgresql.conf"
Copy-Item "C:\Program Files\PostgreSQL\15\data\pg_hba.conf" "$backupPath\pg_hba.conf"

Write-Host "✅ Backup PostgreSQL concluído"
```

### 5.3 Validar Backup do Banco

```powershell
# Verificar tamanho do dump
Get-ChildItem "C:\backups\postgresql\*.sql" | Format-Table Name, Length, LastWriteTime

# Verificar conteúdo (primeiras linhas)
Get-Content "C:\backups\postgresql\revisa_db_backup.sql" -Head 50
```

---

## 📤 ETAPA 6: Upload para Local Seguro

### 6.1 Compactar Backup Final

```powershell
# Criar arquivo ZIP final
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupDir = "C:\backups\backup_$timestamp"
$zipFile = "C:\backups\BACKUP_COMPLETO_PRE_UPGRADE_$timestamp.zip"

Compress-Archive -Path $backupDir -DestinationPath $zipFile -CompressionLevel Optimal

# Calcular hash
$hash = Get-FileHash $zipFile -Algorithm MD5
Write-Host "📦 Backup compactado: $zipFile"
Write-Host "📊 Tamanho: $((Get-Item $zipFile).Length / 1GB) GB"
Write-Host "🔐 MD5: $($hash.Hash)"

# Salvar hash em arquivo
$hash.Hash | Out-File "$zipFile.md5"
```

### 6.2 Transferir Backup para Computador Local

#### Opção A: Via SCP (Recomendado)

```bash
# Do seu Mac/Linux local
scp Administrator@62.171.143.88:"C:/backups/BACKUP_COMPLETO_PRE_UPGRADE_*.zip" ~/Downloads/

# Verificar hash
md5 ~/Downloads/BACKUP_COMPLETO_PRE_UPGRADE_*.zip
```

#### Opção B: Via RDP (Arrastar e Soltar)

1. Conectar via RDP
2. Navegar até `C:\backups\`
3. Arrastar arquivo `.zip` para seu computador local
4. Aguardar transferência (pode levar 10-30 min dependendo do tamanho)

#### Opção C: Upload para Cloud Storage

```powershell
# Exemplo: Upload para Google Drive / Dropbox via CLI
# (requer instalação de cliente)

# Ou usar API do Google Drive:
# https://developers.google.com/drive/api/v3/quickstart/python
```

### 6.3 Validar Transferência

```bash
# No computador local
# Verificar tamanho do arquivo
ls -lh ~/Downloads/BACKUP_COMPLETO_PRE_UPGRADE_*.zip

# Verificar hash MD5
md5sum ~/Downloads/BACKUP_COMPLETO_PRE_UPGRADE_*.zip

# Comparar com hash do servidor
# Devem ser IDÊNTICOS!
```

---

## ✅ ETAPA 7: Validação Final do Backup

### Checklist de Validação:

```markdown
## 📋 Checklist de Validação de Backup

### Infraestrutura
- [ ] Snapshot Contabo criado
- [ ] Snapshot status: "Completed"
- [ ] Nome snapshot anotado: _______________________

### Arquivos
- [ ] ZIP final criado
- [ ] Tamanho: _______ GB
- [ ] Hash MD5 calculado: _______________________
- [ ] Transferido para computador local
- [ ] Hash MD5 validado (local == servidor)

### Conteúdo do Backup
- [ ] Código: `C:\projetos\crawler_tjsp\` ✅
- [ ] `.env` presente e completo ✅
- [ ] Certificado `.pfx` exportado ✅
- [ ] Virtual environment `.venv` ✅
- [ ] Logs copiados ✅
- [ ] Documentação de extensões Chrome ✅
- [ ] Variáveis de ambiente exportadas ✅
- [ ] Firewall rules exportadas ✅
- [ ] PostgreSQL dump (se aplicável) ✅

### Certificado Digital
- [ ] Arquivo `.pfx` presente
- [ ] Tamanho: ~3-5 KB
- [ ] Arquivo `.cer` (público) presente
- [ ] Validação: HasPrivateKey = True ✅
- [ ] Senha anotada: 903205 ✅

### Documentação
- [ ] `BACKUP_MANIFEST.txt` gerado
- [ ] Lista de software instalado
- [ ] Versões documentadas:
  - [ ] Windows Server 2016
  - [ ] Python 3.12.3
  - [ ] Chrome 131.0.6778.86
  - [ ] ChromeDriver (versão compatível)
  - [ ] Web Signer (versão)
  - [ ] Git (versão)

### Armazenamento Seguro
- [ ] Backup em computador local: ~/Downloads/
- [ ] Backup em cloud storage (opcional)
- [ ] Backup em HD externo (recomendado)
- [ ] Backup em múltiplos locais (crítico!)

### Testes de Integridade
- [ ] ZIP pode ser descompactado sem erros
- [ ] Certificado pode ser importado em máquina de teste
- [ ] `.env` é legível e completo
- [ ] SQL dump (se aplicável) é válido

### Documentação de Restore
- [ ] `RESTORE_GUIDE.md` criado
- [ ] Instruções de restore via Snapshot
- [ ] Instruções de restore manual
- [ ] Checklist de pós-restore
```

---

## 🔄 ETAPA 8: Criar Documentação de Restore

### O Que Fazer Se Precisar Voltar Atrás

Criamos um guia separado: `RESTORE_GUIDE.md`

**Conteúdo resumido:**

1. **Restore via Snapshot Contabo (mais rápido)**
   - Painel → Snapshots → Restore
   - Tempo: 10-20 minutos
   - Estado: EXATAMENTE como estava

2. **Restore Manual (se necessário)**
   - Instalar Windows Server 2025
   - Executar `restore_from_backup.ps1`
   - Importar certificado
   - Instalar software
   - Restaurar código e configurações

---

## 📊 Tempo Total Estimado

| Etapa | Tempo | Crítico |
|-------|-------|---------|
| 1. Snapshot Contabo | 10-20 min | 🔴 SIM |
| 2. Script backup automático | 10 min | 🔴 SIM |
| 3. Export certificado | 5 min | 🔴 SIM |
| 4. Documentar configurações | 15 min | 🟡 Recomendado |
| 5. Backup PostgreSQL | 5 min | 🟢 Se aplicável |
| 6. Upload para local seguro | 10-30 min | 🔴 SIM |
| 7. Validação final | 10 min | 🔴 SIM |
| **TOTAL** | **45-90 min** | |

---

## 🎯 Próximos Passos Após Backup

### DEPOIS de completar TODO este guia:

1. ✅ **Validar que todos os checkboxes estão marcados**
2. ✅ **Confirmar que backup está em local seguro**
3. ✅ **Anotar snapshot ID da Contabo**
4. ✅ **Fazer segunda cópia do backup (redundância)**
5. ✅ **Testar restore do certificado em outra máquina**
6. 🚀 **Proceder com upgrade para Windows Server 2025**

### Ao Fazer Upgrade:

```markdown
## Plano de Upgrade

1. **Pré-upgrade:**
   - [ ] Backup completo CONCLUÍDO ✅
   - [ ] Snapshot Contabo ATIVO ✅
   - [ ] Backup transferido para local seguro ✅

2. **Durante upgrade:**
   - [ ] Usar licença Windows Server 2025
   - [ ] Fazer upgrade in-place (preserva dados)
   - [ ] OU: Instalação limpa + restore manual

3. **Pós-upgrade:**
   - [ ] Validar que Chrome/Python/Git ainda funcionam
   - [ ] Reinstalar Web Signer (nova versão se necessário)
   - [ ] Reimportar certificado digital
   - [ ] Testar autenticação no e-SAJ
   - [ ] Executar `test_authentication.py`
   - [ ] Criar novo snapshot: "post-upgrade-ws2025"
```

---

## ⚠️ AVISOS IMPORTANTES

### 🔴 NÃO PROSSIGA COM UPGRADE SEM:
1. Snapshot Contabo criado e validado
2. Backup ZIP transferido para local seguro
3. Hash MD5 validado (local == servidor)
4. Certificado exportado e testado
5. Todos os checkboxes deste guia marcados

### 🟡 RECOMENDAÇÕES:
1. Fazer backup em MÚLTIPLOS locais:
   - Computador local
   - Google Drive / Dropbox
   - HD externo
   - Outro servidor (redundância)

2. Não deletar snapshot antigo após upgrade:
   - Manter snapshot por pelo menos 7 dias
   - Só deletar após confirmar que Windows Server 2025 está 100% operacional

3. Testar restore ANTES de fazer upgrade:
   - Criar VM de teste
   - Fazer restore do certificado
   - Validar que `.env` está completo
   - Confirmar que código funciona

---

## 📞 Suporte

**Em caso de dúvidas:**
- Documentação Contabo Snapshots: https://contabo.com/en/support/snapshots
- Windows Server Backup: https://learn.microsoft.com/windows-server/administration/windows-server-backup/windows-server-backup-overview
- Este projeto: `RESTORE_GUIDE.md`

---

## ✅ Assinatura de Conclusão de Backup

**Backup realizado por:** `___________________`  
**Data:** `___________________`  
**Horário:** `___________________`  
**Snapshot ID Contabo:** `___________________`  
**Backup ZIP transferido:** ☐ Sim ☐ Não  
**Hash MD5 validado:** ☐ Sim ☐ Não  
**Pronto para upgrade:** ☐ Sim ☐ Não  

**Observações:**
```
___________________________________________________
___________________________________________________
___________________________________________________
```

---

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Status:** Pronto para execução  
**Responsável:** Persival Balleste

