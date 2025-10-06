# ⚡ Backup Rápido - Guia Executivo de 5 Passos

**Tempo Total: 30-45 minutos**  
**Data:** 2025-10-06  

---

## 🎯 Para Quem Tem Pressa

Se você quer fazer backup rápido antes do upgrade, siga EXATAMENTE estes 5 passos:

---

## 📝 PASSO 1: Snapshot Contabo (5 min) 🔴 CRÍTICO

### No navegador do seu computador:

```
1. Acesse: https://my.contabo.com
2. Login → Cloud VPS → Selecione servidor 62.171.143.88
3. Menu "Snapshots" → "Create Snapshot"
4. Nome: pre-upgrade-to-ws2025-2025-10-06
5. Descrição: Backup antes upgrade WS2025 - Fase 5 completa
6. Clicar "Create"
7. ⏳ Aguardar status: "Completed" (pode levar 10-15 min)
```

✅ **Snapshot é seu seguro total. NÃO PULE!**

---

## 💻 PASSO 2: Executar Script de Backup (10 min)

### No servidor via RDP:

```powershell
# 1. Conectar via RDP
# IP: 62.171.143.88
# User: Administrator
# Pass: 31032025

# 2. Abrir PowerShell como Administrator

# 3. Navegar para projeto
cd C:\projetos\crawler_tjsp

# 4. Executar backup automático
.\scripts\backup_complete_system.ps1

# 5. Aguardar conclusão (8-10 minutos)
# Deve aparecer: "✅ BACKUP CONCLUÍDO COM SUCESSO!"
```

### O que acontece:
- ✅ Cria estrutura de backup
- ✅ Copia código completo
- ✅ Exporta certificado
- ✅ Documenta sistema
- ✅ Gera arquivo ZIP
- ✅ Calcula hash MD5

---

## 📤 PASSO 3: Transferir Backup para Seu Computador (10-15 min)

### Opção A: Via SCP (Mac/Linux - RECOMENDADO)

```bash
# No terminal do seu Mac
scp Administrator@62.171.143.88:"C:/backups/BACKUP_COMPLETO_PRE_UPGRADE_*.zip" ~/Downloads/

# Também transferir hash
scp Administrator@62.171.143.88:"C:/backups/BACKUP_COMPLETO_PRE_UPGRADE_*.md5" ~/Downloads/
```

### Opção B: Via RDP (Arrastar e Soltar)

```
1. Manter conexão RDP aberta
2. No servidor: navegar até C:\backups\
3. Localizar arquivo BACKUP_COMPLETO_PRE_UPGRADE_*.zip
4. Arrastar arquivo para seu computador local
5. Aguardar transferência (2-5 GB, pode levar 10-15 min)
```

---

## ✅ PASSO 4: Validar Hash MD5 (2 min)

### No servidor (PowerShell):

```powershell
# Ver hash gerado
Get-Content "C:\backups\BACKUP_COMPLETO_PRE_UPGRADE_*.md5"
```

### No seu Mac:

```bash
# Calcular hash do arquivo transferido
md5 ~/Downloads/BACKUP_COMPLETO_PRE_UPGRADE_*.zip

# Comparar com hash do servidor
# DEVEM SER IDÊNTICOS!
```

✅ **Se hashes forem iguais: Transferência OK**  
❌ **Se diferentes: Transferir novamente!**

---

## 📋 PASSO 5: Checklist Final (5 min)

### Antes de fazer upgrade, CONFIRME:

```markdown
## ✅ Checklist Pré-Upgrade

### Snapshot Contabo
- [ ] Snapshot criado
- [ ] Nome: pre-upgrade-to-ws2025-2025-10-06
- [ ] Status: "Completed"
- [ ] Snapshot ID anotado: _______________

### Backup ZIP
- [ ] Script backup_complete_system.ps1 executado
- [ ] Arquivo ZIP criado em C:\backups\
- [ ] Tamanho: ~2-5 GB
- [ ] Arquivo .md5 gerado

### Transferência
- [ ] ZIP transferido para computador local
- [ ] Arquivo em: ~/Downloads/
- [ ] Hash MD5 validado (local == servidor) ✅

### Segurança
- [ ] Cópia adicional do ZIP em HD externo
- [ ] Ou upload para Google Drive / Dropbox
- [ ] Backup em MÚLTIPLOS locais

### Validação
- [ ] Snapshot Contabo ATIVO
- [ ] Backup ZIP íntegro (hash OK)
- [ ] Certificado exportado (dentro do ZIP)
- [ ] Documentação completa (BACKUP_MANIFEST.txt)
```

### 🚨 SE TODOS OS CHECKBOXES ESTIVEREM MARCADOS:

✅ **VOCÊ ESTÁ PRONTO PARA O UPGRADE!**

---

## 🚀 Próximo Passo: Upgrade

### Como fazer upgrade:

#### Opção A: Upgrade In-Place (Preserva Dados)
```
1. Adquirir licença Windows Server 2025
2. Executar upgrade via Windows Update ou mídia de instalação
3. Escolher "Keep files and apps"
4. Aguardar processo (1-2 horas)
5. Validar que tudo funciona
```

