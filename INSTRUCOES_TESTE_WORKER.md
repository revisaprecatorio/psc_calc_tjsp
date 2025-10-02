# 🧪 Instruções para Teste do Worker com ChromeDriver Local

**Data:** 2025-10-02  
**Status Atual:** Xvfb + ChromeDriver configurados e funcionando  
**Próximo Passo:** Testar integração com worker Docker

---

## 📋 PRÉ-REQUISITOS

✅ **Já Configurado:**
- Xvfb rodando no display :99
- ChromeDriver rodando na porta 4444
- Chrome instalado e testado
- Selenium instalado globalmente

🔧 **Ainda Pendente:**
- Certificado digital A1 + Web Signer (será configurado depois)
- Por enquanto, vamos testar SEM autenticação (apenas navegação básica)

---

## 🎯 OBJETIVO DO TESTE

Validar que o worker Docker consegue:
1. ✅ Conectar ao ChromeDriver local (porta 4444)
2. ✅ Usar o Chrome via Xvfb
3. ✅ Processar jobs da fila
4. ✅ Salvar screenshots
5. ⚠️ Falhar na autenticação (esperado, sem certificado ainda)

---

## 📝 PASSO 1: PREPARAR REGISTRO DE TESTE NO BANCO

### **1.1. Conectar ao PostgreSQL**

```bash
# Na VPS - PostgreSQL está exposto na porta 5432
PGPASSWORD="BetaAgent2024SecureDB" psql -h 72.60.62.124 -p 5432 -U admin -d n8n
```

**ℹ️ NOTA:** O PostgreSQL está rodando em container separado e exposto externamente.

### **1.2. Verificar Tabela**

```sql
-- Ver estrutura da tabela
\d consultas_esaj

-- Ver registros existentes
SELECT id, cpf, numero_processo, status, created_at 
FROM consultas_esaj 
ORDER BY id DESC 
LIMIT 5;
```

### **1.3. Inserir Registro de Teste**

```sql
-- Inserir 1 registro de teste
INSERT INTO consultas_esaj (
    cpf, 
    numero_processo, 
    status, 
    created_at
) VALUES (
    '51764890230',  -- CPF do certificado
    '1234567-89.2024.8.26.0100',  -- Processo fictício para teste
    FALSE,  -- Status pendente
    NOW()
);

-- Confirmar inserção
SELECT id, cpf, numero_processo, status 
FROM consultas_esaj 
WHERE status = FALSE 
ORDER BY id DESC 
LIMIT 1;
```

**Anote o ID retornado!** Você vai precisar para verificar o resultado.

### **1.4. Sair do PostgreSQL**

```sql
\q
```

---

## 📝 PASSO 2: MODIFICAR docker-compose.yml

### **2.1. Editar Arquivo**

```bash
# Na VPS
cd /root/crawler_tjsp
nano docker-compose.yml
```

### **2.2. Modificar Configuração**

**ANTES:**
```yaml
services:
  worker:
    build: .
    container_name: tjsp_worker_1
    restart: always
    env_file:
      - .env
    environment:
      - SELENIUM_REMOTE_URL=http://selenium-chrome:4444
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots
    depends_on:
      - selenium-chrome

  selenium-chrome:
    image: selenium/standalone-chrome:latest
    container_name: selenium_chrome
    ports:
      - "4444:4444"
    shm_size: '2gb'
```

**DEPOIS:**
```yaml
services:
  worker:
    build: .
    container_name: tjsp_worker_1
    restart: always
    network_mode: host  # ← ADICIONAR: Acessa ChromeDriver do host
    env_file:
      - .env
    environment:
      - SELENIUM_REMOTE_URL=http://localhost:4444  # ← MODIFICAR: localhost
      - DISPLAY=:99  # ← ADICIONAR: Usa Xvfb do host
    volumes:
      - ./downloads:/app/downloads
      - ./screenshots:/app/screenshots

  # COMENTAR: Não precisamos mais do container Selenium Grid
  # selenium-chrome:
  #   image: selenium/standalone-chrome:latest
  #   container_name: selenium_chrome
  #   ports:
  #     - "4444:4444"
  #   shm_size: '2gb'
```

