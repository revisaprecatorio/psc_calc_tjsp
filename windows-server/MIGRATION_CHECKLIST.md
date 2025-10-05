# ✅ Checklist de Migração - Linux → Windows Server

**Projeto:** Crawler TJSP
**Data:** 2025-10-04
**Objetivo:** Resolver bloqueio do Native Messaging Protocol

---

## 📊 Status Geral

| Fase | Status | Tempo Estimado | Tempo Real | Responsável |
|------|--------|----------------|------------|-------------|
| 1. Setup Inicial | ✅ Concluído | 45 min | ~60 min | Persival |
| 2. Python & Git | ✅ Concluído | 40 min | ~50 min | Persival |
| 3. Chrome & Web Signer | ✅ Concluído | 60 min | ~90 min | Persival |
| 4. PostgreSQL | ⬜ Pendente | 30 min | - | - |
| 5. Deploy Código | ✅ Concluído | 45 min | ~30 min | Persival |
| 6. Testes | 🟡 Em Progresso | 60 min | - | - |
| 7. Produção | ⬜ Pendente | 30 min | - | - |

**Legenda:** ⬜ Pendente | 🟡 Em Progresso | ✅ Concluído | ❌ Bloqueado

---

## 🎯 Fase 1: Setup Inicial do Servidor

### 1.1 Recebimento de Credenciais
- [x] Email da Contabo recebido
- [x] IP anotado: `62.171.143.88`
- [x] Usuário anotado: `Administrator`
- [x] Senha inicial testada: ✅

### 1.2 Primeiro Acesso
- [x] RDP conectado com sucesso
- [x] Desktop Windows Server carregou
- [x] PowerShell abre como Administrator
- [x] Internet funcionando (`ping google.com`)

### 1.3 Segurança Básica
- [x] Senha do Administrator mantida (31032025)
- [x] Nova senha anotada em CREDENTIALS.md (protegido)
- [ ] Windows Firewall configurado
- [x] RDP acessível externamente

### 1.4 SSH (Opcional)
- [x] OpenSSH Server instalado (v9.5.0.0p1-Beta)
- [x] Porta 22 liberada no firewall
- [x] SSH testado do computador local
- [x] SCP funciona (certificado transferido com sucesso)

### 1.5 Configurações do Sistema
- [ ] Timezone configurado (Brasília GMT-3)
- [ ] Windows Updates instalados
- [ ] Servidor reiniciado após updates
- [x] Estrutura de pastas criada (`C:\projetos`, `C:\certs`, `C:\temp`)

### 1.6 Backup
- [ ] Snapshot inicial criado na Contabo
- [ ] Nome do snapshot: `initial-clean-windows-YYYY-MM-DD`

**Documentação:** [setup/01_initial_server_setup.md](setup/01_initial_server_setup.md)

---

## 🐍 Fase 2: Python e Dependências

### 2.1 Python 3.12
- [x] Python 3.12.3 baixado
- [x] Instalação concluída
- [x] `python --version` retorna 3.12.x
- [x] Python no PATH do sistema

### 2.2 pip e Ferramentas
- [x] pip atualizado para última versão
- [x] virtualenv instalado
- [x] wheel e setuptools instalados

### 2.3 Git
- [x] Git para Windows instalado (manual via TLS 1.2)
- [x] `git --version` funciona
- [x] Git configurado (nome e email)

### 2.4 Build Tools
- [x] Visual C++ Build Tools instalado
- [x] psycopg2-binary instalado com sucesso
- [x] cryptography instalado com sucesso

### 2.5 Virtual Environment
- [x] venv criado em `C:\projetos\crawler_tjsp\.venv`
- [x] venv ativado com sucesso
- [x] `python` aponta para venv

### 2.6 Dependências Básicas
- [x] requirements.txt presente no repositório
- [x] selenium instalado
- [x] psycopg2-binary instalado
- [x] requests instalado
- [x] python-dotenv instalado
- [x] Todos os imports funcionam

