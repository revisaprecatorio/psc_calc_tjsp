"""
Extração de Cookies do Perfil Default Chrome
==============================================

Este script extrai cookies de sessão autenticada do perfil Default
onde você fez login manualmente com Web Signer.

IMPORTANTE:
- Execute APÓS fazer login manual no Chrome (perfil Default)
- Chrome DEVE estar FECHADO durante extração
- Cookies são salvos em arquivo pickle

Uso:
    python extract_cookies.py
"""

import sqlite3
import pickle
import os
import shutil
from datetime import datetime

# ====================
# CONFIGURAÇÕES
# ====================

# Localização do arquivo de cookies do Chrome (perfil Profile 1 - revisa.precatorio@gmail.com)
CHROME_COOKIES_PATH = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Profile 1\Network\Cookies"

# Onde salvar cookies extraídos
SAVED_COOKIES_DIR = r"C:\projetos\crawler_tjsp\saved_cookies"
SAVED_COOKIES_FILE = os.path.join(SAVED_COOKIES_DIR, "esaj_cookies.pkl")

# Domínios de interesse (apenas e-SAJ)
TARGET_DOMAINS = [
    ".tjsp.jus.br",
    "esaj.tjsp.jus.br",
    ".esaj.tjsp.jus.br"
]

# ====================
# FUNÇÕES
# ====================

def check_chrome_closed():
    """Verifica se Chrome está fechado."""
    import psutil

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'chrome.exe' in proc.info['name'].lower():
            return False
    return True

