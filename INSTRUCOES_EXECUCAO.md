# 🚀 Instruções de Execução - Teste de Autenticação (Windows Server)

**Data:** 2025-10-05
**Versão:** 1.0
**Objetivo:** Executar teste de autenticação com certificado digital no Windows Server

---

## 📋 Pré-requisitos

Antes de executar o teste, certifique-se de que:

- [x] Windows Server 2016 Datacenter operacional
- [x] RDP configurado e funcionando (62.171.143.88)
- [x] Python 3.12.3 instalado e no PATH
- [x] Git instalado
- [x] Chrome instalado (v131.0.6778.86)
- [x] ChromeDriver instalado (C:\chromedriver\chromedriver.exe)
- [x] Web Signer instalado e rodando
- [x] Certificado A1 importado no Windows Certificate Store
- [x] Repositório clonado em `C:\projetos\crawler_tjsp`
- [x] Virtual environment criado (`.venv`)
- [x] Dependências instaladas (`requirements.txt`)
- [x] Arquivo `.env` configurado

---

## 🔄 Passo 1: Atualizar Código do GitHub

Conecte-se ao Windows Server via RDP e execute os comandos abaixo no PowerShell:

```powershell
# Navegar para o diretório do projeto
cd C:\projetos\crawler_tjsp

# Atualizar código com correção de perfil Chrome
git pull origin main
```

**Saída esperada:**
```
Updating 069eec8..9c0bae7
Fast-forward
 windows-server/scripts/test_authentication.py | 23 +++++++++++++++--------
 windows-server/CHROME_PROFILE_FIX.md          | 250 +++++++++++++++++++++++++
 windows-server/README.md                      | 45 +++--
 windows-server/MIGRATION_CHECKLIST.md         | 98 ++++++----
 ...
 44 files changed, 1128 insertions(+), 235 deletions(-)
```

✅ **Confirmação:** Código atualizado com correção de perfil Chrome!

---

## 🐍 Passo 2: Ativar Virtual Environment

```powershell
# Ativar virtual environment
.\.venv\Scripts\Activate.ps1
```

**Saída esperada:**
```
(.venv) PS C:\projetos\crawler_tjsp>
```

✅ **Confirmação:** Ambiente virtual ativado (prefixo `.venv` aparece no prompt).

---

## 🧪 Passo 3: Executar Teste de Autenticação

```powershell
# Executar script de teste
python windows-server\scripts\test_authentication.py
```

### O Que Vai Acontecer?

1. **Banner inicial:**
   ```
   ============================================================
   TESTE DE AUTENTICAÇÃO - CRAWLER TJSP
   Windows Server - Validação de Native Messaging
   ============================================================

   ⚠️  IMPORTANTE:
      - Certifique-se de que Web Signer está rodando
      - Certifique-se de que certificado está importado
      - Você precisará selecionar o certificado manualmente

   Pressione Enter para iniciar o teste...
   ```

2. **Aguarde a mensagem e pressione `Enter`**

3. **Chrome vai abrir:**
   - Com o perfil padrão (revisa.precatorio@gmail.com)
   - Extensão Web Signer estará disponível! ✅
   - Página do e-SAJ será carregada

4. **Modal Web Signer abrirá automaticamente:**
   - Após clicar no botão "Certificado Digital"
   - Você verá lista de certificados disponíveis
   - Selecione o certificado correto

5. **Login será processado:**
   - Após seleção do certificado
   - Aguarde redirecionamento para painel autenticado

