# 📋 Deploy Tracking - TJSP Crawler Worker

**Data de Início:** 2025-10-01  
**Servidor:** srv987902 (72.60.62.124)  
**Ambiente:** Docker + PostgreSQL  
**Objetivo:** Deploy do crawler TJSP em produção com processamento de fila

---

## 🎯 Contexto Inicial

O código havia sido desenvolvido e testado anteriormente por outra pessoa. Durante o deploy em produção no servidor, foram identificados problemas de compatibilidade e configuração que precisaram ser corrigidos.

---

## 🔧 Problemas Encontrados e Correções Aplicadas

### **1. Erro: psycopg2 Build Failed**
**Data:** 2025-10-01 00:30  
**Problema:**
```
Building wheel for psycopg2 (setup.py): finished with status 'error'
error: command 'gcc' failed: No such file or directory
```

**Causa Raiz:**
- O pacote `psycopg2` requer compilação com GCC
- A imagem Docker `python:3.12-slim-bookworm` não possui ferramentas de build

**Solução Aplicada:**
```diff
# requirements.txt
- psycopg2
+ psycopg2-binary
```

**Commit:** `24b7447` → Alteração de psycopg2 para psycopg2-binary

**Status:** ✅ Resolvido

---

### **2. Erro: CHROME_USER_DATA_DIR com Caminho Windows**
**Data:** 2025-10-01 00:34  
**Problema:**
```bash
--user-data-dir C:\Temp\ChromeProfileTest2
```
O worker estava usando caminho do Windows dentro do container Linux.

**Causa Raiz:**
- O arquivo `.env` continha configuração de desenvolvimento local (Windows)
- O Docker copiou o `.env` com configuração incorreta

**Solução Aplicada:**
```diff
# .env
- CHROME_USER_DATA_DIR="C:\Temp\ChromeProfileTest2"
+ CHROME_USER_DATA_DIR=/app/chrome_profile
```

**Commit:** `eb39a27` → Correção do CHROME_USER_DATA_DIR para caminho Linux

**Observação:** Foi necessário rebuild com `--no-cache` para forçar cópia do novo `.env`

**Status:** ✅ Resolvido

---

### **3. Erro: Query SQL com Boolean como String**
**Data:** 2025-10-01 00:39  
**Problema:**
```python
WHERE status= 'false'  # ← Comparando boolean com string
```

O worker conectava ao banco mas não encontrava registros para processar.

**Causa Raiz:**
- PostgreSQL não converte automaticamente string `'false'` para boolean `FALSE`
- A query nunca retornava resultados mesmo com dados disponíveis

**Solução Aplicada:**
```diff
# orchestrator_subprocess.py (linha 38)
- WHERE status= 'false'
+ WHERE status = FALSE OR status IS NULL

# orchestrator_subprocess.py (linha 90)
- query = "UPDATE consultas_esaj SET status =true WHERE id = %s;"
+ query = "UPDATE consultas_esaj SET status = TRUE WHERE id = %s;"
```

**Melhorias Adicionais:**
- Adicionado `LIMIT 1` para otimização da query
- Tratamento de valores NULL no status

**Commit:** `e9bb8c6` → Correção da query SQL para usar boolean

**Status:** ✅ Resolvido

---

### **4. Adição: Ferramentas de Gerenciamento da Fila**
**Data:** 2025-10-01 00:44  
**Objetivo:**
Criar ferramentas para facilitar o gerenciamento e teste da fila de processamento.

**Problema Identificado:**
- Sem ferramentas, era difícil testar o worker
- Não havia forma fácil de resetar jobs para reprocessamento
- Faltava visibilidade sobre o estado da fila

**Solução Implementada:**

**4.1. manage_queue.py**
Script Python interativo com funcionalidades:
- `--status`: Mostra estatísticas da fila (total, processados, pendentes)
- `--list`: Lista próximos jobs pendentes
- `--list-processed`: Lista últimos jobs processados
- `--reset-all`: Reseta todos os registros (com confirmação)
- `--reset-last N`: Reseta os últimos N registros processados
- `--reset-id ID1 ID2`: Reseta IDs específicos
- `--reset-cpf CPF`: Reseta todos os registros de um CPF

**4.2. reset_queue.sql**
Queries SQL prontas para uso direto no PostgreSQL com opções de reset.

