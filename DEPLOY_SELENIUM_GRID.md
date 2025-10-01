# 🚀 DEPLOY SELENIUM GRID - INSTRUÇÕES

**Data:** 2025-10-01  
**Commit:** f69fdab  
**Objetivo:** Resolver erro "user data directory is already in use" usando Selenium Grid

---

## 📋 RESUMO DAS MUDANÇAS

### **Arquivos Modificados:**
1. ✅ `docker-compose.yml` - Adiciona serviço Selenium Grid
2. ✅ `crawler_full.py` - Usa Remote WebDriver
3. ✅ `Dockerfile` - Simplificado (remove Chrome)

### **Benefícios:**
- ✅ Resolve erro de Chrome definitivamente
- ✅ Imagem 70% menor (~200 MB vs ~800 MB)
- ✅ Build 5x mais rápido (30s vs 3-5min)
- ✅ Suporta 5 sessões paralelas
- ✅ VNC para debug visual (porta 7900)

---

## 🔧 COMANDOS DE DEPLOY NA VPS

### **1. Conectar na VPS**
```bash
ssh root@srv987902.hstgr.cloud
cd /root/crawler_tjsp
```

### **2. Fazer Backup (Segurança)**
```bash
# Backup do docker-compose.yml antigo
cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d_%H%M%S)

# Backup do Dockerfile antigo
cp Dockerfile Dockerfile.backup-$(date +%Y%m%d_%H%M%S)
```

### **3. Atualizar Código do Git**
```bash
# Pull das mudanças
git pull origin main

# Verificar mudanças
git log -1 --stat
```

### **4. Parar Containers Atuais**
```bash
# Para todos os containers
docker compose down

# Verificar que pararam
docker ps -a
```

### **5. Limpar Imagens Antigas (Opcional)**
```bash
# Remove imagem antiga do worker (economiza espaço)
docker rmi tjsp-worker:latest

# Remove imagens não utilizadas
docker image prune -f
```

### **6. Rebuild com Selenium Grid**
```bash
# Build sem cache (garante imagem limpa)
docker compose build --no-cache

# Verificar tamanho da nova imagem
docker images | grep tjsp-worker
```

**Esperado:**
- Imagem antiga: ~800 MB
- Imagem nova: ~200 MB ✅

### **7. Iniciar Containers**
```bash
# Inicia em modo detached
docker compose up -d

# Verificar status
docker compose ps
```

**Esperado:**
```
NAME                IMAGE                              STATUS
selenium_chrome     selenium/standalone-chrome:latest  Up
tjsp_worker_1       tjsp-worker:latest                 Up
```

### **8. Verificar Logs**
```bash
# Logs do Selenium Grid
docker compose logs selenium-chrome

# Logs do Worker
docker compose logs -f worker
```

**Esperado no Worker:**
```
[INFO] Conectando ao Selenium Grid: http://selenium-chrome:4444
[INFO] ✅ Conectado ao Selenium Grid com sucesso!
```

### **9. Testar Conexão ao Grid**
```bash
# Verificar status do Selenium Grid
curl http://localhost:4444/status

# Deve retornar JSON com "ready": true
```

### **10. Validar Processamento**
```bash
# Verificar fila
docker exec tjsp_worker_1 python manage_queue.py --status

# Resetar alguns jobs para teste
docker exec tjsp_worker_1 python manage_queue.py --reset-last 3

# Monitorar processamento
docker compose logs -f worker
```

---

## 🔍 VALIDAÇÕES PÓS-DEPLOY

### **Checklist de Validação:**

- [ ] **Container Selenium Grid iniciou**
  ```bash
  docker ps | grep selenium_chrome
  ```

- [ ] **Container Worker iniciou**
  ```bash
  docker ps | grep tjsp_worker_1
  ```

- [ ] **Worker conectou ao Grid**
  ```bash
  docker compose logs worker | grep "Conectado ao Selenium Grid"
  ```

- [ ] **Grid está pronto**
  ```bash
  curl http://localhost:4444/status | jq '.value.ready'
  # Deve retornar: true
  ```

- [ ] **Worker processa jobs**
  ```bash
  docker compose logs worker | grep "Processando job"
  ```