6. **Script capturará resultado:**
   - Screenshots salvos em `C:\projetos\crawler_tjsp\screenshots\`
   - Logs salvos em `C:\projetos\crawler_tjsp\logs\test_auth.log`

---

## ✅ Resultado Esperado (SUCESSO)

### Saída no Console

```
[2025-10-05 15:30:00] [INFO] ============================================================
[2025-10-05 15:30:00] [INFO] TESTE DE AUTENTICAÇÃO - e-SAJ TJSP
[2025-10-05 15:30:00] [INFO] ============================================================
[2025-10-05 15:30:01] [INFO] 🔧 Configurando Chrome...
[2025-10-05 15:30:01] [INFO]   ✅ Usando perfil padrão do Chrome (onde Web Signer está instalado)
[2025-10-05 15:30:05] [INFO]   ✅ Chrome iniciado com sucesso!
[2025-10-05 15:30:05] [INFO] 🌐 Acessando e-SAJ...
[2025-10-05 15:30:08] [INFO]   ✅ Página carregada: e-SAJ - Tribunal de Justiça do Estado de São Paulo
[2025-10-05 15:30:08] [INFO] 📸 Screenshot salvo: C:\projetos\crawler_tjsp\screenshots\01_esaj_homepage_20251005_153008.png
[2025-10-05 15:30:08] [INFO]   ✅ Página e-SAJ carregada corretamente
[2025-10-05 15:30:09] [INFO] 🔍 Procurando botão 'Certificado Digital'...
[2025-10-05 15:30:10] [INFO]   ✅ Botão 'Certificado Digital' encontrado!
[2025-10-05 15:30:10] [INFO] 🖱️  Clicando em 'Certificado Digital'...
[2025-10-05 15:30:12] [INFO] 📸 Screenshot salvo: C:\projetos\crawler_tjsp\screenshots\03_after_click_cert_20251005_153012.png
[2025-10-05 15:30:12] [INFO] ============================================================
[2025-10-05 15:30:12] [INFO] ⏳ AGUARDANDO WEB SIGNER ABRIR MODAL DE SELEÇÃO...
[2025-10-05 15:30:12] [INFO] ============================================================
[2025-10-05 15:30:12] [INFO] ℹ️  Neste momento, o Native Messaging Protocol será testado:
[2025-10-05 15:30:12] [INFO]    1. Extensão Chrome → envia mensagem → Web Signer
[2025-10-05 15:30:12] [INFO]    2. Web Signer → abre modal nativo → usuário seleciona certificado
[2025-10-05 15:30:12] [INFO]    3. Web Signer → retorna certificado → Extensão Chrome
[2025-10-05 15:30:12] [INFO]    4. Login bem-sucedido no e-SAJ
[2025-10-05 15:30:12] [INFO]
[2025-10-05 15:30:12] [INFO] ⚠️  AÇÃO NECESSÁRIA:
[2025-10-05 15:30:12] [INFO]    - Modal do Web Signer deve aparecer automaticamente
[2025-10-05 15:30:12] [INFO]    - Selecione o certificado na lista
[2025-10-05 15:30:12] [INFO]    - Aguarde redirecionamento
[2025-10-05 15:30:12] [INFO]
[2025-10-05 15:30:12] [INFO] ⏱️  Aguardando 30 segundos para seleção do certificado...
[... VOCÊ SELECIONA O CERTIFICADO NO MODAL ...]
[2025-10-05 15:30:42] [INFO] 🔍 Verificando se login foi bem-sucedido...
[2025-10-05 15:30:42] [INFO]   URL atual: https://esaj.tjsp.jus.br/esaj/portal.do?servico=190000
[2025-10-05 15:30:42] [INFO] ============================================================
[2025-10-05 15:30:42] [SUCCESS] ✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO! ✅✅✅
[2025-10-05 15:30:42] [INFO] ============================================================
[2025-10-05 15:30:42] [INFO] URL pós-login: https://esaj.tjsp.jus.br/esaj/portal.do?servico=190000
[2025-10-05 15:30:42] [INFO] 📸 Screenshot salvo: C:\projetos\crawler_tjsp\screenshots\04_login_success_20251005_153042.png
[2025-10-05 15:30:42] [INFO]
[2025-10-05 15:30:42] [INFO] 🎉 RESULTADO DO TESTE: SUCESSO! 🎉
[2025-10-05 15:30:42] [INFO] ✅ Native Messaging Protocol funcionou corretamente!
[2025-10-05 15:30:42] [INFO] ✅ Web Signer comunicou com extensão Chrome!
[2025-10-05 15:30:42] [INFO] ✅ Autenticação via certificado digital operacional!
[2025-10-05 15:30:42] [INFO]
[2025-10-05 15:30:42] [INFO] 📋 Próximos passos:
[2025-10-05 15:30:42] [INFO]    1. Configurar orchestrator_subprocess.py
[2025-10-05 15:30:42] [INFO]    2. Criar Windows Service
[2025-10-05 15:30:42] [INFO]    3. Testar crawler_full.py completo
[2025-10-05 15:30:42] [INFO]    4. Iniciar processamento de jobs
[2025-10-05 15:30:42] [INFO]
[2025-10-05 15:30:52] [INFO] 🔒 Fechando Chrome...
[2025-10-05 15:30:53] [INFO]   ✅ Chrome fechado
[2025-10-05 15:30:53] [INFO] ============================================================
[2025-10-05 15:30:53] [INFO] TESTE FINALIZADO: SUCESSO
[2025-10-05 15:30:53] [INFO] ============================================================
[2025-10-05 15:30:53] [INFO] 📝 Log completo: C:\projetos\crawler_tjsp\logs\test_auth.log
[2025-10-05 15:30:53] [INFO] 📸 Screenshots: C:\projetos\crawler_tjsp\screenshots