def extract_cookies():
    """Extrai cookies do Chrome."""
    print("=" * 70)
    print("EXTRAÇÃO DE COOKIES - PERFIL PROFILE 1 CHROME")
    print("=" * 70)
    print("")

    # Verificar se Chrome está fechado
    print("Verificando se Chrome está fechado...")
    if not check_chrome_closed():
        print("  ERRO: Chrome está aberto!")
        print("")
        print("AÇÃO NECESSÁRIA:")
        print("  1. Feche TODAS as janelas do Chrome")
        print("  2. Execute este script novamente")
        print("")
        return False

    print("  Chrome está fechado. OK!")
    print("")

    # Verificar se arquivo de cookies existe
    print(f"Verificando arquivo de cookies...")
    print(f"  Caminho: {CHROME_COOKIES_PATH}")

    if not os.path.exists(CHROME_COOKIES_PATH):
        print("  ERRO: Arquivo de cookies não encontrado!")
        print("")
        print("TROUBLESHOOTING:")
        print("  1. Verifique se perfil Profile 1 está correto")
        print("  2. Você fez login no Chrome pelo menos uma vez?")
        print("")
        return False

    print("  Arquivo encontrado. OK!")
    print("")

    # Criar diretório para cookies salvos
    os.makedirs(SAVED_COOKIES_DIR, exist_ok=True)

    # Copiar arquivo de cookies (para não corromper original)
    temp_cookies = os.path.join(SAVED_COOKIES_DIR, "Cookies_temp")
    print("Copiando arquivo de cookies...")
    shutil.copy2(CHROME_COOKIES_PATH, temp_cookies)
    print("  Cópia criada. OK!")
    print("")

    # Conectar ao banco de dados SQLite
    print("Lendo cookies do banco de dados...")
    try:
        conn = sqlite3.connect(temp_cookies)
        cursor = conn.cursor()

        # Query para pegar cookies dos domínios alvo
        query = """
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly
            FROM cookies
            WHERE host_key LIKE ?
        """

        all_cookies = []
        for domain in TARGET_DOMAINS:
            cursor.execute(query, (f"%{domain.replace('.', '')}%",))
            cookies = cursor.fetchall()
            all_cookies.extend(cookies)

        conn.close()

        print(f"  Total de cookies encontrados: {len(all_cookies)}")
        print("")

        if len(all_cookies) == 0:
            print("  AVISO: Nenhum cookie encontrado para domínios e-SAJ!")
            print("")
            print("POSSÍVEIS CAUSAS:")
            print("  1. Você não fez login no e-SAJ ainda")
            print("  2. Sessão expirou")
            print("  3. Cookies foram limpos")
            print("")
            print("SOLUÇÃO:")
            print("  1. Abra Chrome (perfil Profile 1 - revisa.precatorio@gmail.com)")
            print("  2. Acesse: https://esaj.tjsp.jus.br/esaj/portal.do")
            print("  3. Faça login com certificado digital")
            print("  4. Feche Chrome")
            print("  5. Execute este script novamente")
            print("")
            return False

        # Converter para formato Selenium
        selenium_cookies = []
        for cookie in all_cookies:
            host_key, name, value, path, expires_utc, is_secure, is_httponly = cookie

            cookie_dict = {
                'name': name,
                'value': value,
                'domain': host_key,
                'path': path,
                'secure': bool(is_secure),
                'httpOnly': bool(is_httponly)
            }

            # Adicionar expiry se existir
            if expires_utc:
                # Chrome usa microsegundos desde 1601, converter para timestamp Unix
                # Simplificação: usar data futura
                cookie_dict['expiry'] = int((datetime.now().timestamp() + 86400 * 30))  # 30 dias

            selenium_cookies.append(cookie_dict)

        # Salvar cookies em arquivo pickle
        print("Salvando cookies...")
        with open(SAVED_COOKIES_FILE, 'wb') as f:
            pickle.dump(selenium_cookies, f)

        print(f"  Cookies salvos em: {SAVED_COOKIES_FILE}")
        print("")

        # Mostrar amostra dos cookies
        print("Amostra de cookies extraídos:")
        for i, cookie in enumerate(selenium_cookies[:5]):
            print(f"  {i+1}. {cookie['name'][:30]:30} | Domain: {cookie['domain']}")

        if len(selenium_cookies) > 5:
            print(f"  ... e mais {len(selenium_cookies) - 5} cookies")

        print("")
        print("=" * 70)
        print("EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print("")
        print(f"Total de cookies salvos: {len(selenium_cookies)}")
        print(f"Arquivo: {SAVED_COOKIES_FILE}")
        print("")
        print("PRÓXIMO PASSO:")
        print("  Execute: python test_with_cookies.py")
        print("")

        # Limpar arquivo temporário
        os.remove(temp_cookies)

        return True

    except Exception as e:
        print(f"  ERRO ao processar cookies: {e}")
        print("")
        import traceback
        traceback.print_exc()
        return False

# ====================
# MAIN
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("EXTRAÇÃO DE COOKIES - e-SAJ")
    print("=" * 70)
    print("")
    print("ESTE SCRIPT VAI:")
    print("  1. Ler cookies do perfil Profile 1 do Chrome (revisa.precatorio@gmail.com)")
    print("  2. Filtrar apenas cookies do domínio tjsp.jus.br")
    print("  3. Salvar em arquivo para uso no Selenium")
    print("")
    print("PRÉ-REQUISITOS:")
    print("  1. Você FEZ LOGIN no e-SAJ com certificado digital")
    print("  2. Chrome está FECHADO (todas as janelas)")
    print("")

    confirm = input("Você fez login no e-SAJ e Chrome está fechado? (SIM/NAO): ")

    if confirm.upper() != "SIM":
        print("")
        print("Por favor, faça login primeiro:")
        print("  1. Abra Chrome (perfil Profile 1 - revisa.precatorio@gmail.com)")
        print("  2. Acesse: https://esaj.tjsp.jus.br/esaj/portal.do")
        print("  3. Clique em 'Certificado Digital'")
        print("  4. Selecione seu certificado")
        print("  5. Aguarde login completo")
        print("  6. FECHE Chrome")
        print("  7. Execute este script novamente")
        print("")
        exit(0)

    print("")
    success = extract_cookies()

    if success:
        print("Extração bem-sucedida!")
        exit(0)
    else:
        print("Extração falhou. Verifique erros acima.")
        exit(1)
