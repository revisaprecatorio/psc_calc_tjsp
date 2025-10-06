"""
TESTE - Profile 1 Direct Access
================================

Este script testa se conseguimos iniciar o Selenium diretamente no Profile 1
(revisa.precatorio@gmail.com) onde o Web Signer está instalado.

OBJETIVO: Iniciar Chrome no perfil correto sem precisar trocar manualmente
RESULTADO ESPERADO: Chrome abre com Web Signer disponível

Uso:
    python test_profile1_direct.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

# ====================
# CONFIGURAÇÕES
# ====================

CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"

# PERFIL CORRETO: Profile 1 (revisa.precatorio@gmail.com)
USER_DATA_DIR = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data"
PROFILE_DIRECTORY = "Profile 1"

SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_profile1.log"

ESAJ_URL = "https://esaj.tjsp.jus.br/esaj/portal.do"

# ====================
# FUNÇÕES AUXILIARES
# ====================

def log(message, level="INFO"):
    """Escreve mensagem no log e console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def save_screenshot(driver, name):
    """Salva screenshot com timestamp."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
    driver.save_screenshot(filepath)
    log(f"Screenshot salvo: {filepath}")
    return filepath

def setup_chrome():
    """Configura e retorna instância do Chrome via Selenium."""
    log("Configurando Chrome...")
    log(f"  User Data Dir: {USER_DATA_DIR}")
    log(f"  Profile: {PROFILE_DIRECTORY}")

    # Opções do Chrome
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # CONFIGURAÇÃO CRÍTICA: Usar Profile 1 (revisa.precatorio@gmail.com)
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument(f"--profile-directory={PROFILE_DIRECTORY}")
    log(f"  Usando perfil: {PROFILE_DIRECTORY}")

    # Argumentos Windows Server (estabilidade)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    log(f"  Argumentos Windows Server aplicados")

    # Configurações adicionais
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")

    # Preferências
    prefs = {
        "download.default_directory": r"C:\projetos\crawler_tjsp\downloads",
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Service (ChromeDriver)
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        log("  Iniciando Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("  Chrome iniciado com sucesso!")

        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        return driver
    except Exception as e:
        log(f"  ERRO ao iniciar Chrome: {e}", "ERROR")
        raise

# ====================
# TESTE PRINCIPAL
# ====================

def test_profile1():
    """
    Teste de acesso direto ao Profile 1.
    """
    driver = None
    success = False

    try:
        log("=" * 70)
        log("TESTE - PROFILE 1 DIRECT ACCESS")
        log("=" * 70)

        # 1. Iniciar Chrome
        driver = setup_chrome()

        # 2. Acessar e-SAJ
        log("Acessando e-SAJ...")
        driver.get(ESAJ_URL)
        time.sleep(3)

        log(f"  Página carregada: {driver.title}")
        save_screenshot(driver, "01_esaj_homepage")

        # 3. Clicar no botão "Certificado Digital"
        log("Procurando botão 'Certificado Digital'...")
        try:
            cert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
            )
            log("  Botão 'Certificado Digital' encontrado!")
        except Exception as e:
            log(f"  Botão não encontrado: {e}", "ERROR")
            save_screenshot(driver, "02_button_not_found")
            return False

        log("Clicando em 'Certificado Digital'...")
        cert_button.click()
        time.sleep(2)
        save_screenshot(driver, "03_after_click_cert")

        # 4. Verificar se apareceu seleção de certificado
        log("=" * 70)
        log("VERIFICANDO WEB SIGNER...")
        log("=" * 70)
        log("")
        log("AÇÃO NECESSÁRIA:")
        log("  1. Verificar se modal do Web Signer apareceu")
        log("  2. Verificar se certificado está na lista")
        log("  3. Selecionar certificado")
        log("  4. Clicar em 'Entrar'")
        log("")

        # Aguardar 30 segundos para seleção manual
        log("Aguardando 30 segundos para seleção do certificado...")
        for i in range(30, 0, -1):
            if i % 5 == 0:
                log(f"  {i} segundos restantes...")
            time.sleep(1)

        # 5. Verificar se login foi bem-sucedido
        log("Verificando se login foi bem-sucedido...")
        current_url = driver.current_url
        log(f"  URL atual: {current_url}")

        if "portal.do?servico=" in current_url or "painel" in current_url.lower():
            log("=" * 70)
            log("SUCESSO! LOGIN COM CERTIFICADO FUNCIONOU!", "SUCCESS")
            log("=" * 70)
            log(f"URL pós-login: {current_url}")
            save_screenshot(driver, "04_login_success")
            success = True

            log("")
            log("RESULTADO:")
            log("  Profile 1 carregado corretamente!")
            log("  Web Signer funcionou!")
            log("  Autenticação bem-sucedida!")
            log("")

        else:
            log("=" * 70)
            log("FALHA - Login não foi concluído", "ERROR")
            log("=" * 70)
            log(f"URL obtida: {current_url}")
            save_screenshot(driver, "04_login_failed")

            log("")
            log("Possíveis causas:")
            log("  1. Web Signer não abriu modal")
            log("  2. Certificado não foi selecionado")
            log("  3. Profile 1 não tem Web Signer instalado")
            log("")

        # Aguardar antes de fechar
        log("Aguardando 10 segundos antes de fechar...")
        time.sleep(10)

    except Exception as e:
        log(f"ERRO DURANTE TESTE: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
        success = False

    finally:
        if driver:
            log("Fechando Chrome...")
            driver.quit()
            log("  Chrome fechado")

        log("=" * 70)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 70)
        log(f"Log completo: {LOG_FILE}")
        log(f"Screenshots: {SCREENSHOTS_DIR}")

    return success

# ====================
# EXECUÇÃO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("TESTE - PROFILE 1 DIRECT ACCESS")
    print("=" * 70)
    print("")
    print("Este script vai:")
    print("  1. Iniciar Chrome no Profile 1 (revisa.precatorio@gmail.com)")
    print("  2. Acessar e-SAJ")
    print("  3. Clicar em 'Certificado Digital'")
    print("  4. Aguardar você selecionar o certificado")
    print("")
    print("IMPORTANTE:")
    print("  - Web Signer deve estar rodando")
    print("  - Certificado deve estar importado")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = test_profile1()

    print("")
    if result:
        print("SUCESSO! Profile 1 funciona com Web Signer!")
        exit(0)
    else:
        print("FALHA! Verificar logs.")
        exit(1)
