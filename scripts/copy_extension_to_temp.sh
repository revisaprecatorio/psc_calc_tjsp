#!/bin/bash
# Copia extensão Web Signer do perfil do crawler para perfil temporário

echo "Copiando extensão Web Signer para perfil temporário..."

# Diretórios
SOURCE_PROFILE="/home/crawler/.config/google-chrome"
TEMP_PROFILE="/tmp/chrome_profile_test"
EXTENSION_ID="bbafmabaelnnkondpfpjmdklbmfnbmol"

# Criar diretório de extensões no perfil temporário
mkdir -p "$TEMP_PROFILE/Default/Extensions"

# Copiar extensão
if [ -d "$SOURCE_PROFILE/Default/Extensions/$EXTENSION_ID" ]; then
    echo "✅ Extensão encontrada no perfil do crawler"
    cp -r "$SOURCE_PROFILE/Default/Extensions/$EXTENSION_ID" "$TEMP_PROFILE/Default/Extensions/"
    echo "✅ Extensão copiada para perfil temporário"
    
    # Copiar também as configurações da extensão
    mkdir -p "$TEMP_PROFILE/Default/Local Extension Settings"
    mkdir -p "$TEMP_PROFILE/Default/Sync Extension Settings"
    
    if [ -d "$SOURCE_PROFILE/Default/Local Extension Settings/$EXTENSION_ID" ]; then
        cp -r "$SOURCE_PROFILE/Default/Local Extension Settings/$EXTENSION_ID" "$TEMP_PROFILE/Default/Local Extension Settings/"
        echo "✅ Configurações locais copiadas"
    fi
    
    if [ -d "$SOURCE_PROFILE/Default/Sync Extension Settings/$EXTENSION_ID" ]; then
        cp -r "$SOURCE_PROFILE/Default/Sync Extension Settings/$EXTENSION_ID" "$TEMP_PROFILE/Default/Sync Extension Settings/"
        echo "✅ Configurações de sync copiadas"
    fi
    
    echo ""
    echo "✅ EXTENSÃO COPIADA COM SUCESSO!"
    echo "   Agora execute: python3 test_with_chromedriver.py"
else
    echo "❌ Extensão não encontrada no perfil do crawler"
    exit 1
fi