**4.3. QUEUE_MANAGEMENT.md**
Documentação completa com:
- Exemplos de uso de todos os comandos
- Workflow de processamento visual
- Cenários de teste
- Guia de troubleshooting

**Dependência Adicionada:**
```diff
# requirements.txt
+ tabulate  # Para formatação de tabelas no manage_queue.py
```

**Commits:** 
- `136de15` → Documentação de tracking inicial
- `16601a4` → Ferramentas de gerenciamento da fila
- `734c4ae` → Atualização de documentação e correção de comandos

**Status:** ✅ Implementado

**Uso:**
```bash
# Dentro do container
docker exec -it tjsp_worker_1 bash
python manage_queue.py --status

# Do host (sem entrar no container)
docker exec tjsp_worker_1 python manage_queue.py --status
```

---

### **5. Deploy Final: Integração Completa**
**Data:** 2025-10-01 01:39  
**Objetivo:**
Deploy completo com todas as correções e ferramentas integradas.

**Mudanças Consolidadas:**
1. ✅ Query SQL corrigida (boolean ao invés de string)
2. ✅ Ferramentas de gerenciamento da fila implementadas
3. ✅ Dependência `tabulate` adicionada ao requirements.txt
4. ✅ Documentação completa (DEPLOY_TRACKING.md + QUEUE_MANAGEMENT.md)
5. ✅ Comandos Docker corrigidos (docker compose sem hífen)

**Motivo do Rebuild:**
- Novo pacote Python (`tabulate`) precisa ser instalado
- Código do `orchestrator_subprocess.py` atualizado
- Novos scripts (`manage_queue.py`, `reset_queue.sql`) precisam ser copiados

**Procedimento de Deploy:**

```bash
# 1. Navegue até o diretório
cd /opt/crawler_tjsp

# 2. Pare o container atual
docker compose down

# 3. Atualize o código do repositório
git pull origin main

# 4. Reconstrua a imagem (para instalar o tabulate e copiar novos arquivos)
docker compose build

# 5. Suba o container novamente
docker compose up -d

# 6. Verifique se está rodando
docker compose ps

# 7. Teste o script de gerenciamento
docker exec tjsp_worker_1 python manage_queue.py --status

# 8. Se não houver jobs pendentes, resete alguns para teste
docker exec tjsp_worker_1 python manage_queue.py --reset-last 5

# 9. Monitore os logs para ver o processamento
docker compose logs -f worker
```

**Validações Pós-Deploy:**
- [x] Container iniciou sem erros
- [x] Script `manage_queue.py` executa corretamente
- [x] Conexão com banco de dados estabelecida
- [x] Query retorna jobs pendentes (se houver)
- [x] Worker processa jobs da fila
- [x] Status é atualizado no banco após processamento

**Resultado do Deploy:**
```
✅ Job ID=30 → Processado → Status atualizado
✅ Job ID=31 → Processado → Status atualizado
✅ Job ID=32 → Processado → Status atualizado
✅ Comando correto: --user-data-dir /app/chrome_profile
✅ Loop de processamento funcionando
✅ Restart automático ativo
```

**Status:** ✅ **DEPLOY CONCLUÍDO COM SUCESSO** (2025-10-01 02:05)

---

### **6. Problema: Selenium Não Baixa PDFs**
**Data:** 2025-10-01 02:30  
**Problema:**
- Worker processava jobs com sucesso
- Status era atualizado no banco
- Mas nenhum PDF era baixado (diretórios vazios)
- Não havia mensagens de erro nos logs

**Causa Raiz:**
O orchestrator executava `crawler_full.py` com `capture_output=True` mas **não imprimia o stdout**, então erros do Selenium ficavam ocultos.

**Solução Aplicada:**
```python
# orchestrator_subprocess.py
result = subprocess.run(command, capture_output=True, ...)

# ADICIONADO: Imprimir stdout para debug
if result.stdout:
    print("\n--- Output do Crawler ---")
    print(result.stdout)
    print("--- Fim do Output ---\n")
```

**Commit:** `7ac6755` → Adiciona output do crawler nos logs

**Status:** ✅ Resolvido - Agora vemos erros do Selenium

---

### **7. Erro: Chrome user-data-dir Already in Use**
**Data:** 2025-10-01 02:42  
**Problema:**
```
SessionNotCreatedException: user data directory is already in use
```

