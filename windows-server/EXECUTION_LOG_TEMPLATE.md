# 📝 Log de Execução - Migração Windows Server

**Servidor:** Contabo Cloud VPS 10 (62.171.143.88)
**Data de início:** ___________
**Responsável:** ___________

---

## 📊 Status Geral

| Item | Status | Data/Hora | Observações |
|------|--------|-----------|-------------|
| Acesso RDP | ⬜ | | |
| Script setup-complete.ps1 | ⬜ | | |
| Web Signer instalado | ⬜ | | |
| Certificado importado | ⬜ | | |
| Teste de autenticação | ⬜ | | |
| PostgreSQL configurado | ⬜ | | |
| Crawler testado | ⬜ | | |
| Orchestrator configurado | ⬜ | | |
| Produção iniciada | ⬜ | | |

**Legenda:** ⬜ Pendente | 🟡 Em Progresso | ✅ Concluído | ❌ Falha

---

## 1️⃣ Fase 1: Acesso Inicial (Target: 30 min)

### 1.1 Primeiro Acesso via RDP
**Início:** ___:___
**Fim:** ___:___
**Status:** ⬜

**Checklist:**
- [ ] RDP conectado ao IP 62.171.143.88
- [ ] Usuário Administrator logado
- [ ] Desktop Windows Server carregou
- [ ] PowerShell abre como Administrator
- [ ] Internet funcionando (ping google.com)

**Problemas encontrados:**
```
_______________________________________________________________
_______________________________________________________________
```

**Solução aplicada:**
```
_______________________________________________________________
_______________________________________________________________
```

---

### 1.2 Alterar Senha do Administrator
**Data/Hora:** ___________
**Status:** ⬜

**Nova senha definida:** [Anotar em local seguro, NÃO aqui]

---

### 1.3 Criar Estrutura de Diretórios
**Data/Hora:** ___________
**Status:** ⬜

```powershell
# Comando executado:
New-Item -ItemType Directory -Path "C:\projetos","C:\certs","C:\temp","C:\backups","C:\logs" -Force
```

**Resultado:**
```
_______________________________________________________________
```

---

## 2️⃣ Fase 2: Setup Automático (Target: 90 min)

### 2.1 Executar setup-complete.ps1
**Início:** ___:___
**Fim:** ___:___
**Status:** ⬜

**Script executado:**
```powershell
cd C:\projetos\crawler_tjsp\windows-server\scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\setup-complete.ps1
```

**Log de saída:**
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

**Componentes instalados:**
- [ ] Python 3.12.3 → Versão: ___________
- [ ] Git → Versão: ___________
- [ ] Google Chrome → Versão: ___________
- [ ] ChromeDriver → Versão: ___________
- [ ] Repositório clonado em C:\projetos\crawler_tjsp
- [ ] Virtual environment criado
- [ ] Dependências instaladas

**Problemas:**
```
_______________________________________________________________
_______________________________________________________________
```

---

### 2.2 Instalação Manual do Web Signer
**Data/Hora:** ___________
**Status:** ⬜

**URL de download:** https://websigner.softplan.com.br/downloads
**Versão instalada:** ___________

**Checklist:**
- [ ] Arquivo baixado: websigner-___-win64.exe
- [ ] Instalação concluída
- [ ] Web Signer instalado em C:\Program Files\Softplan\WebSigner\
- [ ] Web Signer iniciado (ícone na bandeja)
- [ ] Processo websigner.exe rodando (Task Manager)

**Problemas:**
```
_______________________________________________________________
```

---

## 3️⃣ Fase 3: Certificado Digital (Target: 15 min)

### 3.1 Transferir Certificado
**Data/Hora:** ___________
**Status:** ⬜
**Método usado:** [ ] RDP arrastar/soltar  [ ] SCP  [ ] Outro: _______

**Checklist:**
- [ ] Arquivo 25424636_pf.pfx transferido
- [ ] Salvo em C:\certs\certificado.pfx
- [ ] Tamanho do arquivo: _______ KB

---

### 3.2 Importar Certificado
**Data/Hora:** ___________
**Status:** ⬜

**Comando usado:**
```powershell
$cert = ConvertTo-SecureString '903205' -AsPlainText -Force
Import-PfxCertificate -FilePath C:\certs\certificado.pfx -CertStoreLocation Cert:\CurrentUser\My -Password $cert
```

