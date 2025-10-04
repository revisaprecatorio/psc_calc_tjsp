# 📝 Instruções para Atualizar .env na VPS

**Data:** 2025-10-02  
**Objetivo:** Corrigir configurações do certificado digital no `.env` da VPS

---

## ⚠️ PROBLEMA IDENTIFICADO

O `.env` na VPS está com valores **INCORRETOS** do certificado:

```bash
# ❌ ERRADO (valores de exemplo/placeholder)
CERT_ISSUER_CN="AC Certisign Múltipla G5"
CERT_SUBJECT_CN="NOME COMPLETO:12345678900"
```

**Deveria ser:**

```bash
# ✅ CORRETO (valores reais extraídos do certificado)
CERT_ISSUER_CN=AC Certisign RFB G5
CERT_SUBJECT_CN=FLAVIO EDUARDO CAPPI:51764890230
```

---

## 🔧 CORREÇÃO NA VPS

Execute na VPS:

```bash
# Ir para o diretório
cd /opt/crawler_tjsp

# Backup do .env atual
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Criar novo .env com valores corretos
cat > .env << 'EOF'
# ===== BANCO DE DADOS =====
DB_HOST=72.60.62.124
DB_PORT=5432
DB_NAME=n8n
DB_USER=admin
DB_PASSWORD=BetaAgent2024SecureDB

# ===== CHROME =====
# Caminho para o perfil do Chrome (não necessário com ChromeDriver local, mas mantido por compatibilidade)
CHROME_USER_DATA_DIR=/app/chrome_profile

# ===== CERTIFICADO DIGITAL =====
# Caminho do arquivo .pfx dentro do container
CERT_PFX_PATH=/app/certs/25424636_pf.pfx
CERT_PFX_PASSWORD=903205

# Subject Name (CN) do certificado - usado para seleção automática
# IMPORTANTE: Use o CN COMPLETO extraído do certificado
CERT_SUBJECT_CN=FLAVIO EDUARDO CAPPI:51764890230

# Issuer Name (CN) da CA - usado para validação
# IMPORTANTE: Use o CN CORRETO da CA (AC Certisign RFB G5, não "Múltipla G5")
CERT_ISSUER_CN=AC Certisign RFB G5

# ===== AUTENTICAÇÃO CAS (CPF/SENHA) =====
# Deixar vazio para usar APENAS certificado digital
# Se preencher, o sistema tentará login com CPF/senha primeiro
CAS_USUARIO=
CAS_SENHA=
EOF

# Verificar arquivo criado
echo "=== Novo .env ==="
cat .env

# Restart worker (sem rebuild)
docker compose restart worker

# Resetar 2 jobs para teste
PGPASSWORD="BetaAgent2024SecureDB" psql -h 72.60.62.124 -p 5432 -U admin -d n8n -c \
  "UPDATE consultas_esaj SET status = FALSE WHERE id IN (SELECT id FROM consultas_esaj WHERE status = TRUE ORDER BY id DESC LIMIT 2);"

# Monitorar logs
docker compose logs -f worker
```

---

## 📋 VALORES CORRETOS DO CERTIFICADO

Extraídos via `certutil` em 2025-10-02:

```
Subject: CN=FLAVIO EDUARDO CAPPI:51764890230
Issuer: CN=AC Certisign RFB G5
Serial Number: 13:7a:6a:b8:a6:b1:e7:81:b0:d6:45:f9:6a:cf:ef:63
Validade: 2025-09-09 até 2026-09-09
Tipo: RFB e-CPF A1
```

---

## ⚠️ IMPORTANTE

- O `.env` **NÃO** deve ser commitado no Git (contém senhas)
- Use o `.env.example` como template (commitado no Git)
- Sempre copie do `.env.example` e ajuste os valores reais
