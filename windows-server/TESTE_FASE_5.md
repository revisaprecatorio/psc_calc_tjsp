# 🧪 Testes de Validação - Fase 5

**Data:** 2025-10-05
**Versão:** 2.0
**Objetivo:** Executar dois testes de validação no Windows Server

---

## 📋 Resumo dos Testes

| # | Script | Objetivo | Duração | Resultado Esperado |
|---|--------|----------|---------|-------------------|
| 1 | `test_authentication.py` | Login com certificado | ~2 min | ✅ Login bem-sucedido |
| 2 | `test_direct_process_access.py` | Acesso direto a processo | ~3 min | ✅ Dados do processo carregados |

---

## 🎯 TESTE #1: Autenticação com Certificado

### Objetivo

Validar que Native Messaging Protocol funciona no Windows Server e login com certificado digital é bem-sucedido.

### Como Executar

```powershell
# No Windows Server (via RDP)
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1
python windows-server\scripts\test_authentication.py
```

### O Que Acontece

1. Chrome abre com perfil padrão (revisa.precatorio@gmail.com)
2. Portal e-SAJ carrega
3. Botão "Certificado Digital" é clicado
4. **Modal Web Signer abre** (Native Messaging funcionando!)
5. **Você seleciona o certificado**
6. Login bem-sucedido, URL muda para área autenticada

### Resultado Esperado (Sucesso)

```
[2025-10-05 15:30:42] [SUCCESS] ✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO! ✅✅✅
[2025-10-05 15:30:42] [INFO] URL pós-login: https://esaj.tjsp.jus.br/esaj/portal.do?servico=190000

✅ TESTE PASSOU! Migração para Windows foi bem-sucedida!
```

**Screenshots salvos em:** `C:\projetos\crawler_tjsp\screenshots\`
- `01_esaj_homepage_*.png`
- `03_after_click_cert_*.png`
- `04_login_success_*.png`

---

## 🎯 TESTE #2: Acesso Direto a Processo (Sessão Mantida)

### Objetivo

Validar que após login, podemos acessar processos diretamente sem re-autenticar.

**IMPORTANTE:** Se este teste passar, significa que o crawler pode processar múltiplos jobs na mesma sessão, aumentando performance drasticamente!

### Como Executar

```powershell
# No Windows Server (via RDP)
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1
python windows-server\scripts\test_direct_process_access.py
```

### O Que Acontece

**ETAPA 1: Login com certificado** (igual ao Teste #1)
1. Chrome abre
2. Login com certificado
3. Sessão autenticada estabelecida

**ETAPA 2: Acesso direto a processo**
4. Navegação direta para URL do processo: `0077044-50.2023.8.26.0500`
5. Verificação se sessão foi mantida (não redireciona para login)
6. Extração de dados do processo:
   - Número do processo
   - Classe: Precatório
   - Assunto: Aposentadoria
   - Requerente: Antonio Augusto de Almeida
   - Movimentações
   - Partes

### Resultado Esperado (Sucesso)

```
ETAPA 2: ACESSO DIRETO A PROCESSO (SESSÃO AUTENTICADA)
======================================================================
🌐 Acessando processo: 0077044-50.2023.8.26.0500
  ✅ Página carregada: e-SAJ - TJSP
  URL atual: https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo=...

🔍 Verificando elementos da página do processo...
  ✅ Número do processo encontrado: 0077044-50.2023.8.26.0500
  ✅ Classe encontrada: Precatório
  ✅ Assunto encontrado: Aposentadoria
  ✅ Requerente encontrado: Antonio Augusto de Almeida
  ✅ Tabela de Movimentações encontrada
  ✅ Tabela de Partes encontrada

======================================================================
RESULTADO: 6/6 verificações passaram
======================================================================
✅✅✅ ACESSO DIRETO FUNCIONOU PERFEITAMENTE! ✅✅✅

🎉 CONCLUSÃO:
   ✅ Sessão autenticada foi mantida
   ✅ Acesso direto a processos funciona
   ✅ Crawler pode processar múltiplos jobs na mesma sessão
   ✅ Performance será otimizada (não precisa re-autenticar)
