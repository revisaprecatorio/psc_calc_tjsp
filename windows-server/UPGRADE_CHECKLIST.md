# ✅ Checklist de Upgrade - Windows Server 2016 → 2025

**Data:** 2025-10-06  
**Servidor:** Contabo Cloud VPS 10 (62.171.143.88)  
**Sistema Atual:** Windows Server 2016 Datacenter  
**Sistema Destino:** Windows Server 2025  

---

## 📋 Pré-Upgrade: Backup Completo

### ✅ Checklist Obrigatória

Antes de fazer QUALQUER mudança, TODOS estes itens devem estar marcados:

```markdown
## 🔴 ITENS CRÍTICOS (NÃO PULE!)

### 1. Snapshot Contabo
- [ ] Acesso ao painel Contabo verificado (https://my.contabo.com)
- [ ] Snapshot criado com sucesso
- [ ] Nome do snapshot: pre-upgrade-to-ws2025-2025-10-06
- [ ] Status do snapshot: "Completed"
- [ ] Snapshot ID anotado: ________________________
- [ ] Data/hora do snapshot: ________________________

### 2. Backup Automático
- [ ] Script backup_complete_system.ps1 executado
- [ ] Status: "✅ BACKUP CONCLUÍDO COM SUCESSO!"
- [ ] Arquivo ZIP criado: BACKUP_COMPLETO_PRE_UPGRADE_*.zip
- [ ] Tamanho do ZIP: _______ GB
- [ ] Hash MD5 calculado: ________________________
- [ ] Arquivo .md5 criado

### 3. Transferência de Backup
- [ ] ZIP transferido para computador local
- [ ] Localização local: ~/Downloads/ (ou: ______________)
- [ ] Hash MD5 validado (local == servidor): ✅
- [ ] Tamanho do arquivo local corresponde ao servidor: ✅

### 4. Redundância de Backup
- [ ] Cópia em computador local: ✅
- [ ] Cópia em HD externo: ☐
- [ ] Upload para Google Drive/Dropbox: ☐
- [ ] Pelo menos 2 locais diferentes: ☐

### 5. Certificado Digital
- [ ] Arquivo certificado.pfx em C:\certs\certificado.pfx: ✅
- [ ] Certificado exportado (dentro do backup ZIP): ✅
- [ ] Senha do certificado anotada: 903205
- [ ] Certificado validado (HasPrivateKey=True): ✅

### 6. Documentação
- [ ] BACKUP_MANIFEST.txt gerado: ✅
- [ ] BACKUP_GUIDE.md lido e entendido: ✅
- [ ] RESTORE_GUIDE.md disponível: ✅
- [ ] QUICK_BACKUP.md consultado: ✅

## 🟡 ITENS RECOMENDADOS

### 7. Testes de Validação
- [ ] Backup ZIP pode ser descompactado sem erros
- [ ] Certificado pode ser importado em máquina de teste
- [ ] Arquivo .env é legível
- [ ] BACKUP_MANIFEST.txt contém todas as informações

### 8. Estado do Sistema Atual
- [ ] Código atualizado (último commit): ________________________
- [ ] Branch Git: main
- [ ] Virtual environment funcionando: ✅
- [ ] Teste test_authentication.py PASSOU (antes do backup): ☐
- [ ] PostgreSQL funcionando (se aplicável): ☐

### 9. Preparação para Upgrade
- [ ] Licença Windows Server 2025 adquirida: ☐
- [ ] Mídia de instalação/download preparada: ☐
- [ ] Tempo estimado alocado: 2-4 horas
- [ ] Horário de manutenção agendado: ________________________
```

---

## 🚀 Durante o Upgrade

### Método A: Upgrade In-Place (Preserva Dados)