**Documentação:** [setup/02_python_installation.md](setup/02_python_installation.md)

---

## 🌐 Fase 3: Chrome, ChromeDriver e Web Signer

### 3.1 Google Chrome
- [x] Chrome Enterprise baixado
- [x] Instalação concluída
- [x] Chrome em `C:\Program Files\Google\Chrome\Application\chrome.exe`
- [x] Versão do Chrome anotada: `131.0.6778.86`

### 3.2 ChromeDriver
- [x] Versão compatível identificada
- [x] ChromeDriver baixado
- [x] Instalado em `C:\chromedriver\chromedriver.exe`
- [x] ChromeDriver no PATH
- [x] `chromedriver --version` funciona

### 3.3 Web Signer
- [x] Web Signer baixado do site oficial
- [x] Instalação concluída
- [x] Web Signer em `C:\Program Files\Softplan\WebSigner\`
- [x] Web Signer rodando (ícone na bandeja)

### 3.4 Certificado Digital
- [x] Certificado .pfx transferido para servidor (via SCP)
- [x] Salvo em `C:\certs\certificado.pfx` (3421 bytes)
- [x] Importado no Windows Certificate Store
- [x] Certificado visível em `certmgr.msc` → Personal
- [x] Certificado tem chave privada associada

### 3.5 Configuração Web Signer
- [x] Web Signer reconhece certificado
- [x] Teste manual: modal de seleção abre
- [x] Login manual com certificado bem-sucedido

### 3.6 Extensão Chrome
- [x] Extensão Web Signer instalada (Chrome Web Store)
- [x] Extensão habilitada em `chrome://extensions/`
- [x] Extensão instalada no perfil sincronizado `revisa.precatorio@gmail.com`
- [x] Ícone da extensão aparece na toolbar

### 3.7 Testes de Integração
- [x] Teste manual via Chrome: login com certificado OK
- [x] **DESCOBERTA CRÍTICA**: Chrome sincronizado com perfil Google
- [x] **SOLUÇÃO**: Script Selenium deve usar perfil padrão (não user-data-dir customizado)

**Documentação:** [setup/03_chrome_websigner.md](setup/03_chrome_websigner.md)

---

## 🗄️ Fase 4: PostgreSQL (Opcional - pode usar banco remoto)

### 4.1 Decisão de Arquitetura
- [ ] Decidido: PostgreSQL local OU remoto
- [ ] Se remoto: credenciais de acesso anotadas

### 4.2 PostgreSQL Local (se aplicável)
- [ ] PostgreSQL 15 baixado
- [ ] Instalação concluída
- [ ] Senha do usuário postgres configurada
- [ ] Serviço rodando (`Get-Service postgresql-x64-15`)
- [ ] Porta 5432 listening

### 4.3 Database e Usuário
- [ ] Database `revisa_db` criado
- [ ] Usuário `revisa_user` criado
- [ ] Permissões concedidas
- [ ] Conexão testada: `psql -U revisa_user -d revisa_db -h localhost`

### 4.4 Tabela de Jobs
- [ ] Tabela `consultas_esaj` criada
- [ ] Schema correto (id, processo_numero, status, created_at, updated_at, etc.)
- [ ] Índices criados

**Documentação:** DEPLOYMENT_PLAN.md (Fase 4)

---

## 📦 Fase 5: Deploy do Código

### 5.1 Clonar Repositório
- [x] Repositório clonado em `C:\projetos\crawler_tjsp`
- [x] Branch `main` ativa
- [x] Todos os arquivos presentes

### 5.2 Configurar .env
- [x] `.env` criado em `C:\projetos\crawler_tjsp\.env`
- [x] Variáveis preenchidas:
  - [x] `CERT_PATH=C:\certs\certificado.pfx`
  - [x] `CERT_PASSWORD=903205`
  - [x] `CERT_CPF=517.648.902-30`
  - [x] `CHROME_BINARY_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe`
  - [x] `CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe`
  - [ ] `POSTGRES_HOST` (aguardando decisão de banco)
  - [ ] Demais variáveis PostgreSQL

