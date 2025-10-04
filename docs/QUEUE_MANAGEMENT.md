# 🔧 Gerenciamento da Fila de Processamento

Este documento explica como gerenciar a fila de jobs do crawler TJSP.

---

## 📋 Scripts Disponíveis

### 1. **manage_queue.py** (Recomendado)
Script Python interativo para gerenciar a fila.

### 2. **reset_queue.sql**
Script SQL com queries prontas para executar diretamente no PostgreSQL.

---

## 🚀 Uso do manage_queue.py

### **Instalação (primeira vez):**
```bash
pip install tabulate
```

### **Ver Estatísticas da Fila:**
```bash
python manage_queue.py --status
```
**Output:**
```
============================================================
📊 ESTATÍSTICAS DA FILA
============================================================
Total de registros:     50
✅ Processados:         32
⏳ Pendentes:           18
============================================================
```

### **Listar Jobs Pendentes:**
```bash
python manage_queue.py --list
```

### **Listar Últimos Jobs Processados:**
```bash
python manage_queue.py --list-processed
```

### **Resetar TODOS os Registros:**
```bash
python manage_queue.py --reset-all
```
⚠️ **CUIDADO:** Isso vai marcar todos os registros como pendentes novamente!

### **Resetar os Últimos N Registros:**
```bash
# Resetar os últimos 10 processados
python manage_queue.py --reset-last 10
```

### **Resetar Registros Específicos por ID:**
```bash
# Resetar IDs 30, 31 e 32
python manage_queue.py --reset-id 30 31 32
```

### **Resetar Todos os Registros de um CPF:**
```bash
python manage_queue.py --reset-cpf 07620857893
```

---

## 🗄️ Uso do reset_queue.sql

### **Executar via psql:**
```bash
psql -h 72.60.62.124 -p 5432 -U admin -d n8n -f reset_queue.sql
```

### **Ou conectar e executar manualmente:**
```bash
# 1. Conectar ao banco
psql -h 72.60.62.124 -p 5432 -U admin -d n8n

# 2. Ver estatísticas
SELECT 
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE status = TRUE) as processados,
    COUNT(*) FILTER (WHERE status = FALSE OR status IS NULL) as pendentes
FROM consultas_esaj;

# 3. Resetar todos
UPDATE consultas_esaj SET status = FALSE;

# 4. Resetar últimos 10
UPDATE consultas_esaj 
SET status = FALSE 
WHERE id IN (
    SELECT id FROM consultas_esaj 
    WHERE status = TRUE 
    ORDER BY id DESC 
    LIMIT 10
);

# 5. Resetar por CPF
UPDATE consultas_esaj 
SET status = FALSE 
WHERE cpf = '07620857893';
```

---

## 🐳 Uso Dentro do Docker

### **Opção 1: Executar manage_queue.py no container**
```bash
# Entrar no container
docker exec -it tjsp_worker_1 bash

# Executar o script
python manage_queue.py --status
python manage_queue.py --reset-last 5
```

### **Opção 2: Executar do host (sem entrar no container)**
```bash
docker exec tjsp_worker_1 python manage_queue.py --status
docker exec tjsp_worker_1 python manage_queue.py --reset-last 10
```

---

## 📊 Estrutura da Tabela

```sql
CREATE TABLE consultas_esaj (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11),
    processos JSONB,
    status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Campos Importantes:**
- **id**: Identificador único do job
- **cpf**: CPF associado aos processos
- **processos**: JSON com lista de processos (incluindo precatórios)
- **status**: `FALSE` = pendente, `TRUE` = processado, `NULL` = pendente

---

## 🔄 Workflow de Processamento

```
┌─────────────────────────────────────────────────────────┐
│  1. Job inserido com status = FALSE                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. Worker busca: WHERE status = FALSE OR status IS NULL│
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. Worker processa o job (executa crawler_full.py)     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. Se sucesso: UPDATE status = TRUE                     │
│     Se falha: status permanece FALSE                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  5. Worker busca próximo job pendente (loop infinito)    │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Cenários de Teste

### **Teste 1: Inserir Job Manualmente**
```sql
INSERT INTO consultas_esaj (cpf, processos, status) 
VALUES (
    '07620857893', 
    '{"lista": [{"classe": "Precatório", "numero": "0077044-50.2023.8.26.0500"}]}',
    FALSE
);
```

### **Teste 2: Reprocessar Job Específico**
```bash
# Ver qual ID você quer reprocessar
python manage_queue.py --list-processed

# Resetar o ID específico
python manage_queue.py --reset-id 30
```

### **Teste 3: Reprocessar Últimos Jobs (para debug)**
```bash
# Resetar os últimos 5 processados
python manage_queue.py --reset-last 5

# Verificar que estão pendentes
python manage_queue.py --list

# Monitorar o worker processar
docker compose logs -f worker
```

---

## 🐛 Troubleshooting

### **Problema: Worker não encontra jobs**
```bash
# 1. Verificar se há jobs pendentes
python manage_queue.py --status

# 2. Se não houver, resetar alguns
python manage_queue.py --reset-last 5

# 3. Verificar logs do worker
docker compose logs -f worker
```

### **Problema: Jobs ficam travados (não processam)**
```bash
# 1. Ver quais estão pendentes
python manage_queue.py --list

# 2. Verificar se o worker está rodando
docker compose ps

# 3. Reiniciar o worker
docker compose restart worker
```

### **Problema: Erro de conexão com banco**
```bash
# Verificar variáveis de ambiente
cat .env

# Testar conexão manualmente
psql -h 72.60.62.124 -p 5432 -U admin -d n8n
```

---

## 📝 Boas Práticas

1. **Antes de resetar em produção:**
   - Sempre use `--status` para ver quantos serão afetados
   - Prefira `--reset-last N` ao invés de `--reset-all`
   - Faça backup se necessário

2. **Para testes:**
   - Use `--reset-id` para jobs específicos
   - Monitore os logs após resetar: `docker compose logs -f worker`

3. **Manutenção:**
   - Execute `--status` periodicamente para monitorar a fila
   - Use `--list-processed` para auditar o que foi processado

---

## 🔗 Referências

- **DEPLOY_TRACKING.md** - Histórico completo do deploy
- **README.md** - Documentação geral do projeto
- **orchestrator_subprocess.py** - Código do worker que processa a fila

---

**Última Atualização:** 2025-10-01 00:44