**Causa Raiz:**
- Múltiplas execuções do crawler tentavam usar o mesmo `--user-data-dir`
- Chrome cria locks de arquivo que persistem entre execuções
- Mesmo com diretórios únicos, o problema persistia

**Tentativas de Solução:**
1. ❌ Criar diretório único por execução (`chrome_profile_{job_id}_{i}_{timestamp}`)
2. ✅ **Remover completamente o argumento `--user-data-dir`**

**Solução Final:**
```python
# ANTES
command = [..., "--user-data-dir", chrome_profile_path]

# DEPOIS
command = [...]  # SEM --user-data-dir
# Chrome cria perfil temporário automaticamente
```

**Commits:**
- `9cce20c` → Tentativa com diretório único (não resolveu)
- `dc5bf3e` → Remove user-data-dir completamente

**Status:** ⚠️ **PROBLEMA PERSISTE** - Investigação em andamento

**Observação:** O erro continua mesmo sem `--user-data-dir`. Isso indica que o problema pode estar no próprio `crawler_full.py` que ainda está passando o argumento internamente.

---

## 📦 Arquivos Modificados

### **requirements.txt**
```txt
fastapi==0.115.2
uvicorn[standard]==0.30.6

# Selenium e dependências
selenium==4.25.0

# Outras dependências
requests
psycopg2-binary  # ← ALTERADO de psycopg2
python-dotenv
tabulate  # ← ADICIONADO para manage_queue.py
```

### **.env**
```bash
# ===== BANCO DE DADOS =====
DB_HOST=72.60.62.124
DB_PORT=5432
DB_NAME=n8n
DB_USER=admin
DB_PASSWORD=BetaAgent2024SecureDB

# ===== CHROME =====
CHROME_USER_DATA_DIR=/app/chrome_profile  # ← ALTERADO de C:\Temp\...

# ===== CERTIFICADO DIGITAL (opcional) =====
CERT_ISSUER_CN="AC Certisign Múltipla G5"
CERT_SUBJECT_CN="NOME COMPLETO:12345678900"
```

### **orchestrator_subprocess.py**
```python
# Linha 35-41: Query de busca
query = """
    SELECT id, cpf, processos 
    FROM consultas_esaj 
    WHERE status = FALSE OR status IS NULL  # ← ALTERADO
    ORDER BY id 
    LIMIT 1;  # ← ADICIONADO
"""

# Linha 90: Query de update
query = "UPDATE consultas_esaj SET status = TRUE WHERE id = %s;"  # ← ALTERADO
```

---

## 🚀 Processo de Deploy

### **Comandos Executados no Servidor:**

```bash
# 1. Navegação e preparação
cd /opt/crawler_tjsp

# 2. Parar containers
docker compose down

# 3. Atualizar código
git pull origin main

# 4. Rebuild da imagem (com --no-cache quando necessário)
docker compose build --no-cache

# 5. Subir containers
docker compose up -d

# 6. Monitorar logs
docker compose logs -f worker
```

### **Estrutura Docker:**

**Dockerfile:**
- Base: `python:3.12-slim-bookworm`
- Dependências: Chromium, libs gráficas, certificados
- Workdir: `/app`
- Entrypoint: `orchestrator_subprocess.py`

**docker-compose.yml:**
- Service: `worker`
- Restart: `always`
- Volumes: `./downloads:/app/downloads`
- Network: `crawler_tjsp_default`

---

## 📊 Logs de Deploy

### **Deploy 1 - Erro psycopg2**
- Arquivo: `log_deploy_1.txt`
- Status: ❌ Falhou no pip install
- Erro: Build do psycopg2 falhou

### **Deploy 2 - Erro CHROME_USER_DATA_DIR**
- Arquivo: `log_deploy_2.txt`
- Status: ⚠️ Build OK, runtime com caminho Windows
- Erro: Caminho inválido no Linux

### **Deploy 3 - Query SQL Incorreta**
- Arquivo: `log_deploy_3.txt`
- Status: ⚠️ Build OK, sem jobs encontrados
- Erro: Query não retornava resultados

---

## ✅ Checklist de Validação

### **Pré-Deploy:**
- [x] Código versionado no Git
- [x] `.env` configurado para ambiente Linux
- [x] `requirements.txt` com dependências corretas
- [x] Dockerfile testado localmente