**Resultado:**
```
_______________________________________________________________
```

**Validação:**
- [ ] Certificado aparece em certmgr.msc → Personal → Certificates
- [ ] Subject contém CPF: 517.648.902-30
- [ ] Certificado tem chave privada (ícone de chave)
- [ ] Data de validade: ___________

**Thumbprint do certificado:** ___________________________________

---

### 3.3 Configurar Web Signer
**Data/Hora:** ___________
**Status:** ⬜

**Checklist:**
- [ ] Web Signer detecta certificado
- [ ] Certificado aparece na lista do Web Signer
- [ ] Teste manual: abrir Chrome → e-SAJ → Certificado Digital → Modal abre

---

## 4️⃣ Fase 4: Configuração .env (Target: 5 min)

**Data/Hora:** ___________
**Status:** ⬜

**Arquivo criado:** C:\projetos\crawler_tjsp\.env

**Variáveis configuradas:**
- [ ] POSTGRES_HOST = ___________
- [ ] POSTGRES_PORT = 5432
- [ ] POSTGRES_DB = ___________
- [ ] POSTGRES_USER = ___________
- [ ] POSTGRES_PASSWORD = [DEFINIDA]
- [ ] CHROME_BINARY_PATH = C:\Program Files\Google\Chrome\Application\chrome.exe
- [ ] CHROMEDRIVER_PATH = C:\chromedriver\chromedriver.exe
- [ ] CERT_PATH = C:\certs\certificado.pfx
- [ ] CERT_PASSWORD = 903205

---

## 5️⃣ Fase 5: Teste de Autenticação (Target: 15 min)

### 5.1 Executar test_authentication.py
**Data/Hora:** ___________
**Status:** ⬜

**Comando:**
```powershell
cd C:\projetos\crawler_tjsp
.\venv\Scripts\Activate.ps1
python windows-server\scripts\test_authentication.py
```

**Resultado:**
```
[  ] ✅ SUCESSO - Login com certificado funcionou!
[  ] ❌ FALHA - Teste não passou
```

**Detalhes:**
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

**Screenshots gerados:**
- [ ] 01_esaj_homepage_[timestamp].png
- [ ] 02_after_click_cert_[timestamp].png
- [ ] 03_login_success_[timestamp].png (se sucesso)
- [ ] 04_login_failed_[timestamp].png (se falha)

**Log completo:** C:\projetos\crawler_tjsp\logs\test_auth.log

**Se FALHA, descrever problema:**
```
_______________________________________________________________
_______________________________________________________________
```

**Se SUCESSO:**
🎉 **Native Messaging Protocol FUNCIONOU!** 🎉

---

## 6️⃣ Fase 6: PostgreSQL (Target: 30 min)

**Data/Hora:** ___________
**Status:** ⬜
**Opção escolhida:** [ ] Local  [ ] Remoto

### Se Local:
**Versão instalada:** PostgreSQL ___________

**Database criado:**
```sql
CREATE DATABASE revisa_db;
CREATE USER revisa_user WITH PASSWORD '___________';
GRANT ALL PRIVILEGES ON DATABASE revisa_db TO revisa_user;
```

**Teste de conexão:**
```powershell
psql -U revisa_user -d revisa_db -h localhost
```

**Resultado:** [ ] ✅ Conectou  [ ] ❌ Erro

### Se Remoto:
**Host:** ___________
**Porta:** ___________
**Teste de conexão:** [ ] ✅ OK  [ ] ❌ Falha

---

## 7️⃣ Fase 7: Teste do Crawler (Target: 20 min)

**Data/Hora:** ___________
**Status:** ⬜

**Comando:**
```powershell
python crawler_full.py --debug --processo=1234567-89.2020.8.26.0100
```

**Resultado:**
```
_______________________________________________________________
_______________________________________________________________
```

**Checklist:**
- [ ] Crawler iniciou sem erros
- [ ] Login com certificado funcionou
- [ ] Processo foi localizado
- [ ] Dados foram extraídos
- [ ] JSON de saída gerado
- [ ] Logs sem erros críticos

---

## 8️⃣ Fase 8: Orchestrator (Target: 40 min)

### 8.1 Teste Manual do Orchestrator
**Data/Hora:** ___________
**Status:** ⬜