**Salvar:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 📝 PASSO 3: REBUILD E RESTART DO WORKER

### **3.1. Parar Containers Atuais**

```bash
cd /root/crawler_tjsp
docker compose down
```

### **3.2. Rebuild (se necessário)**

```bash
# Apenas se houve mudanças no código
docker compose build --no-cache
```

### **3.3. Iniciar Worker**

```bash
docker compose up -d
```

### **3.4. Verificar Logs**

```bash
docker compose logs -f worker
```

---

## 📝 PASSO 4: MONITORAR EXECUÇÃO

### **4.1. Logs Esperados (SUCESSO)**

```
[INFO] Conectando ao Selenium Grid: http://localhost:4444
[INFO] ✅ Conectado ao Selenium Grid com sucesso!
[INFO] Processando job ID=XXX
[INFO] Navegando para: https://esaj.tjsp.jus.br/cpopg/open.do
[INFO] Screenshot salvo: /app/screenshots/job_XXX_processo_1.png
[ERROR] RuntimeError: CAS: autenticação necessária e não realizada.
[INFO] Atualizando status do job ID=XXX para TRUE
```

**✅ Isso é SUCESSO!** O erro de autenticação é esperado (ainda não temos certificado).

### **4.2. Logs Esperados (ERRO DE CONEXÃO)**

```
[ERROR] Erro ao conectar ao Selenium Grid: http://localhost:4444
[ERROR] Connection refused
```

**❌ Isso indica problema!** ChromeDriver não está acessível.

---

## 📝 PASSO 5: VALIDAR RESULTADO

### **5.1. Verificar Status no Banco**

```bash
# Conectar ao PostgreSQL
PGPASSWORD="BetaAgent2024SecureDB" psql -h 72.60.62.124 -p 5432 -U admin -d n8n

# Verificar status do job
SELECT id, cpf, numero_processo, status, updated_at 
FROM consultas_esaj 
WHERE id = XXX;  -- Substituir XXX pelo ID anotado

# Sair
\q
```

**Resultado Esperado:**
- `status = TRUE` → Job foi processado
- `updated_at` → Timestamp atualizado

### **5.2. Verificar Screenshots**

```bash
# Na VPS
ls -lh /root/crawler_tjsp/screenshots/

# Ver último screenshot criado
ls -lt /root/crawler_tjsp/screenshots/ | head -5
```

**Resultado Esperado:**
- Arquivo PNG criado com timestamp recente
- Tamanho > 0 bytes

### **5.3. Verificar Logs do ChromeDriver**

```bash
# Ver últimas linhas do log
tail -30 /var/log/chromedriver.log
```

**Resultado Esperado:**
- Mensagens de sessão iniciada
- Comandos de navegação
- Sessão encerrada

---

## 🔍 TROUBLESHOOTING

### **Problema 1: Worker não conecta ao ChromeDriver**

**Sintoma:**
```
[ERROR] Connection refused: http://localhost:4444
```

**Solução:**
```bash
# 1. Verificar se ChromeDriver está rodando
sudo systemctl status chromedriver

# 2. Testar API manualmente
curl http://localhost:4444/status

# 3. Verificar network_mode no docker-compose.yml
docker inspect tjsp_worker_1 | grep NetworkMode
# Deve retornar: "NetworkMode": "host"

# 4. Reiniciar ChromeDriver
sudo systemctl restart chromedriver
```

---

### **Problema 2: Worker não encontra DISPLAY**

**Sintoma:**
```
[ERROR] selenium.common.exceptions.WebDriverException: unknown error: Chrome failed to start
```

