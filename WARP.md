# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.


Projeto: Crawler TJSP (e-SAJ) para consulta de precatórios com Selenium, orquestrado por worker e filas em PostgreSQL.

Estado atual: conforme README e DIAGNOSTIC_REPORT.md, há bloqueio técnico no Linux headless envolvendo Native Messaging (Web Signer). Execução recomendada: Windows Server (ou alternativa terceirizada). Para desenvolvimento local (macOS), é possível testar fluxos sem autenticação por certificado ou com credenciais CAS de fallback.


1) Comandos frequentes (desenvolvimento, execução, docker, testes)

- Preparar ambiente (Python 3.12+)
  - python3 -m venv .venv
  - source .venv/bin/activate
  - pip install -r requirements.txt

- Variáveis de ambiente essenciais (.env)
  - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  - CERT_SUBJECT_CN, CERT_ISSUER_CN  (auto-seleção de certificado no Chrome)
  - CAS_USUARIO, CAS_SENHA            (fallback de login)
  - SELENIUM_REMOTE_URL               (ex.: http://localhost:4444)
  - DISPLAY                           (em Linux com Xvfb, ex.: :99)

- Executar o crawler standalone (exemplos reais do README)
  - Consulta simples:                  python crawler_full.py --doc "12345678900"
  - Abrir Pasta Digital (sem download): python crawler_full.py --doc "12345678900" --abrir-autos
  - Download PDF TURBO (por CNJ):      python crawler_full.py \
      --doc "0158003-37.2025.8.26.0500" \
      --abrir-autos --baixar-pdf --turbo-download \
      --download-dir "downloads/cliente123"
  - Headless (se suportado):           python crawler_full.py --doc "12345678900" --abrir-autos --baixar-pdf --headless
  - Fallback CAS (sem certificado):    python crawler_full.py --doc "12345678900" --cas-usuario "00000000000" --cas-senha "SENHA"

- Orquestrador (fila no PostgreSQL)
  - Local:  python orchestrator_subprocess.py
  - Docker: docker compose build --no-cache worker
            docker compose up -d worker
            docker compose logs -f worker
  Observações Docker:
  - worker usa network_mode: host e espera ChromeDriver local em http://localhost:4444
  - volumes mapeiam downloads/, screenshots/ e certs/

- Gerenciar fila (manage_queue.py)
  - Status:                python manage_queue.py --status
  - Listar pendentes:      python manage_queue.py --list
  - Listar processados:    python manage_queue.py --list-processed
  - Resetar IDs:           python manage_queue.py --reset-id 30 31
  - Resetar últimos N:     python manage_queue.py --reset-last 10
  - Resetar por CPF:       python manage_queue.py --reset-cpf 12345678900

- Testes e diagnósticos (scripts/tests)
  Pré-requisitos para testes com Selenium: ChromeDriver em http://localhost:4444; para cenários Linux, Xvfb (:99) e, quando aplicável, extensão em /opt/crawler_tjsp/chrome_extension; servidor WebSocket (experimental) em ws://localhost:8765.
  - Teste simples (verifica página/indicativos Web Signer):
    python scripts/tests/test_esaj_simple.py
  - Selenium + WebSocket (experimental):
    python scripts/tests/test_selenium_websocket.py
  - Selenium local + WebSocket (experimental):
    python scripts/tests/test_selenium_local.py

- “Build” do projeto
  - Não há build Python. O “build” relevante é da imagem do worker:
    docker compose build --no-cache worker

- Lint/format
  - Não há linter/formatter configurados no repositório.


2) Arquitetura de alto nível (big picture)

Visão geral por componentes principais, com ênfase no fluxo entre arquivos e serviços (sintetizado a partir de README.md, crawler_full.py, orchestrator_subprocess.py, docker-compose.yml e docs/):

- Banco de dados (PostgreSQL)
  - Tabela consultas_esaj atua como fila de jobs.
  - Orquestrador seleciona o próximo job pendente (status = false/null) e, ao concluir com sucesso, atualiza status = true.

- Orquestrador (orchestrator_subprocess.py)
  - Carrega configuração do banco via .env.
  - Busca um job pendente (id, cpf, processos JSON) e itera os processos do tipo “Precatório”.
  - Para cada processo CNJ, dispara um subprocesso do crawler (python crawler_full.py ...) e direciona downloads para downloads/{cpf}.
  - Antes de cada rodada, finaliza instâncias antigas de chrome/chromedriver para evitar “user data directory is already in use”.
  - Ao fim, atualiza o status do job no banco (se todos os subprocessos foram bem-sucedidos).
  - Em produção por Docker: container “worker” conectando a um ChromeDriver exposto no host (network_mode: host), variável SELENIUM_REMOTE_URL=http://localhost:4444.