✅ TESTE PASSOU! Migração para Windows foi bem-sucedida!
```

---

## ❌ Resultado Esperado (FALHA)

Se o teste falhar, você verá:

```
[2025-10-05 15:30:42] [INFO] ============================================================
[2025-10-05 15:30:42] [ERROR] ❌ LOGIN FALHOU OU AINDA NA TELA DE AUTENTICAÇÃO
[2025-10-05 15:30:42] [INFO] ============================================================
[2025-10-05 15:30:42] [INFO] URL esperada: https://esaj.tjsp.jus.br/esaj/portal.do?servico=...
[2025-10-05 15:30:42] [INFO] URL obtida:   https://esaj.tjsp.jus.br/esaj/portal.do
[2025-10-05 15:30:42] [INFO] 📸 Screenshot salvo: C:\projetos\crawler_tjsp\screenshots\04_login_failed_20251005_153042.png

❌ RESULTADO DO TESTE: FALHA
Possíveis causas:
   1. Modal do Web Signer não abriu (Native Messaging falhou)
   2. Certificado não foi selecionado
   3. Certificado expirado ou inválido
   4. Web Signer não está rodando
   5. Extensão não está carregada no Chrome

🔧 Troubleshooting:
   - Verificar se Web Signer está rodando (bandeja do sistema)
   - Verificar extensão em chrome://extensions/
   - Verificar certificado em certmgr.msc
   - Tentar login manual para comparar comportamento
```

### Passos de Troubleshooting

1. **Verificar Web Signer rodando:**
   ```powershell
   Get-Process | Where-Object {$_.Name -like "*WebSigner*"}
   ```

2. **Verificar extensão Chrome:**
   - Abrir Chrome manualmente
   - Acessar `chrome://extensions/`
   - Confirmar que Web Signer está habilitado

3. **Verificar certificado:**
   ```powershell
   certmgr.msc
   ```
   - Personal → Certificates
   - Confirmar certificado presente com chave privada

4. **Verificar logs detalhados:**
   ```powershell
   Get-Content C:\projetos\crawler_tjsp\logs\test_auth.log -Tail 50
   ```

---

## 📊 Arquivos Gerados

Após execução bem-sucedida:

```
C:\projetos\crawler_tjsp\
├── logs\
│   └── test_auth.log                         # Log completo do teste
├── screenshots\
│   ├── 01_esaj_homepage_20251005_153008.png  # Homepage e-SAJ
│   ├── 03_after_click_cert_20251005_153012.png  # Após clicar em "Certificado Digital"
│   └── 04_login_success_20251005_153042.png  # Login bem-sucedido
└── downloads\                                # (criado automaticamente)
```

---

## 🎉 Próximos Passos Após Sucesso

Se o teste passar com sucesso:

1. **Marcar Fase 5 como concluída:**
   - Atualizar [MIGRATION_CHECKLIST.md](windows-server/MIGRATION_CHECKLIST.md)

2. **Avançar para Fase 6 (Worker):**
   - Configurar `orchestrator_subprocess.py`
   - Criar Windows Service
   - Testar processamento de fila

3. **Avançar para Fase 7 (Produção):**
   - Configurar logs rotativos
   - Configurar monitoramento
   - Iniciar operação em produção

4. **Atualizar documentação:**
   - Atualizar [README.md](windows-server/README.md) com status ✅
   - Documentar tempo real de cada fase

---

## 📞 Suporte

### Documentação Relacionada

- [CHROME_PROFILE_FIX.md](windows-server/CHROME_PROFILE_FIX.md) - Explicação da correção aplicada
- [MIGRATION_CHECKLIST.md](windows-server/MIGRATION_CHECKLIST.md) - Checklist completo de migração
- [README.md](windows-server/README.md) - Visão geral do projeto Windows Server

### Troubleshooting Adicional

- **Chrome não abre:** Verificar ChromeDriver compatível com versão do Chrome
- **Extensão não aparece:** Verificar se perfil correto está sendo usado (não Default)
- **Modal não abre:** Verificar se Web Signer está rodando (bandeja do sistema)
- **Certificado não aparece:** Verificar se está em Personal (não em Trusted Root)

---

## ✅ Checklist Final

Antes de declarar sucesso, confirme:

- [ ] Chrome abriu com perfil `revisa.precatorio@gmail.com` (não "Default")
- [ ] Extensão Web Signer aparece em `chrome://extensions/`
- [ ] Modal Web Signer abriu automaticamente
- [ ] Certificado foi selecionado e autenticado
- [ ] URL mudou para `https://esaj.tjsp.jus.br/esaj/portal.do?servico=...`
- [ ] Screenshot `04_login_success_*.png` mostra painel autenticado
- [ ] Log `test_auth.log` contém mensagem "LOGIN COM CERTIFICADO BEM-SUCEDIDO"

---

**Última atualização:** 2025-10-05
**Responsável:** Persival Balleste
**Status:** ✅ Pronto para execução

**BOA SORTE! 🚀**