### 5.3 Instalar Dependências
- [x] `pip install -r requirements.txt` concluído
- [x] Todos os pacotes instalados sem erros
- [x] `pip list` mostra todas as dependências

### 5.4 Adaptar Código para Windows
- [x] Script de teste `test_authentication.py` criado
- [x] **CORREÇÃO CRÍTICA**: Removido `--user-data-dir` customizado
- [x] **SOLUÇÃO**: Selenium agora usa perfil padrão do Chrome (com Web Signer)
- [x] Paths Windows configurados corretamente
- [x] Imports funcionam sem erros

**Documentação:** DEPLOYMENT_PLAN.md (Fase 4)

---

## 🧪 Fase 6: Testes de Validação

### 6.1 Teste Chrome + Selenium
- [ ] Script `test_chrome_windows.py` criado
- [ ] Chrome abre via Selenium
- [ ] Google carrega corretamente
- [ ] Screenshot salvo
- [ ] Chrome fecha sem erros

### 6.2 Teste Web Signer + Extensão
- [ ] Script `test_websigner_extension.py` criado
- [ ] Extensão carrega em `chrome://extensions/`
- [ ] Web Signer mostra ícone verde (ativo)
- [ ] e-SAJ abre corretamente

### 6.3 Teste Autenticação com Certificado (CRÍTICO)
- [ ] Script `test_esaj_auth.py` criado
- [ ] e-SAJ abre
- [ ] Botão "Certificado Digital" clicado
- [ ] Web Signer abre modal de seleção
- [ ] Certificado selecionado
- [ ] **LOGIN BEM-SUCEDIDO** ✅✅✅
- [ ] Screenshot `login_success.png` salvo
- [ ] URL após login: `https://esaj.tjsp.jus.br/esaj/portal.do?servico=...`

### 6.4 Teste Crawler Completo
- [ ] `crawler_full.py` executado manualmente
- [ ] Login com certificado funciona
- [ ] Processo de teste localizado e extraído
- [ ] JSON de saída gerado
- [ ] Logs sem erros críticos

**Documentação:** DEPLOYMENT_PLAN.md (Fase 5)

---

## 🔄 Fase 7: Worker e Produção

### 7.1 Teste Orchestrator
- [ ] `orchestrator_subprocess.py` rodando em foreground
- [ ] Conecta ao PostgreSQL
- [ ] Lê jobs da tabela `consultas_esaj`
- [ ] Processa job de teste
- [ ] Chama `crawler_full.py` via subprocess
- [ ] Atualiza status no banco

