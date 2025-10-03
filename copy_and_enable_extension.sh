#!/bin/bash
# Copia extensão Web Signer E ativa ela no perfil temporário

echo "================================================================================"
echo "COPIANDO E ATIVANDO EXTENSÃO WEB SIGNER"
echo "================================================================================"

# Diretórios
SOURCE_PROFILE="/home/crawler/.config/google.chrome"
TEMP_PROFILE="/tmp/chrome_profile_test"
EXTENSION_ID="bbafmabaelnnkondpfpjmdklbmfnbmol"

# 1. Criar estrutura do perfil temporário
echo ""
echo "[1] Criando estrutura do perfil temporário..."
mkdir -p "$TEMP_PROFILE/Default/Extensions"
mkdir -p "$TEMP_PROFILE/Default/Local Extension Settings"
mkdir -p "$TEMP_PROFILE/Default/Sync Extension Settings"

# 2. Copiar extensão
echo ""
echo "[2] Copiando extensão Web Signer..."
if [ -d "$SOURCE_PROFILE/Default/Extensions/$EXTENSION_ID" ]; then
    cp -r "$SOURCE_PROFILE/Default/Extensions/$EXTENSION_ID" "$TEMP_PROFILE/Default/Extensions/"
    echo "✅ Extensão copiada"
    
    # Copiar configurações
    if [ -d "$SOURCE_PROFILE/Default/Local Extension Settings/$EXTENSION_ID" ]; then
        cp -r "$SOURCE_PROFILE/Default/Local Extension Settings/$EXTENSION_ID" "$TEMP_PROFILE/Default/Local Extension Settings/"
        echo "✅ Configurações locais copiadas"
    fi
    
    if [ -d "$SOURCE_PROFILE/Default/Sync Extension Settings/$EXTENSION_ID" ]; then
        cp -r "$SOURCE_PROFILE/Default/Sync Extension Settings/$EXTENSION_ID" "$TEMP_PROFILE/Default/Sync Extension Settings/"
        echo "✅ Configurações de sync copiadas"
    fi
else
    echo "❌ Extensão não encontrada no perfil do crawler"
    exit 1
fi

# 3. Copiar Preferences do perfil original (se existir)
echo ""
echo "[3] Copiando Preferences do perfil original..."
if [ -f "$SOURCE_PROFILE/Default/Preferences" ]; then
    cp "$SOURCE_PROFILE/Default/Preferences" "$TEMP_PROFILE/Default/Preferences"
    echo "✅ Preferences copiado"
else
    echo "⚠️ Preferences não encontrado no perfil original"
fi

# 4. Copiar Local State (configurações globais)
echo ""
echo "[4] Copiando Local State..."
if [ -f "$SOURCE_PROFILE/Local State" ]; then
    cp "$SOURCE_PROFILE/Local State" "$TEMP_PROFILE/Local State"
    echo "✅ Local State copiado"
else
    echo "⚠️ Local State não encontrado"
fi

# 5. Ajustar permissões
echo ""
echo "[5] Ajustando permissões..."
chmod -R 755 "$TEMP_PROFILE"
echo "✅ Permissões ajustadas"

# 6. Verificar estrutura
echo ""
echo "[6] Verificando estrutura criada..."
echo ""
echo "Extensão:"
ls -la "$TEMP_PROFILE/Default/Extensions/$EXTENSION_ID/" 2>/dev/null | head -5

echo ""
echo "Preferences:"
ls -lh "$TEMP_PROFILE/Default/Preferences" 2>/dev/null || echo "  Não existe"

echo ""
echo "Local State:"
ls -lh "$TEMP_PROFILE/Local State" 2>/dev/null || echo "  Não existe"

echo ""
echo "================================================================================"
echo "CÓPIA E ATIVAÇÃO CONCLUÍDAS!"
echo "================================================================================"
echo ""
echo "Próximos passos:"
echo "  1. Execute: python3 test_with_chromedriver.py"
echo "  2. A extensão deve estar ativa no perfil temporário"
echo "  3. Verifique os screenshots"
echo ""
