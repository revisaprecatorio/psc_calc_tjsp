# 🔐 Script de Export do Certificado Digital
# Versão: 1.0
# Data: 2025-10-06
# Descrição: Exporta certificado digital do Windows Certificate Store

#Requires -RunAsAdministrator

Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔐 EXPORT DE CERTIFICADO DIGITAL" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Configurações
$backupDir = "C:\backups\certificados_" + (Get-Date -Format "yyyy-MM-dd_HHmmss")
$certPassword = "903205"
$cpf = "517.648.902-30"

# Criar diretório de backup
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "📁 Diretório de backup: $backupDir`n" -ForegroundColor Gray

# Buscar certificado
Write-Host "🔍 Buscando certificado com CPF $cpf..." -ForegroundColor Cyan

$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like "*$cpf*"}

if (-not $cert) {
    Write-Host "❌ ERRO: Certificado não encontrado!" -ForegroundColor Red
    Write-Host "`nVerifique se o certificado está instalado em:" -ForegroundColor Yellow
    Write-Host "  Cert:\CurrentUser\My (não LocalMachine\My)`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Certificado encontrado!" -ForegroundColor Green
Write-Host "`n📋 Informações do Certificado:" -ForegroundColor Cyan
Write-Host "   Subject: $($cert.Subject)" -ForegroundColor Gray
Write-Host "   Issuer: $($cert.Issuer)" -ForegroundColor Gray
Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
Write-Host "   Valid From: $($cert.NotBefore)" -ForegroundColor Gray
Write-Host "   Valid Until: $($cert.NotAfter)" -ForegroundColor Gray
Write-Host "   Has Private Key: $($cert.HasPrivateKey)" -ForegroundColor Gray

# Verificar chave privada
if (-not $cert.HasPrivateKey) {
    Write-Host "`n⚠️  AVISO: Certificado NÃO contém chave privada!" -ForegroundColor Yellow
    Write-Host "   Export .pfx pode não funcionar corretamente." -ForegroundColor Yellow
}

# Exportar chave pública (.cer)
Write-Host "`n🔑 Exportando chave pública (.cer)..." -ForegroundColor Cyan
$cerPath = Join-Path $backupDir "certificado_public.cer"
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Write-Host "✅ Chave pública exportada: $cerPath" -ForegroundColor Green

# Exportar com chave privada (.pfx)
Write-Host "`n🔐 Exportando com chave privada (.pfx)..." -ForegroundColor Cyan
$pfxPath = Join-Path $backupDir "certificado_backup.pfx"
$password = ConvertTo-SecureString -String $certPassword -Force -AsPlainText

try {
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $password | Out-Null
    Write-Host "✅ Chave privada exportada: $pfxPath" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO ao exportar chave privada: $_" -ForegroundColor Red
    Write-Host "   Certificado pode não ter permissão de exportação." -ForegroundColor Yellow
}

# Copiar certificado original (se existir)
$originalCertPath = "C:\certs\certificado.pfx"
if (Test-Path $originalCertPath) {
    Write-Host "`n📄 Copiando certificado original..." -ForegroundColor Cyan
    $originalCopyPath = Join-Path $backupDir "certificado_original.pfx"
    Copy-Item $originalCertPath $originalCopyPath -Force
    Write-Host "✅ Certificado original copiado: $originalCopyPath" -ForegroundColor Green
}

# Salvar informações do certificado
Write-Host "`n📝 Salvando informações do certificado..." -ForegroundColor Cyan
$certInfo = @{
    "Subject" = $cert.Subject
    "Issuer" = $cert.Issuer
    "Thumbprint" = $cert.Thumbprint
    "SerialNumber" = $cert.SerialNumber
    "NotBefore" = $cert.NotBefore
    "NotAfter" = $cert.NotAfter
    "HasPrivateKey" = $cert.HasPrivateKey
    "FriendlyName" = $cert.FriendlyName
    "Archived" = $cert.Archived
    "ExportDate" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}
$certInfo | ConvertTo-Json | Out-File (Join-Path $backupDir "certificate_info.json")

# Criar arquivo de texto com informações críticas
$infoText = @"
═══════════════════════════════════════════════════════════════
  CERTIFICADO DIGITAL - INFORMAÇÕES DE BACKUP
═══════════════════════════════════════════════════════════════

Data do Export: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
Servidor: $env:COMPUTERNAME
Usuário: $env:USERNAME

CERTIFICADO
-----------
Subject: $($cert.Subject)
Issuer: $($cert.Issuer)
Thumbprint: $($cert.Thumbprint)
Validade: $($cert.NotBefore) até $($cert.NotAfter)
Has Private Key: $($cert.HasPrivateKey)

CREDENCIAIS
-----------
Arquivo .pfx: certificado.pfx
Senha: $certPassword
CPF Titular: $cpf
Número do Pedido: 25424636
Código de Instalação: 669-281

ARQUIVOS EXPORTADOS
-------------------
1. certificado_public.cer - Chave pública (sem senha)
2. certificado_backup.pfx - Chave privada (senha: $certPassword)
3. certificado_original.pfx - Cópia do arquivo original (se disponível)
4. certificate_info.json - Metadados do certificado

COMO IMPORTAR (Restore)
-----------------------

Via PowerShell:
```
`$certPath = "certificado_backup.pfx"
`$password = ConvertTo-SecureString -String "$certPassword" -Force -AsPlainText
Import-PfxCertificate -FilePath `$certPath -CertStoreLocation Cert:\CurrentUser\My -Password `$password
```

Via Interface Gráfica:
1. Duplo-clique em certificado_backup.pfx
2. Seguir wizard de importação
3. Senha: $certPassword
4. Local: Current User → Personal

VALIDAÇÃO PÓS-IMPORTAÇÃO
-------------------------
```
Get-ChildItem Cert:\CurrentUser\My | Where-Object {`$_.Subject -like "*$cpf*"}
```

Deve mostrar certificado com HasPrivateKey = True

⚠️  IMPORTANTE:
- NUNCA compartilhe este arquivo
- Mantenha senha segura
- Faça backup em múltiplos locais
- Certificado válido até: $($cert.NotAfter)

═══════════════════════════════════════════════════════════════
"@

$infoText | Out-File (Join-Path $backupDir "LEIA-ME.txt") -Encoding UTF8

Write-Host "✅ Informações salvas" -ForegroundColor Green

# Validar exports
Write-Host "`n🔍 Validando exports..." -ForegroundColor Cyan

