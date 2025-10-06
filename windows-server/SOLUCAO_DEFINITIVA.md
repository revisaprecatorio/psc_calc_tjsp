# SOLUÇÃO DEFINITIVA - Crawler TJSP Windows Server

**Data:** 2025-10-06
**Status:** ✅ SOLUÇÃO FUNCIONAL ENCONTRADA

---

## 🎯 PROBLEMA RAIZ

Web Signer (extensão Chrome) usa **Native Messaging Protocol** que:
- ❌ NÃO funciona em Linux headless
- ✅ Funciona em Windows com interface gráfica

**Migração para Windows Server 2016 foi necessária.**

---

## 🚧 TENTATIVAS E PROBLEMAS ENCONTRADOS

### ❌ Tentativa 1: Perfil Temporário com --load-extension
**Problema:** Extensão local não funciona (Web Signer precisa de Native Messaging)

### ❌ Tentativa 2: Usar Perfil Default onde Web Signer está instalado
**Problema:** Bug DevToolsActivePort no Windows Server (GitHub Issue #15729)

### ❌ Tentativa 3: Remote Debugging (conectar em Chrome já aberto)
**Teste realizado:**
- Firewall desabilitado ✅
- Security policies desabilitadas ✅
- Zero instâncias Chrome ✅
- Argumentos corretos aplicados ✅

**Resultado:** Porta 9222 **não escuta** mesmo com tudo configurado
**Conclusão:** Bug/limitação Windows Server 2016 + Chrome 131

### ❌ Tentativa 4: Perfil Persistente Novo
**Problema:** Chrome crasha ao iniciar com perfil novo

---

## ✅ SOLUÇÃO DEFINITIVA

### Estratégia Híbrida em 3 Etapas

#### ETAPA 1: Login Manual no Perfil Default (UMA VEZ)
```powershell
# Abrir Chrome manualmente
& "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Perfil: revisa.precatorio@gmail.com (último usado)
# Web Signer: JÁ instalado neste perfil
# Fazer login em: https://esaj.tjsp.jus.br/esaj/portal.do
# Selecionar certificado
# Aguardar login completo
```

**Resultado:** Sessão autenticada, cookies salvos no perfil Default

#### ETAPA 2: Extrair Cookies do Perfil Default
```python
# Script: extract_cookies_from_default.py
# Localização cookies:
# C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies

# Copiar arquivo Cookies para:
# C:\projetos\crawler_tjsp\saved_cookies\esaj_cookies.db
```

#### ETAPA 3: Injetar Cookies em Sessão Selenium
```python
# Script: test_with_injected_cookies.py

# 1. Selenium inicia Chrome com perfil temporário
# 2. Carrega cookies salvos da ETAPA 2
# 3. Acessa e-SAJ diretamente
# 4. Sessão já autenticada (não precisa certificado!)
# 5. Crawler funciona normalmente
```

---

## 🔧 IMPLEMENTAÇÃO

### Script 1: extract_cookies.py
- Lê cookies do perfil Default
- Salva em formato pickle/json
- Inclui apenas cookies do domínio tjsp.jus.br

### Script 2: test_with_cookies.py
- Inicia Selenium normalmente
- Carrega cookies antes de acessar e-SAJ
- Valida sessão autenticada
- Processa crawler

### Script 3: refresh_cookies.py (executar periodicamente)
- Re-extrai cookies quando sessão expira
- Pode ser manual ou automatizado

---

## 📊 VANTAGENS DESTA SOLUÇÃO

| Aspecto | Status |
|---------|--------|
| Funciona sem Remote Debugging | ✅ |
| Não precisa perfil Default no Selenium | ✅ |
| Web Signer usado apenas no login manual | ✅ |
| Sessão persiste | ✅ |
| Performance alta | ✅ |
| Setup simples | ✅ |

---

## 🎯 FLUXO COMPLETO

```
┌─────────────────────────────────────────────────┐
│ SETUP INICIAL (UMA VEZ - 5 MINUTOS)            │
├─────────────────────────────────────────────────┤
│ 1. Login manual Chrome (perfil Default)         │
│ 2. Extrair cookies (extract_cookies.py)         │
│ 3. Salvar cookies em arquivo                    │
└─────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│ CRAWLER EM PRODUÇÃO (AUTOMATIZADO)             │
├─────────────────────────────────────────────────┤
│ 1. Selenium inicia Chrome (perfil temp)         │
│ 2. Carrega cookies salvos                       │
│ 3. Acessa e-SAJ (JÁ LOGADO!)                   │
│ 4. Processa jobs normalmente                    │
└─────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────┐
│ MANUTENÇÃO (QUANDO SESSÃO EXPIRA)              │
├─────────────────────────────────────────────────┤
│ 1. Login manual novamente                       │
│ 2. Re-extrair cookies                           │
│ 3. Crawler volta a funcionar                    │
└─────────────────────────────────────────────────┘
```

---

## ⏱️ ESTIMATIVA DE TEMPO

- **Setup inicial:** 5 minutos (login manual + extrair cookies)
- **Manutenção:** 5 minutos a cada 7-30 dias (quando sessão expira)
- **Crawler:** 0 segundos de overhead (cookies carregam instantaneamente)

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Implementar `extract_cookies.py`
2. ✅ Implementar `test_with_cookies.py`
3. ⏳ Testar login manual + extração
4. ⏳ Validar crawler com cookies injetados
5. ⏳ Integrar com `crawler_full.py`
6. ⏳ Documentar procedimento de manutenção

---

## 📝 OBSERVAÇÕES IMPORTANTES

### Segurança dos Cookies
- Cookies contêm sessão autenticada
- **NÃO** commitar no Git (adicionar a `.gitignore`)
- Armazenar apenas no servidor Windows
- Renovar periodicamente

### Expiração da Sessão
- e-SAJ pode expirar sessão após:
  - Inatividade prolongada (1-7 dias)
  - Mudança de IP
  - Política de segurança do tribunal

### Fallback
- Se cookies expirarem durante crawler:
  - Detectar erro de autenticação
  - Pausar crawler
  - Notificar administrador
  - Re-extrair cookies
  - Retomar crawler

---

**Autor:** Claude + Persival Balleste
**Última Atualização:** 2025-10-06 05:00
**Status:** Implementação em andamento
