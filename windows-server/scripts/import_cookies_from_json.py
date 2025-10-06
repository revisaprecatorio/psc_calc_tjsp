"""
Importar Cookies do JSON exportado pela extensão Cookie Editor
===============================================================

Este script converte cookies exportados pela extensão Cookie Editor
para o formato que o Selenium precisa.

Uso:
    1. Copie o JSON dos cookies exportados
    2. Cole no arquivo cookies_export.json
    3. Execute: python import_cookies_from_json.py
"""

import json
import pickle
import os
from datetime import datetime

# ====================
# CONFIGURAÇÕES
# ====================

# Arquivo JSON com cookies exportados (você vai colar aqui)
COOKIES_JSON_FILE = r"C:\projetos\crawler_tjsp\cookies_export.json"

# Onde salvar cookies convertidos
SAVED_COOKIES_DIR = r"C:\projetos\crawler_tjsp\saved_cookies"
SAVED_COOKIES_FILE = os.path.join(SAVED_COOKIES_DIR, "esaj_cookies.pkl")

# ====================
# FUNÇÕES
# ====================

def convert_cookies():
    """Converte cookies do formato Cookie Editor para formato Selenium."""

    print("=" * 70)
    print("IMPORTAÇÃO DE COOKIES - Cookie Editor → Selenium")
    print("=" * 70)
    print("")

    # Verificar se arquivo JSON existe
    if not os.path.exists(COOKIES_JSON_FILE):
        print(f"ERRO: Arquivo não encontrado: {COOKIES_JSON_FILE}")
        print("")
        print("SOLUÇÃO:")
        print("  1. Exporte cookies usando Cookie Editor")
        print("  2. Salve o JSON em: C:\\projetos\\crawler_tjsp\\cookies_export.json")
        print("  3. Execute este script novamente")
        print("")
        return False

    print(f"Lendo arquivo JSON: {COOKIES_JSON_FILE}")

    # Ler JSON
    with open(COOKIES_JSON_FILE, 'r', encoding='utf-8') as f:
        cookies_json = json.load(f)

    print(f"  Total de cookies encontrados: {len(cookies_json)}")
    print("")

    # Converter para formato Selenium
    selenium_cookies = []

    for cookie in cookies_json:
        selenium_cookie = {
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie['domain'],
            'path': cookie.get('path', '/'),
            'secure': cookie.get('secure', False),
            'httpOnly': cookie.get('httpOnly', False)
        }

        # Adicionar expiry se existir
        if 'expirationDate' in cookie and cookie['expirationDate']:
            selenium_cookie['expiry'] = int(cookie['expirationDate'])
        else:
            # Cookie de sessão - adicionar expiry de 1 dia
            selenium_cookie['expiry'] = int(datetime.now().timestamp() + 86400)

        selenium_cookies.append(selenium_cookie)

    # Criar diretório se não existir
    os.makedirs(SAVED_COOKIES_DIR, exist_ok=True)

    # Salvar cookies em pickle
    print("Salvando cookies em formato Selenium...")
    with open(SAVED_COOKIES_FILE, 'wb') as f:
        pickle.dump(selenium_cookies, f)

    print(f"  Cookies salvos em: {SAVED_COOKIES_FILE}")
    print("")

    # Mostrar amostra
    print("Amostra de cookies convertidos:")
    for i, cookie in enumerate(selenium_cookies[:5]):
        print(f"  {i+1}. {cookie['name'][:30]:30} | Domain: {cookie['domain']}")

    if len(selenium_cookies) > 5:
        print(f"  ... e mais {len(selenium_cookies) - 5} cookies")

    print("")
    print("=" * 70)
    print("CONVERSÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print("")
    print(f"Total de cookies salvos: {len(selenium_cookies)}")
    print(f"Arquivo: {SAVED_COOKIES_FILE}")
    print("")
    print("PRÓXIMO PASSO:")
    print("  Execute: python windows-server/scripts/test_with_cookies.py")
    print("")

    return True

# ====================
# MAIN
# ====================

if __name__ == "__main__":
    print("")
    success = convert_cookies()

    if success:
        print("Importação bem-sucedida!")
        exit(0)
    else:
        print("Importação falhou. Verifique erros acima.")
        exit(1)