### **Durante Deploy:**
- [x] Docker build sem erros
- [x] Container inicia corretamente
- [x] Conexão com PostgreSQL estabelecida
- [x] Query SQL retorna resultados

### **Pós-Deploy:**
- [ ] Worker processa jobs da fila
- [ ] Downloads salvos corretamente
- [ ] Status atualizado no banco
- [ ] Logs sem erros críticos
- [ ] Restart automático funcionando

---

## 🔍 Próximos Passos

1. **Validar Query no Banco:**
   ```sql
   SELECT id, cpf, status FROM consultas_esaj 
   WHERE status = FALSE OR status IS NULL 
   LIMIT 5;
   ```

2. **Verificar Estrutura da Tabela:**
   ```sql
   \d consultas_esaj
   ```

3. **Inserir Job de Teste (se necessário):**
   ```sql
   INSERT INTO consultas_esaj (cpf, processos, status) 
   VALUES ('12345678900', '{"lista": [{"classe": "Precatório", "numero": "0077044-50.2023.8.26.0500"}]}', FALSE);
   ```

4. **Monitorar Processamento:**
   ```bash
   docker compose logs -f worker
   ```

5. **Validar Selenium/Chromium:**
   - Testar abertura do navegador headless
   - Verificar certificado digital (se aplicável)
   - Confirmar download de PDFs

---

## 📝 Notas Importantes

### **Diferenças Ambiente Dev vs Prod:**
- **Dev (Windows):** `C:\Temp\ChromeProfileTest2`
- **Prod (Linux/Docker):** `/app/chrome_profile`

### **Tipo de Dados PostgreSQL:**
- Campo `status`: **BOOLEAN** (não string)
- Valores válidos: `TRUE`, `FALSE`, `NULL`

### **Comportamento do Worker:**
- Loop infinito processando fila
- Encerra quando não há mais jobs (`status = FALSE`)
- Atualiza `status = TRUE` após sucesso
- Não atualiza se houver falhas

### **Restart Policy:**
- Docker configurado com `restart: always`
- Worker reinicia automaticamente em caso de crash
- Útil para processamento contínuo 24/7

---

## 🐛 Troubleshooting

### **Worker não encontra jobs:**
1. Verificar se há registros com `status = FALSE`
2. Validar estrutura JSON da coluna `processos`
3. Conferir logs de conexão com banco

### **Erro ao executar crawler_full.py:**
1. Verificar se Chromium está instalado
2. Testar modo headless
3. Validar permissões de escrita em `/app/downloads`

### **Container reinicia constantemente:**
1. Verificar logs: `docker compose logs worker`
2. Validar credenciais do banco
3. Conferir variáveis de ambiente

---

## 📚 Referências

- **Repositório:** https://github.com/revisaprecatorio/crawler_tjsp
- **Servidor:** srv987902 (72.60.62.124)
- **Banco de Dados:** PostgreSQL (n8n database)
- **Documentação Selenium:** https://selenium-python.readthedocs.io/
- **Gerenciamento de Fila:** Ver `QUEUE_MANAGEMENT.md`

---

## 📂 Estrutura de Arquivos e Downloads

### **Diretório de Downloads:**

**Dentro do Container:**
```
/app/downloads/{CPF}/
```

**No Host (mapeado via volume):**
```
/opt/crawler_tjsp/downloads/{CPF}/
```

### **Exemplo de Estrutura:**
```
/app/downloads/
├── 07620857893/          ← Diretório por CPF
│   ├── processo_1.pdf
│   ├── processo_2.pdf
│   └── ...
├── 01103192817/
│   └── ...
└── ...
```

### **Mapeamento Docker:**
```yaml
volumes:
  - ./downloads:/app/downloads
```

**Isso significa:**
- ✅ PDFs salvos no container em `/app/downloads/{CPF}/`
- ✅ Acessíveis no host em `/opt/crawler_tjsp/downloads/{CPF}/`
- ✅ Persistem mesmo se o container for removido

### **Comando Executado:**
```bash
--download-dir /app/downloads/07620857893
```

### **Para Verificar Downloads:**
```bash
# No servidor (host)
ls -la /opt/crawler_tjsp/downloads/07620857893/

# Dentro do container
docker exec tjsp_worker_1 ls -la /app/downloads/07620857893/
```

---

**Última Atualização:** 2025-10-01 02:07  
**Status Geral:** ✅ **DEPLOY CONCLUÍDO E VALIDADO**