```markdown
## Checklist Upgrade In-Place

1. PRÉ-UPGRADE
   - [ ] Todos os itens do checklist de backup marcados ✅
   - [ ] Snapshot Contabo ATIVO
   - [ ] Backup transferido e validado
   - [ ] Sistema estável (sem erros)

2. INICIAR UPGRADE
   - [ ] Mídia de instalação Windows Server 2025 montada
   - [ ] Opção "Keep files and apps" selecionada
   - [ ] Processo de upgrade iniciado
   - [ ] Anotado horário de início: ________________________

3. DURANTE INSTALAÇÃO (1-2 horas)
   - [ ] Aguardar conclusão do upgrade
   - [ ] Reinicializações automáticas esperadas
   - [ ] NÃO INTERROMPER O PROCESSO

4. PÓS-UPGRADE IMEDIATO
   - [ ] Windows Server 2025 iniciou com sucesso
   - [ ] Desktop carrega normalmente
   - [ ] RDP ainda funciona
   - [ ] Anotado horário de conclusão: ________________________
```

### Método B: Instalação Limpa + Restore

```markdown
## Checklist Instalação Limpa

1. BACKUP VALIDADO
   - [ ] Snapshot Contabo ATIVO
   - [ ] Backup ZIP íntegro e acessível
   - [ ] RESTORE_GUIDE.md estudado

2. INSTALAÇÃO LIMPA
   - [ ] Windows Server 2025 instalado
   - [ ] Rede configurada
   - [ ] RDP funcionando
   - [ ] Windows Updates aplicados

3. RESTORE MANUAL
   - [ ] Seguir RESTORE_GUIDE.md - FASE 1 a 8
   - [ ] Software base instalado
   - [ ] Certificado importado
   - [ ] Código restaurado
   - [ ] Testes de validação PASSARAM
```

---

## ✅ Pós-Upgrade: Validação Completa

### Checklist de Validação

```markdown
## 1. SISTEMA OPERACIONAL
- [ ] systeminfo mostra: Windows Server 2025
- [ ] Windows ativado e licenciado
- [ ] Atualizações instaladas
- [ ] Firewall ativo e configurado
- [ ] RDP funcionando (testar reconexão)
- [ ] SSH funcionando (se aplicável)

## 2. SOFTWARE INSTALADO
- [ ] Python 3.12.3 funcionando
  ```
  python --version
  # Esperado: Python 3.12.3
  ```
- [ ] Git funcionando
  ```
  git --version
  ```
- [ ] Chrome instalado e abrindo
  ```
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
  ```
- [ ] ChromeDriver compatível
  ```
  chromedriver --version
  ```
- [ ] Web Signer instalado e rodando
  - Ícone na bandeja do sistema
  - Serviço iniciado

## 3. CERTIFICADO DIGITAL
- [ ] Arquivo .pfx em C:\certs\certificado.pfx
- [ ] Certificado no Certificate Store
  ```powershell
  Get-ChildItem Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*517.648.902-30*"}
  ```
- [ ] HasPrivateKey: True
- [ ] Web Signer detecta certificado

## 4. CHROME + WEB SIGNER
- [ ] Chrome abre normalmente
- [ ] Perfil revisa.precatorio@gmail.com sincronizado
- [ ] Extensões sincronizadas (verificar chrome://extensions/)
- [ ] Web Signer aparece nas extensões
- [ ] Extensão habilitada e ativa
- [ ] Comunicação extensão ↔ Web Signer OK

## 5. PROJETO CRAWLER
- [ ] Código em C:\projetos\crawler_tjsp
- [ ] Arquivo .env presente e completo
- [ ] Virtual environment existe
  ```powershell
  Test-Path "C:\projetos\crawler_tjsp\.venv"
  ```
- [ ] Dependências instaladas
  ```powershell
  cd C:\projetos\crawler_tjsp
  .\.venv\Scripts\Activate.ps1
  pip list
  ```
- [ ] Git funcionando
  ```powershell
  git status
  git log -1
  ```

## 6. BANCO DE DADOS (se aplicável)
- [ ] PostgreSQL rodando
  ```powershell
  Get-Service postgresql-x64-15
  ```
- [ ] Database revisa_db existe
- [ ] Conexão funciona
  ```powershell
  psql -U revisa_user -d revisa_db -h localhost
  ```
- [ ] Tabelas presentes

## 7. TESTE DE AUTENTICAÇÃO (CRÍTICO!)
- [ ] Script test_authentication.py executado
  ```powershell
  cd C:\projetos\crawler_tjsp
  .\.venv\Scripts\Activate.ps1
  python windows-server\scripts\test_authentication.py
  ```
- [ ] Chrome abre via Selenium: ✅
- [ ] e-SAJ carrega: ✅
- [ ] Botão "Certificado Digital" clicado: ✅
- [ ] Web Signer abre modal: ✅
- [ ] Certificado pode ser selecionado: ✅
- [ ] LOGIN BEM-SUCEDIDO: ✅✅✅
- [ ] Screenshot salvo: login_success.png

## 8. TESTE DO CRAWLER
- [ ] Crawler executa sem erros
  ```powershell
  python crawler_full.py --help
  ```
- [ ] Teste com processo fictício funciona
  ```powershell
  python crawler_full.py --debug --processo=1234567-89.2020.8.26.0100
  ```
- [ ] Logs sendo gerados
- [ ] Sem erros críticos

## 9. CONFIGURAÇÕES DO SISTEMA
- [ ] Variáveis de ambiente preservadas
- [ ] PATH contém Python, Git, ChromeDriver
- [ ] Serviços/tarefas agendadas preservados (se configurados)
- [ ] Firewall rules preservadas

## 10. PERFORMANCE
- [ ] Sistema responsivo
- [ ] Uso de RAM normal
- [ ] Uso de CPU normal
- [ ] Disco com espaço suficiente
```

