# 🔐 CONFIGURAÇÃO DO CERTIFICADO DIGITAL

**Data:** 2025-10-01  
**Objetivo:** Configurar certificado digital (.pfx) para autenticação CAS no TJSP  
**Arquivo:** `25424636_pf.pfx`

---

## 📋 CONTEXTO

Após deploy bem-sucedido do Selenium Grid, o crawler consegue conectar ao site TJSP, mas precisa de autenticação CAS para acessar os dados dos processos.

**Erro Atual:**
```
RuntimeError: CAS: autenticação necessária e não realizada.
```

**Solução:** Configurar certificado digital no ambiente Docker.

---

## 🔧 PASSOS PARA CONFIGURAÇÃO

### **1. Fazer Upload do Certificado para VPS**

```bash
# No seu computador local (onde está o .pfx)
scp /Users/persivalballeste/Documents/@IANIA/PROJECTS/revisa/revisa/2_Crawler/crawler_tjsp/25424636_pf.pfx root@srv987902.hstgr.cloud:/opt/crawler_tjsp/certs/

# OU usar rsync
rsync -avz 25424636_pf.pfx root@srv987902.hstgr.cloud:/opt/crawler_tjsp/certs/
```

---

### **2. Verificar Upload na VPS**

```bash
# Conectar na VPS
ssh root@srv987902.hstgr.cloud

# Navegar para o diretório
cd /opt/crawler_tjsp

# Verificar se o arquivo existe
ls -lh certs/25424636_pf.pfx

# Verificar permissões
chmod 600 certs/25424636_pf.pfx
```

---

### **3. Configurar Variáveis de Ambiente**

Editar o arquivo `.env`:

```bash
# Na VPS
cd /opt/crawler_tjsp
nano .env
```

**Adicionar/Atualizar as seguintes linhas:**

```bash
# ===== CERTIFICADO DIGITAL =====
# Caminho para o arquivo .pfx
CERT_PATH=/app/certs/25424636_pf.pfx

# Senha do certificado (IMPORTANTE: Você precisa fornecer)
CERT_PASSWORD=SUA_SENHA_AQUI

# Informações do certificado (opcional, para auto-seleção)
CERT_ISSUER_CN="AC Certisign Múltipla G5"
CERT_SUBJECT_CN="NOME COMPLETO:CPF"

# ===== ALTERNATIVA: Login com CPF/CNPJ + Senha =====
# Se não usar certificado, pode usar login/senha
# CAS_USUARIO=12345678900
# CAS_SENHA=sua_senha_aqui
```

**IMPORTANTE:** Você precisa fornecer a **senha do certificado .pfx**!

---

### **4. Atualizar docker-compose.yml**

Verificar se o volume `certs` está mapeado:

```bash
# Ver configuração atual
cat docker-compose.yml | grep -A 5 volumes
```

**Deve ter:**
```yaml
volumes:
  - ./downloads:/app/downloads
  - ./screenshots:/app/screenshots
  - ./certs:/app/certs  # ← Este volume deve existir
```

Se não tiver, adicionar:

```bash
nano docker-compose.yml
```

---

### **5. Reiniciar Worker**

```bash
# Parar worker
docker compose stop worker

# Verificar variáveis de ambiente
docker compose config | grep CERT

# Reiniciar worker
docker compose up -d worker

# Monitorar logs
docker compose logs -f worker
```

---

### **6. Testar Autenticação**

```bash
# Resetar um job para teste
psql -h 72.60.62.124 -U admin -d n8n -c "
UPDATE consultas_esaj 
SET status = FALSE 
WHERE id = 28;"

# Monitorar processamento
docker compose logs -f worker
```

**Esperado:**
```
[INFO] Conectando ao Selenium Grid: http://selenium-chrome:4444
[INFO] ✅ Conectado ao Selenium Grid com sucesso!
[INFO] CAS: tentando aba CERTIFICADO...
[INFO] CAS: certificado = NOME DO TITULAR
[INFO] CAS: certificado OK.
```

---

## 🔍 TROUBLESHOOTING

### **Problema: Certificado não encontrado**

```bash
# Verificar se arquivo existe no container
docker exec tjsp_worker_1 ls -la /app/certs/

# Verificar variável de ambiente
docker exec tjsp_worker_1 env | grep CERT_PATH
```

**Solução:** Verificar mapeamento de volume no docker-compose.yml

---

### **Problema: Senha incorreta**

```
Error: Unable to load certificate
```

**Solução:** Verificar senha do certificado no `.env`

```bash
# Testar senha localmente (se tiver openssl)
openssl pkcs12 -info -in certs/25424636_pf.pfx -noout
```

---

### **Problema: Certificado não selecionado**

```
CAS: nenhum certificado disponível
```

**Solução:** Verificar `CERT_SUBJECT_CN` no `.env`

```bash
# Ver informações do certificado
openssl pkcs12 -in certs/25424636_pf.pfx -nokeys -info
```

---

## 📊 CHECKLIST DE VALIDAÇÃO

Antes de testar, verificar:

- [ ] Arquivo `.pfx` copiado para `/opt/crawler_tjsp/certs/`
- [ ] Permissões corretas: `chmod 600 certs/25424636_pf.pfx`
- [ ] Variável `CERT_PATH` configurada no `.env`
- [ ] Variável `CERT_PASSWORD` configurada no `.env`
- [ ] Volume `./certs:/app/certs` no docker-compose.yml
- [ ] Worker reiniciado: `docker compose restart worker`
- [ ] Logs monitorados: `docker compose logs -f worker`

---

## 🔐 SEGURANÇA

### **Proteção da Senha:**

```bash
# Permissões restritas no .env
chmod 600 .env

# Verificar que .env está no .gitignore
cat .gitignore | grep .env
```

### **Backup do Certificado:**

```bash
# Fazer backup do certificado
cp certs/25424636_pf.pfx certs/25424636_pf.pfx.backup-$(date +%Y%m%d)

# Permissões restritas
chmod 600 certs/*.pfx*
```

---

## 📝 INFORMAÇÕES NECESSÁRIAS

Para completar a configuração, você precisa fornecer:

1. **Senha do certificado .pfx** → Para `CERT_PASSWORD` no `.env`
2. **Nome do titular** (opcional) → Para `CERT_SUBJECT_CN` no `.env`
3. **CPF do titular** (opcional) → Para `CERT_SUBJECT_CN` no `.env`

---

## 🚀 COMANDOS RÁPIDOS - RESUMO

```bash
# 1. Upload do certificado (no seu computador)
scp 25424636_pf.pfx root@srv987902.hstgr.cloud:/opt/crawler_tjsp/certs/

# 2. Na VPS - Configurar
ssh root@srv987902.hstgr.cloud
cd /opt/crawler_tjsp
chmod 600 certs/25424636_pf.pfx
nano .env  # Adicionar CERT_PATH e CERT_PASSWORD

# 3. Reiniciar
docker compose restart worker
docker compose logs -f worker

# 4. Testar
psql -h 72.60.62.124 -U admin -d n8n -c "UPDATE consultas_esaj SET status = FALSE WHERE id = 28;"
```

---

**Próximo Passo:** Fornecer a senha do certificado para configurar no `.env`!