### 7.2 Configurar Windows Service
- [ ] NSSM ou Task Scheduler configurado
- [ ] Serviço/Tarefa criado: "CrawlerTJSP"
- [ ] Configurado para iniciar no boot
- [ ] Logs configurados (`C:\projetos\crawler_tjsp\logs\`)

### 7.3 Teste Auto-start
- [ ] Servidor reiniciado
- [ ] Serviço inicia automaticamente
- [ ] Logs sendo gerados
- [ ] Jobs processados após reboot

### 7.4 Monitoramento
- [ ] Logs rotativos configurados (10 MB, 5 backups)
- [ ] Script de status criado (`status_crawler.py`)
- [ ] Alertas configurados (email/webhook) - opcional

### 7.5 Backup
- [ ] Auto-backup da Contabo habilitado
- [ ] Script de backup manual criado (`backup.ps1`)
- [ ] Backup agendado semanalmente (Task Scheduler)
- [ ] Teste de restore bem-sucedido

### 7.6 Documentação de Manutenção
- [ ] Procedimentos documentados em `docs/maintenance.md`
- [ ] Troubleshooting documentado
- [ ] Comandos comuns listados

**Documentação:** DEPLOYMENT_PLAN.md (Fase 6 e 7)

---

## 🎉 Fase 8: Go-Live

### 8.1 Pré-Produção
- [ ] Todos os testes passaram
- [ ] Autenticação com certificado 100% funcional
- [ ] Orchestrator processa jobs corretamente
- [ ] Serviço configurado para auto-start
- [ ] Backup configurado
- [ ] Snapshot pré-produção criado

### 8.2 Produção
- [ ] Jobs reais inseridos na fila
- [ ] Monitoramento ativo por 2-4 horas
- [ ] Taxa de sucesso > 95%
- [ ] Dados extraídos validados
- [ ] Sistema estável

### 8.3 Pós-Deployment
- [ ] DEPLOY_TRACKING.md atualizado (Deploy #31)
- [ ] DIAGNOSTIC_REPORT.md atualizado (solução final)
- [ ] README.md atualizado (status: ✅ OPERACIONAL)
- [ ] Stakeholders notificados
- [ ] Celebrar sucesso! 🎉

---

## 📈 Métricas de Sucesso

| Métrica | Meta | Resultado Real | Status |
|---------|------|----------------|--------|
| Login com Certificado | > 98% | ___ % | ⬜ |
| Tempo Médio por Job | < 2 min | ___ min | ⬜ |
| Uptime do Serviço | > 99% | ___ % | ⬜ |
| Erros por Dia | < 5 | ___ erros | ⬜ |
| Jobs Processados/Dia | > 100 | ___ jobs | ⬜ |

---

## 🚨 Blockers e Riscos

### Blockers Identificados
| # | Descrição | Severidade | Status | Responsável | Solução |
|---|-----------|------------|--------|-------------|---------|
| 1 | - | - | ⬜ | - | - |

### Riscos Ativos
| Risco | Probabilidade | Impacto | Mitigação | Status |
|-------|--------------|---------|-----------|--------|
| Licença Windows expirar | Baixa | Alto | Contabo gerencia | ⬜ |
| Performance inferior | Média | Médio | Monitorar recursos | ⬜ |
| Vulnerabilidades | Média | Alto | Windows Updates automáticos | ⬜ |

---

## 📝 Notas e Observações

### Anotações durante a migração:

```
Data: _____________
Hora: _____________
Nota: _____________________________________________
____________________________________________________
____________________________________________________
```

### Lições Aprendidas:

```
1. Chrome sincronizado com Google Account não cria diretório local de perfil
2. PowerShell Start-Process sem --user-data-dir abre perfil padrão correto
3. Selenium com --user-data-dir customizado cria perfil novo SEM extensões
4. Solução: USAR --user-data-dir + --profile-directory=Default (não remover!)
5. NUNCA usar --load-extension com perfis sincronizados (cria perfil temporário)
6. chrome://version é fonte confiável para descobrir Profile Path
7. Chrome manual aberto BLOQUEIA Selenium (DevToolsActivePort error)
8. Sempre fechar Chrome antes de executar testes Selenium
9. Sessão autenticada PERSISTE no perfil Default (ganho de performance)
10. OpenSSH no Windows Server 2016 requer instalação manual (v9.5.0.0p1-Beta)
11. Git no Windows Server 2016 requer TLS 1.2 habilitado para download
```

### Desvios do Plano:

```
Item: ______________________________________________
Razão: _____________________________________________
Impacto: ___________________________________________
```

---

## 📞 Contatos de Suporte

| Recurso | Contato | Observações |
|---------|---------|-------------|
| Contabo Support | https://contabo.com/support | Problemas com VPS |
| Softplan Web Signer | https://websigner.softplan.com.br | Problemas com certificado |
| Equipe Interna | - | - |

---

## ✅ Assinatura de Conclusão

**Migração concluída por:** `___________________`
**Data:** `___________________`
**Horário:** `___________________`
**Status Final:** ✅ Sucesso / ❌ Falha / 🟡 Parcial

**Observações finais:**
```
____________________________________________________
____________________________________________________
____________________________________________________
```

---

**Última atualização:** 2025-10-04
**Versão:** 1.0
**Status:** Pronto para execução
