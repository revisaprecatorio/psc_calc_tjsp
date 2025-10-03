#!/bin/bash
# Script para copiar a extensão Web Signer do perfil do crawler para o root

echo "================================================================================"
echo "COPIANDO EXTENSÃO WEB SIGNER DO PERFIL DO CRAWLER PARA O ROOT"
echo "================================================================================"

# ID da extensão Web Signer
EXTENSION_ID="bbafmabaelnnkondpfpjmdklbmfnbmol"

# Diretórios
CRAWLER_CHROME_DIR="/home/crawler/.config/google-chrome/Default/Extensions"
ROOT_CHROME_DIR="/root/.config/google-chrome/Default/Extensions"

echo ""
echo "[1] Verificando se a extensão existe no perfil do crawler..."
if [ -d "$CRAWLER_CHROME_DIR/$EXTENSION_ID" ]; then
    echo "✅ Extensão encontrada em: $CRAWLER_CHROME_DIR/$EXTENSION_ID"
    
    # Listar versões
    echo ""
    echo "[2] Versões disponíveis:"
    ls -la "$CRAWLER_CHROME_DIR/$EXTENSION_ID/"
    
    # Criar diretório de destino
    echo ""
    echo "[3] Criando diretório de destino..."
    mkdir -p "$ROOT_CHROME_DIR"
    
    # Copiar extensão
    echo ""
    echo "[4] Copiando extensão..."
    cp -r "$CRAWLER_CHROME_DIR/$EXTENSION_ID" "$ROOT_CHROME_DIR/"
    
    # Verificar cópia
    if [ -d "$ROOT_CHROME_DIR/$EXTENSION_ID" ]; then
        echo "✅ Extensão copiada com sucesso!"
        echo ""
        echo "[5] Conteúdo copiado:"
        ls -la "$ROOT_CHROME_DIR/$EXTENSION_ID/"
    else
        echo "❌ Erro ao copiar extensão"
        exit 1
    fi
else
    echo "❌ Extensão NÃO encontrada no perfil do crawler"
    echo "   Caminho esperado: $CRAWLER_CHROME_DIR/$EXTENSION_ID"
    exit 1
fi

# Copiar também as preferências do Chrome (se existirem)
echo ""
echo "[6] Copiando preferências do Chrome..."
CRAWLER_PREFS="/home/crawler/.config/google-chrome/Default/Preferences"
ROOT_PREFS="/root/.config/google-chrome/Default/Preferences"

if [ -f "$CRAWLER_PREFS" ]; then
    # Fazer backup se já existir
    if [ -f "$ROOT_PREFS" ]; then
        cp "$ROOT_PREFS" "$ROOT_PREFS.backup-$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backup das preferências antigas criado"
    fi
    
    # Copiar preferências
    cp "$CRAWLER_PREFS" "$ROOT_PREFS"
    echo "✅ Preferências copiadas"
else
    echo "⚠️ Arquivo de preferências não encontrado"
fi

# Copiar também o Local State (configurações globais)
echo ""
echo "[7] Copiando Local State..."
CRAWLER_LOCAL_STATE="/home/crawler/.config/google-chrome/Local State"
ROOT_LOCAL_STATE="/root/.config/google-chrome/Local State"

if [ -f "$CRAWLER_LOCAL_STATE" ]; then
    # Fazer backup se já existir
    if [ -f "$ROOT_LOCAL_STATE" ]; then
        cp "$ROOT_LOCAL_STATE" "$ROOT_LOCAL_STATE.backup-$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backup do Local State antigo criado"
    fi
    
    # Copiar Local State
    cp "$CRAWLER_LOCAL_STATE" "$ROOT_LOCAL_STATE"
    echo "✅ Local State copiado"
else
    echo "⚠️ Local State não encontrado"
fi

echo ""
echo "================================================================================"
echo "CÓPIA CONCLUÍDA!"
echo "================================================================================"
echo ""
echo "Próximos passos:"
echo "1. Execute: python3 verify_extension.py"
echo "2. Verifique se a extensão aparece em chrome://extensions/"
echo "3. Teste o login com certificado"
echo ""
