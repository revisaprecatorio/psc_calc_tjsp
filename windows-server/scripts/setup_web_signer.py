"""
Setup Web Signer no Perfil Persistente
========================================

Este script abre Chrome com perfil persistente
para voce instalar Web Signer MANUALMENTE.

Passos:
1. Chrome abre com perfil persistente
2. Acessa Chrome Web Store automaticamente
3. Voce clica em "Adicionar ao Chrome"
4. Instala Web Signer
5. Fecha este script
6. Executa test_authentication_final.py novamente

Uso:
    python setup_web_signer.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# ====================
# CONFIGURACOES
# ====================

CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"
USER_DATA_DIR = r"C:\projetos\crawler_tjsp\chrome-profile-persistent"

# Web Signer Chrome Web Store URL
WEB_SIGNER_URL = "https://chrome.google.com/webstore/detail/web-signer/fpiefhbemjeeekaffbhpbkfjffhmpbgg"

# ====================
# FUNCOES
# ====================

def setup_chrome():
    """Configura Chrome com perfil persistente."""
    print("Configurando Chrome...")
    print(f"  Perfil: {USER_DATA_DIR}")

    os.makedirs(USER_DATA_DIR, exist_ok=True)

    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # Perfil persistente
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

    # Argumentos Windows Server
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")

    # Service
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        print("  Iniciando Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("  Chrome iniciado!")
        return driver
    except Exception as e:
        print(f"  ERRO: {e}")
        raise

def install_web_signer(driver):
    """Abre Chrome Web Store para instalacao manual."""
    print("")
    print("=" * 70)
    print("INSTALACAO WEB SIGNER")
    print("=" * 70)
    print("")

    # Acessar Chrome Web Store
    print("Abrindo Chrome Web Store (Web Signer)...")
    driver.get(WEB_SIGNER_URL)
    time.sleep(3)

    print("")
    print("=" * 70)
    print("ACAO NECESSARIA:")
    print("=" * 70)
    print("")
    print("1. Na pagina aberta, clique em 'Adicionar ao Chrome'")
    print("2. Confirme a instalacao")
    print("3. Aguarde Web Signer ser instalado")
    print("4. Feche a aba de extensoes se abrir")
    print("")
    print("Quando terminar, volte aqui e pressione Enter...")
    print("")

    input("Pressione Enter apos instalar Web Signer...")

    # Verificar extensoes
    print("")
    print("Abrindo pagina de extensoes para verificacao...")
    driver.get("chrome://extensions/")
    time.sleep(2)

    print("")
    print("=" * 70)
    print("VERIFICACAO:")
    print("=" * 70)
    print("")
    print("Na pagina de extensoes, verifique:")
    print("  - Web Signer (Softplan) aparece na lista?")
    print("  - Esta HABILITADO (toggle azul)?")
    print("")

    response = input("Web Signer esta instalado e habilitado? (SIM/NAO): ")

    if response.upper() == "SIM":
        print("")
        print("=" * 70)
        print("SUCESSO! WEB SIGNER INSTALADO!")
        print("=" * 70)
        print("")
        print("PROXIMO PASSO:")
        print("  Execute: python windows-server\\scripts\\test_authentication_final.py")
        print("")
        return True
    else:
        print("")
        print("=" * 70)
        print("INSTALACAO INCOMPLETA")
        print("=" * 70)
        print("")
        print("Tente novamente:")
        print("  1. Acesse: chrome://extensions/")
        print("  2. Procure 'Web Signer (Softplan)'")
        print("  3. Se nao aparecer, reinstale pela Chrome Web Store")
        print("")
        return False

# ====================
# MAIN
# ====================

def main():
    """Executa setup."""
    driver = None

    try:
        print("")
        print("=" * 70)
        print("SETUP WEB SIGNER - PERFIL PERSISTENTE")
        print("=" * 70)
        print("")
        print("Este script vai:")
        print("  1. Abrir Chrome com perfil persistente")
        print("  2. Acessar Chrome Web Store (Web Signer)")
        print("  3. Voce instala manualmente")
        print("  4. Web Signer fica salvo no perfil")
        print("")
        print("Depois disso, test_authentication_final.py vai funcionar!")
        print("")
        input("Pressione Enter para continuar...")

        # Setup Chrome
        driver = setup_chrome()

        # Instalar Web Signer
        success = install_web_signer(driver)

        # Aguardar
        print("")
        print("Aguardando 5 segundos antes de fechar...")
        time.sleep(5)

        if success:
            print("")
            print("Setup concluido com sucesso!")
            print("")

    except Exception as e:
        print(f"ERRO: {e}")

    finally:
        if driver:
            print("Fechando Chrome...")
            driver.quit()
            print("Chrome fechado")

        print("")
        print("=" * 70)
        print("SETUP FINALIZADO")
        print("=" * 70)
        print("")

if __name__ == "__main__":
    main()
