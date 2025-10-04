# 🪟 Migração para Windows Server - Crawler TJSP

**Data de Início:** 2025-10-04
**Status:** 🟡 Planejamento
**Servidor:** Contabo Cloud VPS 10

---

## 📋 Especificações do Servidor

### Hardware
- **CPU:** 3 vCPU Cores
- **RAM:** 8 GB
- **Storage:** 75 GB NVMe + 150 GB SSD
- **Região:** European Union
- **Backup:** Auto Backup habilitado
- **Transferência:** 32 TB Out + Unlimited In

### Sistema Operacional
- **OS:** Windows Server 2016 Datacenter
- **Snapshot:** 1 disponível

### Custo Estimado
- **Mensal:** ~€9-15 (R$50-80)
- **Anual:** ~€108-180 (R$600-1.000)

---

## 🎯 Objetivo da Migração

**Resolver o bloqueio do Native Messaging Protocol** que impede a autenticação via certificado digital no ambiente Linux headless.

### Por Que Windows Server?

✅ **Native Messaging funciona nativamente**
- ChromeDriver executa Chrome em modo desktop
- Web Signer se comunica com extensão sem restrições
- Selenium mantém controle total do browser

✅ **Solução já validada**
- Evidências do DEPLOY_TRACKING.md mostram que funciona via RDP
- Login manual bem-sucedido (Deploy #30)
- Mesma arquitetura do ambiente de desenvolvimento

✅ **Custo-benefício otimizado**
- Tier 1: Solução definitiva e de baixo custo
- Sem dependências de serviços terceiros
- Total controle sobre infraestrutura

---

## 📁 Estrutura deste Diretório

```
windows-server/
├── README.md                          # Este arquivo
├── DEPLOYMENT_PLAN.md                 # Plano detalhado de deploy
├── setup/
│   ├── 01_initial_server_setup.md    # Configuração inicial (RDP, SSH, firewall)
│   ├── 02_python_installation.md     # Python 3.12 + pip + virtualenv
│   ├── 03_chrome_websigner.md        # Chrome + Web Signer + Certificado
│   ├── 04_postgresql.md              # PostgreSQL 15 instalação e setup
│   └── 05_crawler_deployment.md      # Deploy do crawler + worker
├── scripts/
│   ├── install_python.ps1            # Script PowerShell instalação Python
│   ├── install_chrome.ps1            # Script instalação Chrome
│   ├── install_postgresql.ps1        # Script instalação PostgreSQL
│   ├── setup_firewall.ps1            # Configuração firewall
│   ├── install_dependencies.ps1      # pip install requirements.txt
│   └── start_services.ps1            # Iniciar crawler + orchestrator
└── docs/
    ├── windows_vs_linux.md           # Comparativo de arquitetura
    ├── troubleshooting.md            # Troubleshooting específico Windows
    └── security_hardening.md         # Hardening de segurança

```

---

## 🚀 Roadmap de Implementação

### Fase 1: Preparação do Servidor (1-2 horas)
- [ ] Receber credenciais de acesso da Contabo
- [ ] Configurar RDP (Remote Desktop Protocol)
- [ ] Configurar SSH (OpenSSH Server no Windows)
- [ ] Configurar Windows Firewall
- [ ] Criar snapshot inicial
- [ ] Habilitar Auto Backup

### Fase 2: Instalação de Dependências (2-3 horas)
- [ ] Instalar Python 3.12.x
- [ ] Instalar Git para Windows
- [ ] Instalar Google Chrome
- [ ] Instalar Web Signer (Softplan)
- [ ] Instalar PostgreSQL 15
- [ ] Configurar variáveis de ambiente

### Fase 3: Configuração de Certificado (30 min)
- [ ] Transferir certificado A1 (.pfx) via SCP
- [ ] Importar certificado no Windows Certificate Store
- [ ] Configurar Web Signer com certificado
- [ ] Validar conexão extensão ↔ Web Signer

### Fase 4: Deploy do Crawler (1-2 horas)
- [ ] Clonar repositório via Git
- [ ] Criar virtualenv Python
- [ ] Instalar dependências (requirements.txt)
- [ ] Configurar .env com credenciais PostgreSQL
- [ ] Adaptar código para Windows (paths, services)
- [ ] Testar crawler_full.py manualmente

### Fase 5: Teste de Autenticação (30 min)
- [ ] Executar teste de login com certificado
- [ ] Validar Native Messaging funcionando
- [ ] Screenshot de login bem-sucedido
- [ ] Log de autenticação capturado

### Fase 6: Configuração do Worker (1 hora)
- [ ] Configurar orchestrator_subprocess.py
- [ ] Criar Windows Service para orchestrator
- [ ] Configurar auto-start no boot
- [ ] Testar processamento de fila

### Fase 7: Produção e Monitoramento (1 hora)
- [ ] Configurar logs (rotação automática)
- [ ] Configurar alertas (email/webhook)
- [ ] Documentar procedimentos de manutenção
- [ ] Realizar backup completo
- [ ] Iniciar operação em produção

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Licença Windows Server expirar | Baixa | Alto | Contabo gerencia licenciamento |
| Performance inferior ao Linux | Média | Médio | Monitorar uso de recursos, escalar se necessário |
| Custos de manutenção maiores | Baixa | Médio | Auto-backup reduz custos operacionais |
| Vulnerabilidades de segurança | Média | Alto | Hardening + Windows Updates automáticos |
| Incompatibilidade de bibliotecas Python | Baixa | Médio | Selenium e psycopg2 têm suporte oficial Windows |

---

## 📊 Comparativo: Linux vs Windows

| Aspecto | Linux (Atual) | Windows Server (Proposto) |
|---------|---------------|---------------------------|
| Native Messaging | ❌ Não funciona | ✅ Funciona |
| Custo Mensal | €5-10 | €9-15 |
| Manutenção | Complexa | Moderada |
| Debugging | Difícil (headless) | Fácil (RDP visual) |
| Estabilidade Selenium | Baixa | Alta |
| Suporte Web Signer | Não oficial | Oficial |
| Auto-scaling | Fácil | Moderado |

---

## 📚 Referências

- [DIAGNOSTIC_REPORT.md](../DIAGNOSTIC_REPORT.md) - Análise completa das 30 tentativas
- [DEPLOY_TRACKING.md](../DEPLOY_TRACKING.md) - Histórico detalhado de deploys
- [Windows Server 2016 Documentation](https://learn.microsoft.com/en-us/windows-server/)
- [Selenium on Windows](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)
- [Python on Windows](https://docs.python.org/3/using/windows.html)

---

## 🤝 Próximos Passos

1. **Aguardar credenciais da Contabo** (email com IP, usuário, senha)
2. **Executar Fase 1** seguindo [setup/01_initial_server_setup.md](setup/01_initial_server_setup.md)
3. **Reportar progresso** atualizando este README
4. **Documentar desvios** do plano original

---

**Última atualização:** 2025-10-04
**Responsável:** Equipe Revisa Precatório
**Status:** Aguardando credenciais Contabo
