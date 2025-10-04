# 🏛️ Crawler TJSP - Sistema de Consulta de Precatórios

Sistema automatizado para consulta e download de documentos de processos judiciais (Precatórios) no portal e-SAJ do Tribunal de Justiça de São Paulo (TJSP).

[![Status](https://img.shields.io/badge/status-bloqueado-red)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![Selenium](https://img.shields.io/badge/selenium-4.25-green)]()
[![License](https://img.shields.io/badge/license-proprietary-orange)]()

---

## ⚠️ **STATUS ATUAL**

🔴 **PROJETO BLOQUEADO** - Requer decisão estratégica

O projeto está **tecnicamente funcional** mas **bloqueado** por limitação do Native Messaging Protocol em ambiente headless Linux. Veja [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) para análise completa e alternativas.

**Última atualização:** 2025-10-04
**Iterações de deploy:** 30
**Próximo passo:** Migração para Windows Server (recomendado)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Status do Projeto](#-status-do-projeto)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Documentação](#-documentação)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)

---

## 🎯 Visão Geral

O **Crawler TJSP** automatiza o processo de:
1. Autenticação no e-SAJ via certificado digital A1
2. Busca de processos por CPF/CNPJ ou número CNJ
3. Extração de metadados processuais
4. Download de PDFs da Pasta Digital
5. Gerenciamento de filas via PostgreSQL

### Componentes Principais

```
┌─────────────────────────────────────────────────┐
│  crawler_full.py (Selenium WebDriver)           │
│  └─ Automação de navegação e download           │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  orchestrator_subprocess.py (Worker)            │
│  └─ Gerencia filas e executa crawler            │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  PostgreSQL Database                             │
│  └─ Tabela: consultas_esaj                      │
└─────────────────────────────────────────────────┘
```

### Casos de Uso

- ✅ Consulta de processos por **CPF/CNPJ**
- ✅ Consulta por **Número CNJ** (formato: 0000000-00.0000.0.00.0000)
- ✅ Download automático de PDFs
- ✅ Processamento em lote
- ✅ Modo TURBO (download acelerado)
- ✅ Fallback HTTP para downloads

---

## 🚨 Status do Projeto

### Situação Atual

| Componente | Status | Observação |
|------------|--------|------------|
| **Código Crawler** | ✅ Funcional | Testado e validado |
| **Orquestrador** | ✅ Funcional | Worker daemon operacional |
| **PostgreSQL** | ✅ Funcional | Integração completa |
| **Xvfb + ChromeDriver** | ✅ Configurado | Display virtual funcionando |
| **Certificado A1** | ✅ Importado | NSS database configurado |
| **Web Signer** | ❌ **BLOQUEADO** | Native Messaging não funciona |
| **Autenticação e-SAJ** | ❌ **BLOQUEADO** | Dependente do Web Signer |

### Problema Técnico

**Native Messaging Protocol não funciona em Linux headless via Selenium.**

Mesmo com todas as configurações corretas:
- ✅ Extensão Chrome carregada
- ✅ Web Signer instalado e rodando
- ✅ Certificado importado no NSS database
- ✅ Manifesto configurado

A comunicação entre extensão e executável nativo **NUNCA ocorre** quando Chrome é controlado via ChromeDriver.

**Detalhes:** Veja análise técnica completa em [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)

### Soluções Propostas

| Solução | Confiabilidade | Custo/mês | Tempo Setup | Recomendação |
|---------|---------------|-----------|-------------|--------------|
| **Windows Server** | ⭐⭐⭐⭐⭐ | $9-30 | 3-4h | **✅ RECOMENDADO** |
| **Legal Wizard** | ⭐⭐⭐⭐⭐ | R$50-200 | Imediato | ✅ Alternativa |
| **Ubuntu + XFCE** | ⭐⭐ | $5-20 | 6-8h | ⚠️ Risco alto |
| **Debug WebSocket** | ⭐⭐ | $5-20 | 40-80h | ❌ Não recomendado |

**Decisão recomendada:** Migrar para **Windows Server EC2** (AWS).

---

## 🏗️ Arquitetura

### Diagrama Completo

```
┌────────────────────────────────────────────────────────┐
│                PostgreSQL Database                      │
│              (consultas_esaj table)                     │
└───────────────────────┬────────────────────────────────┘
                        │ SELECT status=false
                        ▼
┌────────────────────────────────────────────────────────┐
│          orchestrator_subprocess.py                     │
│  ┌────────────────────────────────────────────────┐   │
│  │ 1. Busca jobs pendentes no banco               │   │
│  │ 2. Para cada processo na fila:                 │   │
│  │    └─> Executa: python crawler_full.py         │   │
│  │ 3. Atualiza status=true após sucesso           │   │
│  │ 4. Loop contínuo (daemon)                      │   │
│  └────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────┘
                        │ subprocess.run(crawler_full.py)
                        ▼
┌────────────────────────────────────────────────────────┐
│                crawler_full.py                          │
│  ┌────────────────────────────────────────────────┐   │
│  │ 1. Inicializa Chrome (Selenium)                │   │
│  │ 2. Acessa e-SAJ (https://esaj.tjsp.jus.br)     │   │
│  │ 3. Autenticação CAS:                           │   │
│  │    └─> Certificado digital A1 (PRIORIDADE)    │   │
│  │    └─> CPF/Senha (fallback)                    │   │
│  │ 4. Preenche formulário de consulta             │   │
│  │ 5. Aguarda resultado (lista ou detalhe)        │   │
│  │ 6. Extrai metadados do processo                │   │
│  │ 7. Abre Pasta Digital (se --abrir-autos)       │   │
│  │ 8. Seleciona documentos (jstree)               │   │
│  │ 9. Baixa PDF (se --baixar-pdf):                │   │
│  │    └─> Modo TURBO (via JavaScript)             │   │
│  │    └─> Modo Normal (aguarda árvore)            │   │
│  │    └─> Fallback HTTP (se Chrome falhar)        │   │
│  │ 10. Retorna JSON com resultados                │   │
│  └────────────────────────────────────────────────┘   │
└───────────────────────┬────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│                  Saída de Dados                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ downloads/{cpf}/processo_*.pdf                 │   │
│  │ screenshots/screenshot_*.png                   │   │
│  │ screenshots/erro_*.html, erro_*.png            │   │
│  │ STDOUT: JSON com metadados                     │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### Arquitetura Atual (Linux - BLOQUEADA)

```
VPS Ubuntu 24.04 (srv987902)
├── Xvfb :99 (Display Virtual)
├── ChromeDriver :4444 (Standalone)
├── Web Signer 2.12.1 (Instalado mas NÃO funciona)
├── Certificado A1 (Importado no NSS database)
├── Worker Docker (network_mode: host)
└── PostgreSQL (Externo: 72.60.62.124)

⚠️ BLOQUEIO: Native Messaging não funciona via Selenium
```

### Arquitetura Proposta (Windows - RECOMENDADA)

```
AWS EC2 Windows Server 2019/2022
├── Chrome (GUI)
├── Web Signer 2.12.1 (Funciona nativamente)
├── Certificado A1 (Importado via certmgr.msc)
├── Python 3.12 + Selenium
├── Worker (Task Scheduler ou NSSM)
└── PostgreSQL (Local ou remoto)

✅ FUNCIONA: Native Messaging 100% operacional
```

---

## ✨ Funcionalidades

### Consulta de Processos

- ✅ **Por CPF/CNPJ:** Busca todos os processos de uma pessoa/empresa
- ✅ **Por Número CNJ:** Consulta processo específico
- ✅ **Detecção automática:** Identifica tipo de input (CPF vs CNJ)
- ✅ **Paginação:** Navega múltiplas páginas de resultados
- ✅ **Filtro:** Processa apenas processos da classe "Precatório"

### Autenticação

- ✅ **Certificado Digital:** Auto-seleção via políticas do Chrome
- ✅ **CPF/Senha:** Fallback para login tradicional
- ✅ **Perfil do Chrome:** Reutiliza sessões e certificados salvos

### Download de PDFs

- ✅ **Modo TURBO:** Seleção e download acelerados via JavaScript
- ✅ **Modo Normal:** Aguarda carregamento completo da interface
- ✅ **Fallback Automático:** Se normal falhar, tenta TURBO
- ✅ **Fallback HTTP:** Se Chrome falhar, usa requests com cookies
- ✅ **Tratamento de Alertas:** Detecta "Selecione pelo menos um item"
- ✅ **Arquivo Único:** PDF consolidado de todos os documentos

### Robustez

- ✅ **Retry Automático:** Múltiplas tentativas em caso de falha
- ✅ **Screenshots:** Captura tela em caso de erro (HTML + PNG)
- ✅ **Métricas:** Tempo de execução (started_at, finished_at, duration)
- ✅ **Limpeza:** Fecha abas criadas e encerra Chrome ao final
- ✅ **Headless Mode:** Execução sem interface gráfica

---

## 📦 Requisitos

### Sistema Operacional

| SO | Status | Observação |
|----|--------|------------|
| **Windows Server** | ✅ Recomendado | Native Messaging funciona |
| **macOS** | ✅ Funciona | Apenas desenvolvimento |
| **Linux** | ❌ **BLOQUEADO** | Native Messaging não funciona via Selenium |

### Software

```bash
# Python
Python 3.12+

# Navegador
Chrome/Chromium (instalado automaticamente)

# Banco de Dados
PostgreSQL 12+

# Certificado Digital
Certificado A1 (.pfx) válido e não expirado
```

### Dependências Python

```txt
fastapi==0.115.2
uvicorn[standard]==0.30.6
selenium==4.25.0
requests
psycopg2
cryptography  # Para solução WebSocket (experimental)
websockets    # Para solução WebSocket (experimental)
```

---

## 🚀 Instalação

### Ambiente de Desenvolvimento (macOS/Windows)

```bash
# 1. Clonar repositório
git clone https://github.com/revisaprecatorio/crawler_tjsp.git
cd crawler_tjsp

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Ajustar conforme necessário
```

### Ambiente de Produção (Windows Server - RECOMENDADO)

Veja guia completo em [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md#-recomendação-estratégica)

```powershell
# 1. Instalar software
# - Google Chrome
# - Web Signer 2.12.1
# - Python 3.12
# - Git for Windows

# 2. Importar certificado
# Windows + R > certmgr.msc
# Personal > Certificates > Import > certificado.pfx

# 3. Configurar política Chrome
# Registry: AutoSelectCertificateForUrls

# 4. Clonar e configurar
git clone https://github.com/revisaprecatorio/crawler_tjsp.git
cd crawler_tjsp
pip install -r requirements.txt
copy .env.example .env
notepad .env

# 5. Testar
python crawler_full.py --doc "12345678900" --abrir-autos --baixar-pdf
```

---

## 💻 Uso

### Crawler Standalone

```bash
# Consulta simples (apenas extrai dados)
python crawler_full.py --doc "12345678900"

# Consulta + abre Pasta Digital (sem download)
python crawler_full.py \
  --doc "12345678900" \
  --abrir-autos

# Consulta + download PDF (modo TURBO)
python crawler_full.py \
  --doc "0158003-37.2025.8.26.0500" \
  --abrir-autos \
  --baixar-pdf \
  --turbo-download \
  --download-dir "downloads/cliente123"

# Modo headless (servidor sem GUI)
python crawler_full.py \
  --doc "12345678900" \
  --abrir-autos \
  --baixar-pdf \
  --headless

# Com login CPF/senha (sem certificado)
python crawler_full.py \
  --doc "12345678900" \
  --cas-usuario "98765432100" \
  --cas-senha "minhaSenha123"
```

### Parâmetros Disponíveis

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--doc` | ✅ | CPF/CNPJ ou Número CNJ do processo |
| `--abrir-autos` | ❌ | Abre a Pasta Digital do processo |
| `--baixar-pdf` | ❌ | Baixa PDFs da Pasta Digital |
| `--turbo-download` | ❌ | Usa modo TURBO (seleção via JS) |
| `--download-dir` | ❌ | Diretório de download (padrão: `downloads`) |
| `--user-data-dir` | ❌ | Caminho do perfil do Chrome |
| `--cert-issuer-cn` | ❌ | CN do emissor do certificado |
| `--cert-subject-cn` | ❌ | CN do titular do certificado |
| `--cas-usuario` | ❌ | CPF para login CAS (fallback) |
| `--cas-senha` | ❌ | Senha para login CAS (fallback) |
| `--headless` | ❌ | Executa sem interface gráfica |
| `--debugger-address` | ❌ | Anexa a Chrome existente (ex: `localhost:9222`) |

### Orquestrador (Worker)

```bash
# Modo direto
python orchestrator_subprocess.py

# Com Docker (Linux - atualmente BLOQUEADO)
docker compose up -d worker
docker compose logs -f worker
```

### Gerenciar Filas no Banco

```sql
-- Inserir novo job
INSERT INTO consultas_esaj (cpf, processos, status)
VALUES (
  '12345678900',
  '{
    "lista": [
      {"numero": "0158003-37.2025.8.26.0500", "classe": "Precatório"}
    ]
  }'::jsonb,
  false
);

-- Ver jobs pendentes
SELECT id, cpf, status, created_at
FROM consultas_esaj
WHERE status = false
ORDER BY id;

-- Resetar job para reprocessamento
UPDATE consultas_esaj
SET status = false
WHERE id = 123;
```

---

## 📚 Documentação

### Estrutura de Arquivos

```
crawler_tjsp/
├── README.md                          # Este arquivo
├── DIAGNOSTIC_REPORT.md               # ⭐ Análise completa e alternativas
├── DEPLOY_TRACKING.md                 # Histórico de 30 deploys
├── crawler_full.py                    # Motor do crawler (Selenium)
├── orchestrator_subprocess.py         # Orquestrador de filas
├── requirements.txt                   # Dependências Python
├── Dockerfile                         # Imagem Docker (worker)
├── docker-compose.yml                 # Orquestração Docker
├── .env.example                       # Template de configuração
│
├── docs/                              # Documentação técnica
│   ├── PLANO_XVFB_WEBSIGNER.md       # Plano Xvfb (não funcionou)
│   ├── PLANO_WEBSOCKET.md            # Plano WebSocket (experimental)
│   ├── CERTIFICADO_DIGITAL_SETUP.md  # Setup de certificado
│   ├── TROUBLESHOOTING_AUTENTICACAO.md
│   └── QUEUE_MANAGEMENT.md
│
├── chrome_extension/                  # Extensão customizada (WebSocket)
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   └── injected.js
│
├── websocket_cert_server.py          # Servidor WebSocket (experimental)
├── wip-research/                     # Pesquisas técnicas
│   ├── wip-Claude-search.md
│   ├── wip-Chatgpt-search.md
│   └── wip-Perplexity-search.md
│
├── downloads/                        # PDFs baixados
├── screenshots/                      # Screenshots e logs
└── log_deploys/                      # Histórico de deploys
```

### Documentos Importantes

| Arquivo | Descrição |
|---------|-----------|
| [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) | **⭐ LEIA PRIMEIRO** - Análise completa, problema técnico e soluções |
| [DEPLOY_TRACKING.md](DEPLOY_TRACKING.md) | Histórico detalhado de 30 tentativas de deploy |
| [PLANO_WEBSOCKET.md](PLANO_WEBSOCKET.md) | Solução WebSocket customizada (experimental) |
| [wip-research/](wip-research/) | Pesquisas em Claude, ChatGPT, Perplexity |

---

## 🔧 Troubleshooting

### Erro: "Certificado não encontrado"

**Causa:** Certificado não importado no Chrome.

**Solução (Windows):**
```powershell
# Abrir gerenciador de certificados
certmgr.msc

# Personal > Certificates > Import
# Selecionar arquivo .pfx e importar
```

**Solução (Linux - NSS):**
```bash
# Criar NSS database
mkdir -p ~/.pki/nssdb
certutil -d sql:$HOME/.pki/nssdb -N --empty-password

# Importar certificado
pk12util -d sql:$HOME/.pki/nssdb -i certificado.pfx

# Verificar
certutil -L -d sql:$HOME/.pki/nssdb
```

### Erro: "Timeout aguardando resultado"

**Causa:** Site e-SAJ lento ou consulta sem resultados.

**Solução:**
- Verificar se CPF/CNJ está correto
- Tentar novamente (instabilidade do e-SAJ)
- Aumentar timeout em `_wait_result_page()` se necessário

### Erro: "Selecione pelo menos um item da árvore"

**Causa:** Árvore de documentos não carregou a tempo.

**Solução:**
- Usar `--turbo-download` (já trata esse erro automaticamente)
- Função `_dismiss_select_alert_and_retry()` resolve isso

### Container Docker não inicia

**Causa:** Falta de memória compartilhada.

**Solução:**
```yaml
# No docker-compose.yml
shm_size: '2gb'
```

### Erro de conexão com PostgreSQL

**Causa:** Credenciais incorretas ou firewall.

**Solução:**
```bash
# Teste conexão manual
psql -h 72.60.62.124 -p 5432 -U admin -d n8n

# Verificar firewall
sudo ufw allow 5432/tcp
```

---

## 🗺️ Roadmap

### Curto Prazo (Próximas 2 semanas)

- [ ] **Decisão estratégica:** Windows Server ou Legal Wizard
- [ ] **Implementar solução escolhida** (3-4 horas)
- [ ] **Validar autenticação** end-to-end
- [ ] **Processar 100 jobs reais** (teste de stress)
- [ ] **Documentar setup final**

### Médio Prazo (Próximo mês)

- [ ] Otimizar custos (auto-shutdown, Reserved Instance)
- [ ] Implementar monitoramento (alertas, métricas)
- [ ] Configurar backup e disaster recovery
- [ ] Criar dashboard de acompanhamento
- [ ] Documentação de manutenção

### Longo Prazo (Próximos 3-6 meses)

- [ ] Avaliar migração para Playwright
- [ ] Investigar APIs REST do TJSP (se existirem)
- [ ] Considerar paralelização (múltiplos workers)
- [ ] Implementar cache de resultados
- [ ] Exportar para formatos estruturados (JSON, CSV)

---

## 🤝 Contribuição

Este é um projeto proprietário de uso interno.

Para dúvidas ou sugestões:
1. Verificar [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)
2. Consultar [DEPLOY_TRACKING.md](DEPLOY_TRACKING.md)
3. Revisar [wip-research/](wip-research/)
4. Contatar equipe de desenvolvimento

---

## 📄 Licença

Proprietário - Uso interno apenas.

---

## 📞 Suporte

**Status do Projeto:** Aguardando decisão estratégica

**Próximos Passos:**
1. Ler [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)
2. Decidir entre Windows Server ou Legal Wizard
3. Implementar solução escolhida
4. Validar em produção

**Documentação Técnica Completa:** [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)

---

**Última atualização:** 2025-10-04
**Versão:** 2.0 (Restruturação profissional)
**Mantenedor:** Equipe de Desenvolvimento