**Comando:**
```powershell
python orchestrator_subprocess.py
```

**Resultado:**
```
_______________________________________________________________
```

**Checklist:**
- [ ] Conectou ao PostgreSQL
- [ ] Leu jobs da fila
- [ ] Processou job de teste
- [ ] Atualizou status no banco

---

### 8.2 Configurar Windows Service (NSSM)
**Data/Hora:** ___________
**Status:** ⬜

**Comandos:**
```powershell
C:\nssm\nssm-2.24\win64\nssm.exe install CrawlerTJSP "C:\projetos\crawler_tjsp\venv\Scripts\python.exe" "C:\projetos\crawler_tjsp\orchestrator_subprocess.py"
C:\nssm\nssm-2.24\win64\nssm.exe set CrawlerTJSP AppDirectory "C:\projetos\crawler_tjsp"
C:\nssm\nssm-2.24\win64\nssm.exe start CrawlerTJSP
```

**Resultado:**
```
_______________________________________________________________
```

**Checklist:**
- [ ] Serviço CrawlerTJSP criado
- [ ] Serviço iniciado com sucesso
- [ ] Logs sendo gerados em C:\projetos\crawler_tjsp\logs\

**Teste de auto-start:**
- [ ] Servidor reiniciado
- [ ] Serviço iniciou automaticamente após boot

---

## 9️⃣ Fase 9: Produção (Target: 30 min)

### 9.1 Inserir Jobs Reais
**Data/Hora:** ___________
**Status:** ⬜

**Quantidade de jobs inseridos:** ___________

```sql
-- Exemplo de insert
INSERT INTO consultas_esaj (processo_numero, status, created_at)
VALUES ('1234567-89.2020.8.26.0100', 'pending', NOW());
```

---

### 9.2 Monitoramento (Primeiras 2 horas)
**Início:** ___:___
**Fim:** ___:___

| Hora | Jobs Processados | Sucessos | Falhas | Observações |
|------|------------------|----------|--------|-------------|
| ___:___ | ___ | ___ | ___ | |
| ___:___ | ___ | ___ | ___ | |
| ___:___ | ___ | ___ | ___ | |
| ___:___ | ___ | ___ | ___ | |

**Taxa de sucesso:** _____ % (Meta: > 95%)

**Problemas identificados:**
```
_______________________________________________________________
_______________________________________________________________
```

---

### 9.3 Criar Snapshot de Produção
**Data/Hora:** ___________
**Status:** ⬜

**Nome do snapshot:** production-ready-2025-10-04

**Checklist:**
- [ ] Acessou painel Contabo: https://my.contabo.com
- [ ] Navegou para Cloud VPS → Snapshots
- [ ] Snapshot criado com sucesso
- [ ] Snapshot aparece na lista

---

## 🎉 Finalização

### Métricas Finais

| Métrica | Meta | Resultado | Status |
|---------|------|-----------|--------|
| Taxa de Sucesso Login | > 98% | ___% | ⬜ |
| Tempo Médio por Job | < 2 min | ___ min | ⬜ |
| Jobs Processados/Hora | > 30 | ___ | ⬜ |

---

### Checklist Final

- [ ] Todos os testes passaram
- [ ] Autenticação com certificado funcionando 100%
- [ ] Orchestrator processando jobs automaticamente
- [ ] Serviço configurado para auto-start
- [ ] Logs rotativos configurados
- [ ] Backup/snapshot criado
- [ ] Documentação atualizada (DEPLOY_TRACKING.md, README.md)

---

### Tempo Total de Migração

**Início:** ___________
**Fim:** ___________
**Duração total:** _______ horas

**Estimado:** 8-12 horas
**Real:** _______ horas

---

### Lições Aprendidas

```
1. _____________________________________________________________
2. _____________________________________________________________
3. _____________________________________________________________
```

---

### Próximos Passos

```
1. _____________________________________________________________
2. _____________________________________________________________
3. _____________________________________________________________
```

---

### Assinatura

**Migração concluída por:** ___________________________
**Data:** ___________
**Status Final:** [ ] ✅ Sucesso  [ ] ⚠️ Parcial  [ ] ❌ Falha

**Observações finais:**
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

---

**🎉 FIM DO LOG DE EXECUÇÃO 🎉**
