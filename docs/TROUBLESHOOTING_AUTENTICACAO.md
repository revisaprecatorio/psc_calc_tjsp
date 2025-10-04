# 🔐 TROUBLESHOOTING - AUTENTICAÇÃO e-SAJ

**Data:** 2025-10-01  
**Objetivo:** Guia completo para resolver problemas de autenticação no Portal e-SAJ

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Métodos de Autenticação](#métodos-de-autenticação)
3. [Problemas Comuns](#problemas-comuns)
4. [Checklist de Validação](#checklist-de-validação)
5. [Testes Manuais](#testes-manuais)
6. [Configuração no Crawler](#configuração-no-crawler)

---

## 🎯 VISÃO GERAL

O Portal e-SAJ do TJSP oferece **DOIS métodos independentes** de autenticação:

### **Método 1: CPF/CNPJ + Senha**
- ✅ **Mais simples** para automação
- ✅ Funciona sem certificado digital
- ✅ Requer apenas credenciais válidas
- ⚠️ Pode ter 2FA (código por email)

### **Método 2: Certificado Digital**
- ❌ **Complexo** para automação
- ❌ Requer plugin Web Signer instalado
- ❌ Selenium Grid não suporta nativamente
- ⚠️ **AINDA PRECISA** de senha do Portal e-SAJ

---

## 🔑 MÉTODOS DE AUTENTICAÇÃO

### **1. Login com CPF/CNPJ + Senha**

**URL:** https://esaj.tjsp.jus.br/sajcas/login

**Passos:**
1. Acessar página de login
2. Clicar na aba "CPF/CNPJ"
3. Preencher CPF/CNPJ (com ou sem formatação)
4. Preencher senha do Portal e-SAJ
5. Clicar em "Entrar"
6. Se tiver 2FA: inserir código enviado por email

**Requisitos:**
- ✅ CPF/CNPJ cadastrado no Portal e-SAJ
- ✅ Senha do Portal (não confundir com senha do certificado)
- ✅ Perfil adequado (advogado, para acessar processos)
- ✅ Email cadastrado (para 2FA, se habilitado)

---

### **2. Login com Certificado Digital**

**URL:** https://esaj.tjsp.jus.br/sajcas/login

**Passos:**
1. Acessar página de login
2. Clicar na aba "Certificado digital"
3. **Instalar plugin Web Signer** (obrigatório)
4. Selecionar certificado da lista
5. **Informar senha do Portal e-SAJ** (sim, precisa!)
6. Clicar em "Entrar"

**Requisitos:**
- ✅ Certificado digital válido (e-CPF ou e-CNPJ)
- ✅ Plugin Web Signer instalado no navegador
- ✅ **Senha do Portal e-SAJ** (mesmo com certificado!)
- ✅ CPF do certificado cadastrado no Portal
- ✅ Perfil adequado (advogado)

**Limitações no Selenium Grid:**
- ❌ Web Signer não funciona em containers Docker
- ❌ Certificado não pode ser carregado automaticamente
- ❌ Não recomendado para automação

---

## ⚠️ PROBLEMAS COMUNS

### **Problema 1: "Usuário ou senha inválidos"**

**Causas Possíveis:**

1. **CPF não cadastrado no Portal e-SAJ**
   - Solução: Fazer cadastro em https://esaj.tjsp.jus.br/esajperfil/

2. **Senha incorreta**
   - ⚠️ **ATENÇÃO:** Não confundir:
     - Senha do certificado `.pfx` (ex: 903205)
     - Senha do Portal e-SAJ (cadastrada pelo usuário)
   - Solução: Recuperar senha em "Esqueci minha senha"

3. **Conta não ativada**
   - Solução: Verificar email de ativação

4. **Senha expirada**
   - Solução: Redefinir senha

**Como Validar:**
```bash
# Teste manual no navegador
1. Acesse: https://esaj.tjsp.jus.br/sajcas/login
2. Aba "CPF/CNPJ"
3. Informe CPF e senha
4. Tente fazer login

Se funcionar manualmente → Credenciais estão corretas
Se falhar → Credenciais inválidas ou conta não existe
```

---

### **Problema 2: "Web Signer não instalado"**

**Causa:**
- Plugin Web Signer não está instalado no navegador

**Solução para Uso Manual:**
1. Acessar: https://websigner.lacunasoftware.com/
2. Baixar e instalar o plugin
3. Reiniciar navegador

**Solução para Automação:**
- ❌ **NÃO RECOMENDADO:** Web Signer não funciona em Docker
- ✅ **ALTERNATIVA:** Usar login com CPF/senha

---

### **Problema 3: Login funciona mas não acessa processos**

**Causa:**
- Conta não tem perfil de advogado ou permissões adequadas

**Sintomas:**
- Login bem-sucedido
- Entra no Portal e-SAJ
- Ao tentar consultar processos: erro de permissão

**Solução:**
1. Verificar perfil da conta no Portal
2. Solicitar habilitação de perfil adequado
3. Vincular OAB (para advogados)

---

### **Problema 4: 2FA (Código por Email)**

**Causa:**
- Conta tem autenticação de dois fatores habilitada

**Sintomas:**
- Após login, pede código de validação
- Código enviado para email cadastrado

**Solução para Automação:**
- ⚠️ **COMPLEXO:** Requer integração com email
- 💡 **ALTERNATIVA:** Desabilitar 2FA na conta (se possível)
- 💡 **ALTERNATIVA:** Usar conta sem 2FA para testes

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de configurar o crawler, validar:

### **Credenciais**
- [ ] CPF está cadastrado no Portal e-SAJ
- [ ] Senha do Portal está correta (não a senha do .pfx)
- [ ] Login manual funciona no navegador
- [ ] Conta tem perfil de advogado
- [ ] 2FA está desabilitado (ou configurado)

### **Testes Manuais**
- [ ] Acesso: https://esaj.tjsp.jus.br/sajcas/login
- [ ] Login com CPF/senha bem-sucedido
- [ ] Consegue acessar consulta de processos
- [ ] Consegue visualizar dados de processos

### **Configuração**
- [ ] `.env` atualizado com credenciais corretas
- [ ] `CAS_USUARIO` = CPF sem formatação (ex: 51764890230)
- [ ] `CAS_SENHA` = Senha do Portal e-SAJ
- [ ] Variáveis lidas pelo docker-compose

---

## 🧪 TESTES MANUAIS

### **Teste 1: Validar Credenciais**

```bash
# 1. Acessar Portal
URL: https://esaj.tjsp.jus.br/sajcas/login

# 2. Aba CPF/CNPJ
- CPF: [INFORMAR]
- Senha: [INFORMAR]

# 3. Resultado Esperado
✅ Login bem-sucedido
✅ Redireciona para Portal e-SAJ
✅ Mostra nome do usuário no canto superior direito

# 4. Se falhar
❌ "Usuário ou senha inválidos" → Credenciais incorretas
❌ Pede código 2FA → Conta tem 2FA habilitado
❌ Erro de permissão → Conta sem perfil adequado
```

---

### **Teste 2: Validar Acesso a Processos**

```bash
# 1. Após login bem-sucedido
URL: https://esaj.tjsp.jus.br/cpopg/open.do

# 2. Tentar consultar processo
- Número do Processo: [QUALQUER PROCESSO DE TESTE]

# 3. Resultado Esperado
✅ Mostra dados do processo
✅ Consegue abrir autos
✅ Consegue baixar PDFs

# 4. Se falhar
❌ "Sem permissão" → Conta não tem perfil adequado
❌ "Processo não encontrado" → Número inválido (normal)
❌ Redireciona para login → Sessão expirou
```

---

## ⚙️ CONFIGURAÇÃO NO CRAWLER

### **Arquivo: `.env`**

```bash
# ===== AUTENTICAÇÃO CAS (CPF/SENHA) =====
# CPF sem formatação (apenas números)
CAS_USUARIO=51764890230

# Senha do Portal e-SAJ (NÃO a senha do certificado .pfx)
CAS_SENHA=SUA_SENHA_AQUI

# ===== CERTIFICADO DIGITAL (OPCIONAL) =====
# Apenas se for usar certificado (não recomendado)
# CERT_PATH=/app/certs/certificado.pfx
# CERT_PASSWORD=903205
# CERT_SUBJECT_CN=517.648.902-30
```

---

### **Validar Configuração**

```bash
# Na VPS
cd /opt/crawler_tjsp

# 1. Verificar .env
cat .env | grep CAS

# 2. Verificar docker-compose lê as variáveis
docker compose config | grep CAS

# 3. Verificar container recebe as variáveis
docker exec tjsp_worker_1 env | grep CAS
```

---

### **Testar Autenticação**

```bash
# 1. Resetar 1 job
psql -h 72.60.62.124 -U admin -d n8n -c "
UPDATE consultas_esaj SET status = FALSE WHERE id = 28;"

# 2. Monitorar logs
docker compose logs -f worker

# 3. Logs Esperados (SUCESSO)
[INFO] Conectando ao Selenium Grid: http://selenium-chrome:4444
[INFO] ✅ Conectado ao Selenium Grid com sucesso!
CAS: tentando login com CPF/CNPJ…
CAS: login CPF/CNPJ OK.

# 4. Logs de Erro (FALHA)
CAS: tentando login com CPF/CNPJ…
CAS: falha no login CPF/CNPJ.
RuntimeError: CAS: autenticação necessária e não realizada.
```

---

## 📞 CONTATO COM DETENTOR DO CERTIFICADO

### **Perguntas a Fazer:**

1. **Cadastro no Portal:**
   - O CPF 517.648.902-30 está cadastrado no Portal e-SAJ?
   - Já fez login alguma vez?
   - Qual o email cadastrado?

2. **Senha:**
   - Qual a senha do Portal e-SAJ?
   - ⚠️ **NÃO** é a senha do certificado .pfx (903205)
   - É a senha cadastrada no site

3. **Perfil:**
   - A conta tem perfil de advogado?
   - Tem OAB vinculada?
   - Consegue acessar processos manualmente?

4. **2FA:**
   - A conta tem autenticação de dois fatores?
   - Se sim, pode desabilitar para testes?

5. **Teste Manual:**
   - Pode fazer um teste de login manual agora?
   - URL: https://esaj.tjsp.jus.br/sajcas/login
   - Confirmar se login funciona

---

## 📊 RESUMO EXECUTIVO

### **O Que Funciona:**
- ✅ Selenium Grid operacional
- ✅ Código preparado para login CPF/senha
- ✅ Sistema de autenticação do e-SAJ testado
- ✅ Login manual com CPF pessoal funcionou

### **O Que NÃO Funciona:**
- ❌ Credenciais do certificado (CPF 517.648.902-30)
- ❌ Senha 903205 inválida ou conta não cadastrada

### **Próximos Passos:**
1. ⏸️ Validar credenciais com detentor do certificado
2. 🧪 Testar login manual com credenciais corretas
3. ⚙️ Atualizar `.env` com credenciais válidas
4. 🚀 Deploy e teste automatizado
5. ✅ Validar acesso aos processos

---

**Última Atualização:** 2025-10-01 20:30:00