```

**Screenshots salvos em:** `C:\projetos\crawler_tjsp\screenshots\`
- `05_processo_loaded_*.png`
- `05_processo_html_*.html` (HTML completo para análise)

---

## 💡 Por Que Teste #2 É Importante?

### Cenário 1: Sem Sessão Mantida (❌ Ruim)

```
Job 1: Login → Extrair → Logout (2 min)
Job 2: Login → Extrair → Logout (2 min)
Job 3: Login → Extrair → Logout (2 min)
...
100 jobs = 200 minutos (3h 20min)
```

### Cenário 2: Com Sessão Mantida (✅ Ótimo!)

```
Login → Extrair Job 1 → Extrair Job 2 → Extrair Job 3 → ... → Extrair Job 100 (30 min)
```

**Ganho de performance: 6x mais rápido!** 🚀

---

## 🔄 Ordem de Execução Recomendada

### Primeira Vez (Validação Completa)

1. **Execute TESTE #1** (`test_authentication.py`)
   - Valida Native Messaging funcionando
   - Valida login com certificado

2. **Se TESTE #1 passar, execute TESTE #2** (`test_direct_process_access.py`)
   - Valida sessão mantida
   - Valida acesso direto a processos

### Execuções Subsequentes

Você pode executar **apenas TESTE #2**, pois ele já inclui o login (TESTE #1) e valida acesso direto.

---

## ✅ Checklist de Pré-requisitos

Antes de executar os testes, confirme:

- [x] Windows Server 2016 operacional (62.171.143.88)
- [x] Python 3.12.3 instalado
- [x] Chrome v131.0.6778.86 instalado
- [x] ChromeDriver instalado (C:\chromedriver\)
- [x] Web Signer instalado e **RODANDO** (ícone na bandeja)
- [x] Certificado A1 importado no Windows Certificate Store
- [x] Repositório atualizado (`git pull origin main`)
- [x] Virtual environment ativado (`.venv`)

---

## 🚨 Troubleshooting

### Teste #1 Falha: Modal Web Signer Não Abre

**Causa:** Web Signer não está rodando ou extensão não carregada

**Solução:**
```powershell
# Verificar se Web Signer está rodando
Get-Process | Where-Object {$_.Name -like "*WebSigner*"}

# Se não estiver, iniciar manualmente
Start-Process "C:\Program Files\Softplan\WebSigner\WebSigner.exe"
```

### Teste #2 Falha: Redirecionado para Login

**Causa:** Sessão não foi mantida (cookies perdidos)

**Possíveis razões:**
1. Timeout de sessão do e-SAJ (muito tempo entre login e acesso)
2. Chrome não está usando perfil correto
3. Cookies foram bloqueados

**Solução:**
- Executar teste mais rápido (sem pausas longas)
- Verificar se Chrome está usando perfil padrão (não Default)
- Verificar configurações de cookies do Chrome

### Teste #2 Falha: Elementos Não Encontrados

**Causa:** HTML da página mudou ou seletores incorretos

**Solução:**
- Analisar HTML salvo em `05_processo_html_*.html`
- Comparar com HTML esperado
- Ajustar seletores no script se necessário

---

## 📊 Arquivos Gerados

Após execução dos testes:

```
C:\projetos\crawler_tjsp\
├── logs\
│   ├── test_auth.log              # Log do Teste #1
│   └── test_direct_access.log     # Log do Teste #2
├── screenshots\
│   ├── 01_esaj_homepage_*.png
│   ├── 03_after_click_cert_*.png
│   ├── 04_login_success_*.png
│   ├── 05_processo_loaded_*.png
│   └── 05_processo_html_*.html    # HTML completo do processo
└── downloads\
```

---

## 🎉 Próximos Passos Após Sucesso

Se ambos os testes passarem:

### ✅ Fase 5 Concluída!

1. **Marcar Fase 5 como concluída** no [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md)
2. **Atualizar [README.md](README.md)** com status ✅

### ⏭️ Avançar para Fase 6: Configuração do Worker

1. Adaptar `crawler_full.py` para usar sessão persistente
2. Configurar `orchestrator_subprocess.py`
3. Criar Windows Service
4. Testar processamento de fila

### ⏭️ Avançar para Fase 7: Produção

1. Configurar logs rotativos
2. Configurar monitoramento
3. Criar backup
4. Iniciar operação em produção

---

## 📞 Suporte

### Documentação Relacionada

- [CHROME_PROFILE_FIX.md](CHROME_PROFILE_FIX.md) - Solução de perfil Chrome
- [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md) - Checklist completo
- [README.md](README.md) - Visão geral do projeto

### Comandos Úteis

```powershell
# Ver logs em tempo real
Get-Content C:\projetos\crawler_tjsp\logs\test_auth.log -Tail 20 -Wait

# Verificar processos Chrome
Get-Process | Where-Object {$_.Name -like "*chrome*"}

# Matar Chrome (se travou)
Stop-Process -Name "chrome" -Force

# Ver screenshots
explorer C:\projetos\crawler_tjsp\screenshots
```

---

**Última atualização:** 2025-10-05
**Responsável:** Persival Balleste
**Status:** ✅ Pronto para execução

**BOA SORTE COM OS TESTES! 🚀**
