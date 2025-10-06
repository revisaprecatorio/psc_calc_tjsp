"""
Teste de Autenticação com Cookies Injetados
============================================

Este script testa a autenticação no e-SAJ usando cookies salvos
previamente de uma sessão autenticada.

OBJETIVO: Validar que cookie injection funciona para manter sessão autenticada
RESULTADO ESPERADO: Acesso direto à área logada sem precisar de certificado

Uso:
    python test_with_cookies.py

Pré-requisitos:
    - Cookies salvos em saved_cookies/esaj_cookies.pkl
    - Chrome instalado
    - ChromeDriver instalado
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os
from datetime import datetime

# ====================
# CONFIGURAÇÕES
# ====================

CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"

# Arquivo de cookies salvos
SAVED_COOKIES_FILE = r"C:\projetos\crawler_tjsp\saved_cookies\esaj_cookies.pkl"

SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_cookies.log"

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

    # Opções do Chrome
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # Argumentos Windows Server (estabilidade)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    log("  Argumentos Windows Server aplicados")

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

def load_cookies(driver):
    """Carrega cookies salvos no driver."""
    log("Carregando cookies salvos...")

    if not os.path.exists(SAVED_COOKIES_FILE):
        log(f"  ERRO: Arquivo de cookies não encontrado: {SAVED_COOKIES_FILE}", "ERROR")
        log("  Execute primeiro: python import_cookies_from_json.py", "ERROR")
        return False

    # Carregar cookies do arquivo
    with open(SAVED_COOKIES_FILE, 'rb') as f:
        cookies = pickle.load(f)

    log(f"  Total de cookies carregados: {len(cookies)}")

    # Primeiro, acessar o domínio para poder adicionar cookies
    log("  Acessando domínio base para injetar cookies...")
    driver.get("https://esaj.tjsp.jus.br")
    time.sleep(2)

    # Adicionar cada cookie
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            log(f"  Aviso: Não foi possível adicionar cookie {cookie['name']}: {e}", "WARN")

    log("  Cookies injetados com sucesso!")
    return True

# ====================
# TESTE PRINCIPAL
# ====================

def test_with_cookies():
    """
    Teste de autenticação com cookies injetados.
    """
    driver = None
    success = False

    try:
        log("=" * 70)
        log("TESTE DE AUTENTICAÇÃO COM COOKIES - e-SAJ TJSP")
        log("=" * 70)

        # 1. Iniciar Chrome
        driver = setup_chrome()

        # 2. Carregar cookies
        if not load_cookies(driver):
            return False

        # 3. Acessar e-SAJ (agora com cookies)
        log("Acessando e-SAJ com cookies injetados...")
        driver.get(ESAJ_URL)
        time.sleep(3)

        log(f"  Página carregada: {driver.title}")
        save_screenshot(driver, "01_esaj_with_cookies")

        # 4. Verificar se está autenticado
        log("Verificando autenticação...")
        current_url = driver.current_url
        page_source = driver.page_source

        log(f"  URL atual: {current_url}")

        # Verificar indicadores de autenticação
        is_authenticated = False

        # Indicador 1: URL contém "servico="
        if "servico=" in current_url or "painel" in current_url.lower():
            log("  ✓ URL indica autenticação (contém 'servico=' ou 'painel')")
            is_authenticated = True

        # Indicador 2: Procurar por elementos da área logada
        try:
            # Procurar por "Painel do advogado" ou nome do usuário
            if "Painel" in page_source or "advogado" in page_source.lower():
                log("  ✓ Página contém elementos da área logada")
                is_authenticated = True
        except:
            pass

        # Indicador 3: NÃO tem botão "Certificado Digital"
        try:
            cert_button = driver.find_element(By.LINK_TEXT, "Certificado Digital")
            log("  ✗ Ainda na página de login (botão 'Certificado Digital' presente)")
            is_authenticated = False
        except:
            log("  ✓ Não está na página de login (sem botão 'Certificado Digital')")
            is_authenticated = True

        # 5. Resultado
        if is_authenticated:
            log("=" * 70)
            log("✅✅✅ SUCESSO! AUTENTICAÇÃO COM COOKIES FUNCIONOU! ✅✅✅", "SUCCESS")
            log("=" * 70)
            log(f"URL pós-login: {current_url}")
            save_screenshot(driver, "02_authenticated_success")
            success = True

            log("")
            log("🎉 RESULTADO:")
            log("  ✅ Cookie injection funcionou!")
            log("  ✅ Acesso à área logada sem certificado!")
            log("  ✅ Sessão mantida com sucesso!")
            log("")
            log("📋 PRÓXIMOS PASSOS:")
            log("  1. Integrar com crawler principal")
            log("  2. Implementar renovação de cookies quando expirarem")
            log("  3. Testar extração de dados de processos")
            log("")

        else:
            log("=" * 70)
            log("❌ FALHA - Cookies não mantiveram sessão", "ERROR")
            log("=" * 70)
            log(f"URL obtida: {current_url}")
            save_screenshot(driver, "02_authentication_failed")

            log("")
            log("Possíveis causas:")
            log("  1. Cookies expiraram")
            log("  2. Sessão foi invalidada no servidor")
            log("  3. IP diferente do login original")
            log("  4. Cookies incompletos")
            log("")
            log("SOLUÇÃO:")
            log("  1. Exportar cookies novamente (sessão ativa)")
            log("  2. Executar import_cookies_from_json.py")
            log("  3. Executar este teste imediatamente")
            log("")

        # Aguardar antes de fechar
        log("Aguardando 10 segundos antes de fechar...")
        time.sleep(10)

    except Exception as e:
        log(f"ERRO DURANTE TESTE: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
        import traceback
        traceback.print_exc()
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
    print("TESTE DE AUTENTICAÇÃO COM COOKIES - CRAWLER TJSP")
    print("=" * 70)
    print("")
    print("Este script vai:")
    print("  1. Iniciar Chrome")
    print("  2. Injetar cookies salvos")
    print("  3. Acessar e-SAJ")
    print("  4. Verificar se está autenticado")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = test_with_cookies()

    print("")
    if result:
        print("✅ TESTE PASSOU! Cookie injection funciona!")
        exit(0)
    else:
        print("❌ TESTE FALHOU! Verificar logs.")
        exit(1)