# Validar .cer
if (Test-Path $cerPath) {
    $cerSize = (Get-Item $cerPath).Length
    Write-Host "✅ certificado_public.cer ($cerSize bytes)" -ForegroundColor Green
} else {
    Write-Host "❌ certificado_public.cer não foi criado!" -ForegroundColor Red
}

# Validar .pfx
if (Test-Path $pfxPath) {
    $pfxSize = (Get-Item $pfxPath).Length
    Write-Host "✅ certificado_backup.pfx ($pfxSize bytes)" -ForegroundColor Green
    
    # Testar se .pfx pode ser importado (dry-run)
    try {
        $testCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($pfxPath, $certPassword)
        Write-Host "✅ Certificado .pfx validado (pode ser importado)" -ForegroundColor Green
        Write-Host "   Has Private Key: $($testCert.HasPrivateKey)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️  Aviso ao validar .pfx: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ certificado_backup.pfx não foi criado!" -ForegroundColor Red
}

# Criar ZIP
Write-Host "`n📦 Criando arquivo ZIP..." -ForegroundColor Cyan
$zipPath = "$backupDir.zip"
Compress-Archive -Path $backupDir -DestinationPath $zipPath -CompressionLevel Optimal
Write-Host "✅ ZIP criado: $zipPath" -ForegroundColor Green

# Calcular hash
$hash = Get-FileHash $zipPath -Algorithm MD5
$hash.Hash | Out-File "$zipPath.md5"
Write-Host "🔐 MD5: $($hash.Hash)" -ForegroundColor Gray

# Resumo final
Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ EXPORT CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n📁 Arquivos criados:" -ForegroundColor Cyan
Write-Host "   📦 $zipPath" -ForegroundColor Gray
Write-Host "   🔐 $zipPath.md5" -ForegroundColor Gray
Write-Host "`n📊 Tamanho do ZIP: $(((Get-Item $zipPath).Length / 1KB).ToString('0.00')) KB" -ForegroundColor Gray
Write-Host "`n📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Transferir ZIP para computador local" -ForegroundColor Yellow
Write-Host "   2. Validar hash MD5" -ForegroundColor Yellow
Write-Host "   3. Guardar em local seguro" -ForegroundColor Yellow
Write-Host "   4. Fazer cópia adicional (HD externo/cloud)" -ForegroundColor Yellow
Write-Host "`n⚠️  Senha do certificado: $certPassword (anote!)`n" -ForegroundColor Red