**Solução:**
```bash
# 1. Verificar se Xvfb está rodando
sudo systemctl status xvfb

# 2. Verificar variável DISPLAY no container
docker exec tjsp_worker_1 env | grep DISPLAY
# Deve retornar: DISPLAY=:99

# 3. Testar Xvfb manualmente
export DISPLAY=:99
xdpyinfo | head -5

# 4. Reiniciar Xvfb
sudo systemctl restart xvfb
sudo systemctl restart chromedriver
```

---

### **Problema 3: Job não é processado (fila vazia)**

**Sintoma:**
```
[INFO] Nenhum job pendente encontrado. Aguardando...
```

**Solução:**
```bash
# 1. Verificar se há jobs pendentes no banco
PGPASSWORD="BetaAgent2024SecureDB" psql -h 72.60.62.124 -p 5432 -U admin -d n8n -c \
  "SELECT COUNT(*) FROM consultas_esaj WHERE status = FALSE;"

# 2. Se retornar 0, inserir novo registro (ver Passo 1.3)

# 3. Verificar query no código
docker exec tjsp_worker_1 cat orchestrator_subprocess.py | grep "WHERE status"
```

---

### **Problema 4: Screenshot não é salvo**

**Sintoma:**
- Job processado (status=TRUE)
- Mas diretório screenshots/ vazio

**Solução:**
```bash
# 1. Verificar permissões do diretório
ls -ld /root/crawler_tjsp/screenshots/
# Deve ser writeable

# 2. Verificar volume no container
docker exec tjsp_worker_1 ls -la /app/screenshots/

# 3. Verificar logs do crawler
docker compose logs worker | grep -i screenshot

# 4. Testar criação manual
docker exec tjsp_worker_1 touch /app/screenshots/test.txt
ls /root/crawler_tjsp/screenshots/test.txt
```

---

## ✅ CRITÉRIOS DE SUCESSO

Para considerar o teste **BEM-SUCEDIDO**, você deve ver:

1. ✅ Worker conecta ao ChromeDriver local
2. ✅ Chrome abre via Xvfb (sem erros de display)
3. ✅ Navegação para TJSP funciona
4. ✅ Screenshot é salvo
5. ✅ Status do job é atualizado para TRUE
6. ⚠️ Erro de autenticação (esperado, sem certificado)

---

## 📊 RESULTADO ESPERADO

```
╔════════════════════════════════════════════════════════════╗
║  ✅ TESTE BEM-SUCEDIDO (Parcial)                           ║
╠════════════════════════════════════════════════════════════╣
║  ✅ Xvfb funcionando                                       ║
║  ✅ ChromeDriver funcionando                               ║
║  ✅ Worker conecta ao ChromeDriver                         ║
║  ✅ Chrome abre e navega                                   ║
║  ✅ Screenshot salvo                                       ║
║  ✅ Status atualizado no banco                             ║
║  ⚠️  Autenticação falha (ESPERADO - sem certificado)      ║
╠════════════════════════════════════════════════════════════╣
║  🔧 PRÓXIMO PASSO: Configurar certificado A1 + Web Signer ║
╚════════════════════════════════════════════════════════════╝
```

---

## 📝 APÓS O TESTE

### **Se o teste foi bem-sucedido:**

1. ✅ Documentar resultado neste arquivo
2. ✅ Atualizar DEPLOY_TRACKING.md
3. 🔧 Prosseguir para configuração do certificado (Fase 7-8)

### **Se o teste falhou:**

1. ❌ Documentar erro encontrado
2. 🔍 Seguir troubleshooting acima
3. 💬 Reportar problema com logs completos

---

## 📞 COMANDOS ÚTEIS

```bash
# Status geral do sistema
sudo systemctl status xvfb
sudo systemctl status chromedriver
docker compose ps

# Logs em tempo real
docker compose logs -f worker
tail -f /var/log/chromedriver.log

# Reiniciar tudo
sudo systemctl restart xvfb
sudo systemctl restart chromedriver
docker compose restart worker

# Limpar e recomeçar
docker compose down
docker compose up -d
docker compose logs -f worker
```

---

**Boa sorte com o teste! 🚀**