- Crawler (crawler_full.py)
  - Motor Selenium que acessa e-SAJ, realiza autenticação e executa a consulta.
  - Autenticação: prioriza certificado digital A1 (via Web Signer/Extensão) e, se falhar, tenta login CAS (CPF/senha) quando fornecidos.
  - Critérios de consulta: por Documento da Parte (CPF/CNPJ) ou por Número do Processo (CNJ), com parsing e preenchimento robusto de campos.
  - Resultado: identifica se há “lista” ou “detalhe”; percorre apenas itens da classe “Precatório”; ao entrar no detalhe, opcionalmente abre a Pasta Digital.
  - Download de PDFs: habilita downloads via CDP, tenta “Selecionar todos”, lida com jstree/iframes, trata modal de impressão (“Arquivo único”), aguarda novos PDFs no diretório de download e, se necessário, usa fallback HTTP com cookies do navegador para concluir o download.
  - Estratégias de resiliência: múltiplas tentativas de clique (direto/JS), detecção e fechamento de banners de erro no viewer, anti-alerta (“Selecione pelo menos um item da árvore”) e fallback de URL direta de impressão quando presente.
  - Integração com infraestrutura de execução:
    - Conecta preferencialmente a um Selenium remoto (SELENIUM_REMOTE_URL) ou a um ChromeDriver local; suporta anexar a uma sessão existente via DEBUGGER_ADDRESS.
    - Em Linux com Xvfb, o fluxo “headless” efetivo é o Chrome “headed” no display virtual (:99), conforme documentação em docs/.

- Servidor WebSocket (websocket_cert_server.py) — experimental
  - Proposta alternativa ao Native Messaging: servidor Python que carrega .pfx, expõe listagem de certificado e operação de assinatura via WebSocket.
  - Usado em conjunto com extensão Chrome custom (fora deste repositório público), para emular a API window.WebSigner.
  - Constatado em DIAGNOSTIC_REPORT.md: funciona manualmente, mas apresenta limitações sob automação com ChromeDriver em Linux headless.

- Contêineres e execução
  - Dockerfile constrói apenas o worker Python; o Chrome/ChromeDriver não são instalados na imagem do worker (premissa: ChromeDriver roda no host ou em serviço dedicado).
  - docker-compose.yml levanta o worker com network_mode: host, monta pastas de downloads/screenshots/certs e (opcionalmente) o NSS database do host.

- Pastas de saída
  - downloads/: PDFs salvos por CPF/execução.
  - screenshots/: prints e páginas de erro para diagnóstico.

- Limitações e recomendação de plataforma
  - Native Messaging/Web Signer falham sob automação com ChromeDriver no Linux headless/Xvfb (detalhes no DIAGNOSTIC_REPORT.md).
  - Recomendada a execução em Windows Server (onde Native Messaging funciona de forma confiável) ou adoção de solução terceirizada (ver README/DIAGNOSTIC_REPORT.md).


3) Referências internas importantes

- README.md: visão geral, comandos exemplificados, status do projeto e recomendações de plataforma.
- DIAGNOSTIC_REPORT.md: análise técnica completa do bloqueio e comparativo de alternativas (Windows, WebSocket, etc.).
- docs/: instruções de deploy (Xvfb, Selenium Grid), troubleshooting de autenticação, plano WebSocket e resumo de implementação.
- docker-compose.yml e Dockerfile: base para execução do worker em produção (Linux host com ChromeDriver exposto em 4444).
- scripts/tests/: utilitários de validação com Selenium (para cenários específicos); exigem infraestrutura local apropriada.
- CLAUDE.md / AGENTS.md: instruções voltadas a outro agente (byterover-mcp); não se aplicam ao fluxo do Warp.


Notas finais para Warp
- Evite pressupor a existência de linter/pytest: o repositório não traz configuração para isso.
- Ao criar comandos de execução, considere o ambiente atual:
  - macOS (dev): preferir Chrome local; a autenticação por certificado pode não funcionar integralmente sob automação.
  - Linux: seguir docs/ para Xvfb/ChromeDriver; atentar-se ao bloqueio de Native Messaging.
  - Windows (prod recomendado): seguir README/DIAGNOSTIC_REPORT.md para configuração do certificado e políticas do Chrome.
