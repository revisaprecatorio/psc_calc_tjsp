# ✅ Checklist de Migração - Linux → Windows Server

**Projeto:** Crawler TJSP
**Data:** 2025-10-04
**Objetivo:** Resolver bloqueio do Native Messaging Protocol

---

## 📊 Status Geral

| Fase | Status | Tempo Estimado | Tempo Real | Responsável |
|------|--------|----------------|------------|-------------|
| 1. Setup Inicial | ⬜ Pendente | 45 min | - | - |
| 2. Python & Git | ⬜ Pendente | 40 min | - | - |
| 3. Chrome & Web Signer | ⬜ Pendente | 60 min | - | - |
| 4. PostgreSQL | ⬜ Pendente | 30 min | - | - |
| 5. Deploy Código | ⬜ Pendente | 45 min | - | - |
| 6. Testes | ⬜ Pendente | 60 min | - | - |
| 7. Produção | ⬜ Pendente | 30 min | - | - |

**Legenda:** ⬜ Pendente | 🟡 Em Progresso | ✅ Concluído | ❌ Bloqueado

---

## 🎯 Fase 1: Setup Inicial do Servidor

### 1.1 Recebimento de Credenciais
- [ ] Email da Contabo recebido
- [ ] IP anotado: `___________________`
- [ ] Usuário anotado: `___________________`
- [ ] Senha inicial testada: ✅ / ❌

### 1.2 Primeiro Acesso
- [ ] RDP conectado com sucesso
- [ ] Desktop Windows Server carregou
- [ ] PowerShell abre como Administrator
- [ ] Internet funcionando (`ping google.com`)

### 1.3 Segurança Básica
- [ ] Senha do Administrator alterada
- [ ] Nova senha anotada em local seguro
- [ ] Windows Firewall configurado
- [ ] RDP acessível externamente

### 1.4 SSH (Opcional)
- [ ] OpenSSH Server instalado
- [ ] Porta 22 liberada no firewall
- [ ] SSH testado do computador local
- [ ] SCP funciona (teste de transferência)

### 1.5 Configurações do Sistema
- [ ] Timezone configurado (Brasília GMT-3)
- [ ] Windows Updates instalados
- [ ] Servidor reiniciado após updates
- [ ] Estrutura de pastas criada (`C:\projetos`, `C:\certs`, `C:\temp`, `C:\backups`)

### 1.6 Backup
- [ ] Snapshot inicial criado na Contabo
- [ ] Nome do snapshot: `initial-clean-windows-YYYY-MM-DD`

**Documentação:** [setup/01_initial_server_setup.md](setup/01_initial_server_setup.md)

---

## 🐍 Fase 2: Python e Dependências

### 2.1 Python 3.12
- [ ] Python 3.12.3 baixado
- [ ] Instalação concluída
- [ ] `python --version` retorna 3.12.x
- [ ] Python no PATH do sistema

### 2.2 pip e Ferramentas
- [ ] pip atualizado para última versão
- [ ] virtualenv instalado
- [ ] wheel e setuptools instalados

### 2.3 Git
- [ ] Git para Windows instalado
- [ ] `git --version` funciona
- [ ] Git configurado (nome e email)

### 2.4 Build Tools
- [ ] Visual C++ Build Tools instalado
- [ ] psycopg2-binary instalado com sucesso
- [ ] cryptography instalado com sucesso

### 2.5 Virtual Environment
- [ ] venv criado em `C:\projetos\crawler_tjsp\venv`
- [ ] venv ativado com sucesso
- [ ] `python` aponta para venv

### 2.6 Dependências Básicas
- [ ] requirements.txt criado
- [ ] selenium instalado
- [ ] psycopg2-binary instalado
- [ ] requests instalado
- [ ] python-dotenv instalado
- [ ] Todos os imports funcionam

**Documentação:** [setup/02_python_installation.md](setup/02_python_installation.md)

---

## 🌐 Fase 3: Chrome, ChromeDriver e Web Signer

### 3.1 Google Chrome
- [ ] Chrome Enterprise baixado
- [ ] Instalação concluída
- [ ] Chrome em `C:\Program Files\Google\Chrome\Application\chrome.exe`
- [ ] Versão do Chrome anotada: `___________________`

### 3.2 ChromeDriver
- [ ] Versão compatível identificada
- [ ] ChromeDriver baixado
- [ ] Instalado em `C:\chromedriver\chromedriver.exe`
- [ ] ChromeDriver no PATH
- [ ] `chromedriver --version` funciona

### 3.3 Web Signer
- [ ] Web Signer baixado do site oficial
- [ ] Instalação concluída
- [ ] Web Signer em `C:\Program Files\Softplan\WebSigner\`
- [ ] Web Signer rodando (ícone na bandeja)

### 3.4 Certificado Digital
- [ ] Certificado .pfx transferido para servidor
- [ ] Salvo em `C:\certs\certificado.pfx`
- [ ] Importado no Windows Certificate Store
- [ ] Certificado visível em `certmgr.msc` → Personal
- [ ] Certificado tem chave privada associada

### 3.5 Configuração Web Signer
- [ ] Web Signer reconhece certificado
- [ ] Teste manual: modal de seleção abre
- [ ] Login manual com certificado bem-sucedido

### 3.6 Extensão Chrome
- [ ] Extensão Web Signer instalada (Chrome Web Store ou local)
- [ ] Extensão habilitada em `chrome://extensions/`
- [ ] Ícone da extensão aparece na toolbar

### 3.7 Testes de Integração
- [ ] Teste manual via Chrome: login com certificado OK
- [ ] Teste Selenium básico: Chrome abre via script Python
- [ ] Screenshot de teste salvo

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
- [ ] Repositório clonado em `C:\projetos\crawler_tjsp`
- [ ] Branch `main` ativa
- [ ] Todos os arquivos presentes

### 5.2 Configurar .env
- [ ] `.env` criado a partir de `.env.example`
- [ ] Variáveis preenchidas:
  - [ ] `POSTGRES_HOST`
  - [ ] `POSTGRES_PORT`
  - [ ] `POSTGRES_DB`
  - [ ] `POSTGRES_USER`
  - [ ] `POSTGRES_PASSWORD`
  - [ ] `CHROME_BINARY_PATH`
  - [ ] `CHROMEDRIVER_PATH`
  - [ ] `CERT_PATH`
  - [ ] `CERT_PASSWORD`

### 5.3 Instalar Dependências
- [ ] `pip install -r requirements.txt` concluído
- [ ] Todos os pacotes instalados sem erros
- [ ] `pip list` mostra todas as dependências

### 5.4 Adaptar Código para Windows
- [ ] `crawler_full.py`: paths Windows (barras invertidas)
- [ ] `orchestrator_subprocess.py`: paths ajustados
- [ ] User data directory: `C:\temp\chrome-profile`
- [ ] Download directory: `C:\projetos\crawler_tjsp\downloads`
- [ ] Imports funcionam sem erros

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
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________
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