---

## 🎯 Critérios de Sucesso

### ✅ Upgrade BEM-SUCEDIDO se:

1. ✅ Sistema operacional: Windows Server 2025 ativo e licenciado
2. ✅ Todo software funcionando (Python, Git, Chrome, Web Signer)
3. ✅ Certificado digital funcionando
4. ✅ Chrome + Web Signer comunicando
5. ✅ **test_authentication.py PASSOU** (login com certificado OK)
6. ✅ Crawler executa sem erros
7. ✅ Sistema estável por pelo menos 24 horas

### ❌ ROLLBACK NECESSÁRIO se:

1. ❌ test_authentication.py FALHA (login não funciona)
2. ❌ Web Signer não detecta certificado
3. ❌ Chrome não abre ou extensões não funcionam
4. ❌ Sistema instável (crashes, erros críticos)
5. ❌ Qualquer funcionalidade crítica quebrada

**Se rollback necessário:** Seguir RESTORE_GUIDE.md → Método 1 (Snapshot Contabo)

---

## 📊 Pós-Upgrade: Próximos Passos

### Após Validação Bem-Sucedida:

```markdown
## 1. CRIAR NOVO SNAPSHOT
- [ ] Painel Contabo → Criar snapshot
- [ ] Nome: post-upgrade-ws2025-success-2025-10-06
- [ ] Descrição: Windows Server 2025 instalado e validado
- [ ] Status: Completed

## 2. PERÍODO DE OBSERVAÇÃO
- [ ] Monitorar sistema por 7 dias
- [ ] Executar testes diários
- [ ] Validar processamento de jobs reais
- [ ] Registrar qualquer anomalia

## 3. LIMPEZA (após 7 dias)
- [ ] Se tudo estável, pode deletar snapshot antigo
- [ ] Manter backup ZIP por mais 30 dias
- [ ] Documentar lições aprendidas

## 4. DOCUMENTAÇÃO
- [ ] Atualizar README.md
- [ ] Atualizar CREDENTIALS.md (se senhas mudaram)
- [ ] Atualizar MIGRATION_CHECKLIST.md
- [ ] Criar log de upgrade (data, horário, problemas, soluções)

## 5. NOTIFICAÇÕES
- [ ] Comunicar sucesso do upgrade para stakeholders
- [ ] Atualizar documentação técnica
- [ ] Compartilhar lições aprendidas com equipe
```

