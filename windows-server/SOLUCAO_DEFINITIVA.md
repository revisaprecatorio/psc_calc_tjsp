# SOLUÇÃO DEFINITIVA - Crawler TJSP Windows Server

**Data:** 2025-10-06
**Status:** ✅✅✅ SOLUÇÃO IMPLEMENTADA E TESTADA COM SUCESSO!

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

## ✅ SOLUÇÃO DEFINITIVA - COOKIE INJECTION

### Estratégia: Exportar Cookies Manualmente + Injetar no Selenium

#### ETAPA 1: Login Manual + Exportar Cookies (5 minutos, 1x por semana)
```powershell
# 1. Abrir Chrome no perfil Default
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="Default"

# 2. Acessar e-SAJ e fazer login com certificado
# https://esaj.tjsp.jus.br/esaj/portal.do

# 3. Instalar extensão "Cookie Editor" (cookieeditor.org)
# https://chromewebstore.google.com/detail/cookie-editor/cgfpcedhhilpcknohkgikfkecjgjmofo

# 4. Com e-SAJ aberto e logado, clicar na extensão Cookie Editor
# 5. Clicar no botão "Export" (terceiro ícone)
# 6. Copiar JSON gerado
```

**Resultado:** JSON com cookies da sessão autenticada copiado

#### ETAPA 2: Importar Cookies para Selenium
```powershell
# 1. Colar JSON em: C:\projetos\crawler_tjsp\cookies_export.json

# 2. Executar script de importação
cd C:\projetos\crawler_tjsp
python windows-server/scripts/import_cookies_from_json.py

# Resultado: Cookies convertidos para formato Selenium
# Salvos em: C:\projetos\crawler_tjsp\saved_cookies\esaj_cookies.pkl
```

#### ETAPA 3: Testar Autenticação com Cookies
```powershell
# Executar teste
python windows-server/scripts/test_with_cookies.py

# ✅ Resultado esperado: Acesso à área logada SEM certificado!
```

---

## 🔧 IMPLEMENTAÇÃO

### ✅ Scripts Desenvolvidos e Testados

#### 1. import_cookies_from_json.py
- **Função:** Converte cookies exportados (JSON) → formato Selenium (pickle)
- **Input:** `cookies_export.json` (JSON da extensão Cookie Editor)
- **Output:** `saved_cookies/esaj_cookies.pkl` (formato Selenium)
- **Status:** ✅ Funcionando

#### 2. test_with_cookies.py
- **Função:** Testa autenticação com cookies injetados
- **Processo:**
  1. Inicia Selenium com Chrome
  2. Carrega cookies do arquivo pickle
  3. Acessa e-SAJ
  4. Valida se está autenticado
- **Status:** ✅ Teste passou com sucesso!

#### 3. extract_cookies.py (DEPRECATED)
- **Status:** ❌ Não funciona no Windows Server
- **Problema:** SQLite do Chrome não permite leitura de cookies
- **Substituído por:** Exportação manual via extensão Cookie Editor

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

1. ✅ Implementar `import_cookies_from_json.py`
2. ✅ Implementar `test_with_cookies.py`
3. ✅ Testar login manual + extração via Cookie Editor
4. ✅ Validar autenticação com cookies injetados (TESTE PASSOU!)
5. ⏳ Integrar solução com `crawler_full.py`
6. ⏳ Implementar detecção de expiração de cookies
7. ⏳ Criar procedimento de renovação de cookies
8. ⏳ Documentar procedimento de manutenção
9. ⏳ Testar extração de dados de processos reais

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
**Última Atualização:** 2025-10-06 05:30
**Status:** ✅ Solução implementada e testada com sucesso!

---

## 🎉 RESULTADO FINAL

```
✅✅✅ SUCESSO! AUTENTICAÇÃO COM COOKIES FUNCIONOU! ✅✅✅

🎯 Cookie injection funcionou!
🎯 Acesso à área logada sem certificado!
🎯 Sessão mantida com sucesso!

Teste executado em: 2025-10-06 05:22:50
Log: C:\projetos\crawler_tjsp\logs\test_cookies.log
Screenshots: C:\projetos\crawler_tjsp\screenshots\02_authenticated_success_20251006_052250.png
```