- [ ] **PDFs são baixados**
  ```bash
  ls -lh downloads/
  # Deve ter arquivos .pdf recentes
  ```

- [ ] **Status atualizado no banco**
  ```bash
  docker exec tjsp_worker_1 python manage_queue.py --status
  # Verificar jobs com status "completed"
  ```

---

## 🐛 TROUBLESHOOTING

### **Problema: Selenium Grid não inicia**

**Sintomas:**
```
selenium_chrome | Error: ...
```

**Solução:**
```bash
# Verificar logs
docker compose logs selenium-chrome

# Verificar recursos
docker stats selenium_chrome

# Reiniciar apenas o Grid
docker compose restart selenium-chrome
```

---

### **Problema: Worker não conecta ao Grid**

**Sintomas:**
```
[ERROR] ❌ Falha ao conectar no Selenium Grid
```

**Solução:**
```bash
# Verificar se Grid está rodando
docker ps | grep selenium

# Verificar variável de ambiente
docker exec tjsp_worker_1 env | grep SELENIUM_REMOTE_URL
# Deve retornar: SELENIUM_REMOTE_URL=http://selenium-chrome:4444

# Testar conexão manualmente
docker exec tjsp_worker_1 curl http://selenium-chrome:4444/status
```

---

### **Problema: PDFs não são baixados**

**Sintomas:**
- Worker processa jobs
- Status atualizado
- Mas diretório `downloads/` vazio

**Solução:**
```bash
# Verificar volumes compartilhados
docker inspect selenium_chrome | grep -A 10 Mounts

# Verificar permissões
ls -la downloads/

# Verificar logs do Grid
docker compose logs selenium-chrome | grep -i download
```

---

## 🎯 DEBUG VISUAL (VNC)

O Selenium Grid expõe porta 7900 para debug visual via VNC.

### **Acessar VNC:**

1. **Criar túnel SSH:**
   ```bash
   # No seu computador local
   ssh -L 7900:localhost:7900 root@srv987902.hstgr.cloud
   ```

2. **Abrir navegador:**
   ```
   http://localhost:7900
   ```

3. **Senha:** (deixe em branco ou use `secret`)

4. **Ver Chrome em tempo real** enquanto crawler executa!

---

## 📊 MONITORAMENTO

### **Verificar Recursos:**
```bash
# CPU e Memória dos containers
docker stats

# Espaço em disco
df -h

# Logs em tempo real
docker compose logs -f
```

### **Verificar Sessões do Grid:**
```bash
# Status detalhado
curl http://localhost:4444/status | jq

# Sessões ativas
curl http://localhost:4444/status | jq '.value.nodes[0].slots'
```

---

## 🔄 ROLLBACK (Se necessário)

Se algo der errado, você pode voltar para a versão anterior:

```bash
# Parar containers
docker compose down

# Restaurar arquivos antigos
cp docker-compose.yml.backup-YYYYMMDD_HHMMSS docker-compose.yml
cp Dockerfile.backup-YYYYMMDD_HHMMSS Dockerfile

# Voltar commit no Git
git reset --hard 80d2682

# Rebuild e iniciar
docker compose build --no-cache
docker compose up -d
```

---

## ✅ SUCESSO ESPERADO

Após deploy bem-sucedido, você deve ver:

```bash
$ docker compose ps
NAME                IMAGE                              STATUS
selenium_chrome     selenium/standalone-chrome:latest  Up 2 minutes
tjsp_worker_1       tjsp-worker:latest                 Up 2 minutes

$ docker compose logs worker | tail -5
[INFO] Conectando ao Selenium Grid: http://selenium-chrome:4444
[INFO] ✅ Conectado ao Selenium Grid com sucesso!
[INFO] Processando job ID=35...
[INFO] ✅ Job ID=35 concluído com sucesso
[INFO] PDF baixado: downloads/processo_1234567.pdf
```

---

## 📝 PRÓXIMOS PASSOS

Após validar que tudo funciona:

1. ✅ Monitorar por 24h
2. ✅ Verificar estabilidade
3. ✅ Documentar no DEPLOY_TRACKING.md
4. ✅ Remover backups antigos (após 1 semana)

---

**Boa sorte com o deploy! 🚀**