#### Opção B: Instalação Limpa + Restore
```
1. Fazer instalação limpa do Windows Server 2025
2. Seguir guia: RESTORE_GUIDE.md
3. Restaurar backup manualmente
4. Validar funcionamento
```

### Após Upgrade:

```powershell
# Testar autenticação
cd C:\projetos\crawler_tjsp
.\.venv\Scripts\Activate.ps1
python windows-server\scripts\test_authentication.py
```

✅ **Se teste passar: Upgrade bem-sucedido!**  
❌ **Se falhar: Restore via snapshot Contabo**

---

## 🔄 Como Voltar Atrás (Se Necessário)

### Via Snapshot (RÁPIDO - 10-20 min):

```
1. Painel Contabo → Snapshots
2. Selecionar: pre-upgrade-to-ws2025-2025-10-06
3. Clicar "Restore"
4. Aguardar conclusão
5. ✅ Sistema volta exatamente como estava
```

### Via Backup Manual (DEMORADO - 2-4 horas):

```
Consultar: RESTORE_GUIDE.md
```

---

## 📊 Resumo Visual do Processo

```
┌─────────────────────────────────────────────────┐
│  ANTES DO UPGRADE - BACKUP COMPLETO             │
└─────────────────────────────────────────────────┘

1️⃣  SNAPSHOT CONTABO
    └─> https://my.contabo.com
        └─> Create Snapshot
            └─> ✅ Seguro total

2️⃣  SCRIPT AUTOMÁTICO
    └─> PowerShell: backup_complete_system.ps1
        └─> Cria ZIP completo
            └─> ✅ Backup secundário

3️⃣  TRANSFERIR
    └─> SCP ou RDP
        └─> ZIP para computador local
            └─> ✅ Redundância

4️⃣  VALIDAR
    └─> MD5 hash
        └─> Local == Servidor
            └─> ✅ Integridade confirmada

5️⃣  CHECKLIST
    └─> Todos ✅ marcados
        └─> Backup em múltiplos locais
            └─> ✅ PRONTO PARA UPGRADE

┌─────────────────────────────────────────────────┐
│  FAZER UPGRADE                                  │
└─────────────────────────────────────────────────┘

    Windows Server 2016 ──upgrade──> 2025

┌─────────────────────────────────────────────────┐
│  VALIDAR                                        │
└─────────────────────────────────────────────────┘

    ✅ Tudo funciona? → SUCESSO!
    ❌ Problema? → RESTORE VIA SNAPSHOT
```

---

## ⚠️ AVISOS CRÍTICOS

### 🔴 NUNCA:
- ❌ Fazer upgrade sem snapshot Contabo
- ❌ Deletar snapshot antigo imediatamente após upgrade
- ❌ Confiar apenas em um único backup
- ❌ Pular validação de hash MD5

### 🟢 SEMPRE:
- ✅ Criar snapshot ANTES de qualquer mudança
- ✅ Manter backup em MÚLTIPLOS locais
- ✅ Validar hash após transferência
- ✅ Testar funcionalidade após upgrade
- ✅ Manter snapshot por pelo menos 7 dias após upgrade

---

## 📞 Ajuda Rápida

**Problema:** Script backup_complete_system.ps1 não existe
```powershell
# Verificar localização
Get-ChildItem "C:\projetos\crawler_tjsp\scripts\" -Filter "*.ps1"

# Se não existir, usar método manual:
# Consultar: BACKUP_GUIDE.md
```

**Problema:** Snapshot Contabo não completa
```
- Aguardar até 30 minutos
- Verificar painel Contabo para mensagens de erro
- Contatar suporte Contabo se necessário
```

**Problema:** Transferência SCP falha
```bash
# Verificar SSH funciona
ssh Administrator@62.171.143.88

# Se não funcionar, usar RDP (arrastar/soltar)
```

---

## 📚 Documentação Completa

Para instruções detalhadas, consulte:

- **BACKUP_GUIDE.md** - Guia completo de backup (todas as etapas explicadas)
- **RESTORE_GUIDE.md** - Como restaurar sistema
- **DEPLOYMENT_PLAN.md** - Plano de deployment original

---

## ✅ Conclusão

Seguindo estes 5 passos, você terá:

1. ✅ **Snapshot Contabo** - Restore completo em 10-20 min
2. ✅ **Backup ZIP** - Redundância e portabilidade
3. ✅ **Backup local** - Cópia segura no seu computador
4. ✅ **Hash validado** - Integridade confirmada
5. ✅ **Checklist OK** - Pronto para upgrade

**Tempo total: 30-45 minutos**  
**Segurança: MÁXIMA** 🔒  
**Risco: MÍNIMO** ✅  

---

**Última atualização:** 2025-10-06  
**Versão:** 1.0  
**Responsável:** Persival Balleste  

🚀 **BOA SORTE COM O UPGRADE!**