---

## 🚨 Plano de Contingência

### Se Algo Der Errado:

#### NÍVEL 1: Problema Pequeno (Ex: Extensão não funciona)
```
1. Consultar TROUBLESHOOTING_AUTENTICACAO.md
2. Tentar soluções rápidas (reinstalar extensão, etc)
3. Se resolver em < 30 min: Continuar
4. Se não resolver: Escalar para Nível 2
```

#### NÍVEL 2: Problema Médio (Ex: Certificado não importa)
```
1. Consultar RESTORE_GUIDE.md - Seção de Troubleshooting
2. Tentar soluções alternativas
3. Se resolver em < 1 hora: Continuar
4. Se não resolver: Escalar para Nível 3
```

#### NÍVEL 3: Problema Grave (Ex: Sistema instável, login não funciona)
```
1. PARAR tentativas de correção
2. DECISÃO: Rollback via snapshot Contabo
3. Executar restore (10-20 min)
4. Validar sistema voltou ao normal
5. Analisar causa do problema
6. Tentar upgrade novamente em outra data
```

### Contatos de Emergência:

```
Contabo Support: https://contabo.com/support
Softplan Web Signer: https://websigner.softplan.com.br
Equipe Interna: [adicionar contatos]
```

---

## 📝 Registro de Execução

### Preencher Durante o Processo:

```
═══════════════════════════════════════════════════════════
  REGISTRO DE UPGRADE - WINDOWS SERVER 2016 → 2025
═══════════════════════════════════════════════════════════

Data: _____________
Horário Início: _____________
Responsável: _____________

PRÉ-UPGRADE
-----------
[ ] Snapshot Contabo criado às: _____________
[ ] Snapshot ID: _____________
[ ] Backup ZIP criado às: _____________
[ ] Hash MD5: _____________
[ ] Backup transferido e validado: ✅

UPGRADE
-------
[ ] Método escolhido: ☐ In-Place  ☐ Limpa + Restore
[ ] Início do upgrade: _____________
[ ] Fim do upgrade: _____________
[ ] Duração total: _____________

PROBLEMAS ENCONTRADOS
---------------------
1. _______________________________________________________
   Solução: ________________________________________________
2. _______________________________________________________
   Solução: ________________________________________________

VALIDAÇÃO PÓS-UPGRADE
----------------------
[ ] Windows Server 2025 ativo: ✅
[ ] Software funcionando: ✅
[ ] Certificado OK: ✅
[ ] test_authentication.py: ✅
[ ] Crawler funcional: ✅

RESULTADO FINAL
---------------
☐ SUCESSO - Sistema 100% operacional
☐ SUCESSO PARCIAL - Com observações
☐ FALHA - Rollback executado

Observações:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

Horário Conclusão: _____________
Duração Total: _____________

Assinatura: ___________________
═══════════════════════════════════════════════════════════
```

---

## ✅ Assinatura de Aprovação

**Eu confirmo que:**

```
[ ] Li e entendi todos os documentos:
    - BACKUP_GUIDE.md
    - RESTORE_GUIDE.md
    - QUICK_BACKUP.md
    - Este UPGRADE_CHECKLIST.md

[ ] Criei snapshot Contabo ANTES de iniciar

[ ] Tenho backup em múltiplos locais

[ ] Entendo como fazer rollback se necessário

[ ] Tenho tempo alocado para o processo (2-4 horas)

[ ] Estou preparado para possíveis problemas

[ ] Testei que o backup é íntegro (hash MD5 validado)
```

**Nome:** _____________________  
**Data:** _____________________  
**Assinatura:** _____________________  

---

**🚀 VOCÊ ESTÁ PRONTO PARA O UPGRADE!**

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Status:** Pronto para uso

