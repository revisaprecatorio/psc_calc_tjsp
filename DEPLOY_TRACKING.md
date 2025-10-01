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
docker-compose down

# 3. Atualizar código
git pull origin main

# 4. Rebuild da imagem (com --no-cache quando necessário)
docker-compose build --no-cache

# 5. Subir containers
docker-compose up -d

# 6. Monitorar logs
docker-compose logs -f worker
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
   docker-compose logs -f worker
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
1. Verificar logs: `docker-compose logs worker`
2. Validar credenciais do banco
3. Conferir variáveis de ambiente

---

## 📚 Referências

- **Repositório:** https://github.com/revisaprecatorio/crawler_tjsp
- **Servidor:** srv987902 (72.60.62.124)
- **Banco de Dados:** PostgreSQL (n8n database)
- **Documentação Selenium:** https://selenium-python.readthedocs.io/

---

**Última Atualização:** 2025-10-01 00:41  
**Status Geral:** 🟡 Em validação (aguardando teste com jobs reais)
