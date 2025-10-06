"""
TESTE #1 - Autenticacao e-SAJ (REMOTE DEBUGGING V2)
===================================================

Versao 2: Usa chrome_options.add_experimental_option("debuggerAddress")
ao inves de chrome_options.debugger_address

Uso:
    1. Execute start_chrome_debug.bat PRIMEIRO
    2. Execute: python test_authentication_remote_v2.py
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
# CONFIGURACOES
# ====================

CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"
REMOTE_DEBUGGING_PORT = 9222
SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_auth_remote_v2.log"
ESAJ_URL = "https://esaj.tjsp.jus.br/esaj/portal.do"

# ====================
# FUNCOES AUXILIARES
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

def connect_to_chrome_v2():
    """Conecta ao Chrome via Remote Debugging - VERSAO 2."""
    log("Conectando ao Chrome via Remote Debugging (V2)...")
    log(f"  Porta: {REMOTE_DEBUGGING_PORT}")
    log(f"  ChromeDriver: {CHROMEDRIVER_PATH}")

    # Opcoes Chrome
    chrome_options = Options()

    # METODO 2: usar add_experimental_option
    chrome_options.add_experimental_option("debuggerAddress", f"localhost:{REMOTE_DEBUGGING_PORT}")

    # Service
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        log("  Iniciando ChromeDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("  Conectado com sucesso!")

        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        # Mostrar URL atual
        current_url = driver.current_url
        log(f"  URL atual: {current_url}")

        return driver
    except Exception as e:
        log(f"  ERRO ao conectar: {e}", "ERROR")
        log("", "ERROR")
        log("TROUBLESHOOTING:", "ERROR")
        log("  1. Chrome esta aberto com Remote Debugging?", "ERROR")
        log("  2. Execute: start_chrome_debug.bat", "ERROR")
        log("  3. Verifique porta 9222:", "ERROR")
        log("     netstat -ano | findstr :9222", "ERROR")
        log("  4. Verifique ChromeDriver compativel com Chrome", "ERROR")
        raise

def test_authentication(driver):
    """Testa autenticacao com certificado digital."""
    log("=" * 70)
    log("TESTE DE AUTENTICACAO - e-SAJ TJSP")
    log("=" * 70)

    # Pegar URL atual primeiro
    current_url = driver.current_url
    log(f"URL inicial: {current_url}")

    # Se ja estiver em alguma pagina, salvar screenshot
    save_screenshot(driver, "00_initial_state")

    # Verificar se ja esta logado
    if "servico=" in current_url or "painel" in current_url.lower():
        log("=" * 70)
        log("JA ESTA LOGADO! Sessao mantida!", "SUCCESS")
        log("=" * 70)
        save_screenshot(driver, "01_already_logged_in")
        return True

    # Acessar portal e-SAJ
    log("Acessando portal e-SAJ...")
    driver.get(ESAJ_URL)
    time.sleep(3)
    log(f"  Pagina carregada: {driver.title}")
    save_screenshot(driver, "02_portal_esaj")

    # Verificar novamente se ja esta logado (redirect automatico)
    current_url = driver.current_url
    if "servico=" in current_url or "painel" in current_url.lower():
        log("=" * 70)
        log("LOGIN AUTOMATICO! Sessao ja estava ativa!", "SUCCESS")
        log("=" * 70)
        save_screenshot(driver, "03_auto_logged_in")
        return True

    # Procurar botao "Certificado Digital"
    log("Procurando botao 'Certificado Digital'...")
    try:
        cert_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
        )
        log("  Botao 'Certificado Digital' encontrado!")
    except Exception as e:
        log(f"  Botao nao encontrado: {e}", "ERROR")
        save_screenshot(driver, "04_button_not_found")

        # Verificar extensoes
        log("")
        log("Verificando extensoes Chrome...", "WARNING")
        driver.get("chrome://extensions/")
        time.sleep(2)
        save_screenshot(driver, "05_extensions_check")

        return False

    # Clicar no botao
    log("Clicando em 'Certificado Digital'...")
    cert_button.click()
    time.sleep(2)
    save_screenshot(driver, "06_after_click_cert")

    # Aguardar selecao manual do certificado
    log("=" * 70)
    log("AGUARDANDO SELECAO DO CERTIFICADO (30 segundos)...")
    log("=" * 70)
    log("ACAO NECESSARIA:")
    log("   - Modal do Web Signer deve aparecer")
    log("   - Selecione o certificado na lista")
    log("   - Aguarde redirecionamento")
    log("")

    for i in range(30, 0, -1):
        if i % 5 == 0:
            log(f"   {i} segundos restantes...")
        time.sleep(1)

    # Verificar se login foi bem-sucedido
    log("Verificando se login foi bem-sucedido...")
    current_url = driver.current_url
    log(f"  URL atual: {current_url}")

    if "servico=" in current_url or "painel" in current_url.lower():
        log("=" * 70)
        log("LOGIN BEM-SUCEDIDO!", "SUCCESS")
        log("=" * 70)
        save_screenshot(driver, "07_login_success")
        return True
    else:
        log("=" * 70)
        log("LOGIN FALHOU", "ERROR")
        log("=" * 70)
        save_screenshot(driver, "07_login_failed")
        return False

# ====================
# TESTE PRINCIPAL
# ====================

def run_test():
    """Executa teste completo."""
    driver = None
    success = False

    try:
        log("=" * 70)
        log("TESTE #1 - AUTENTICACAO VIA REMOTE DEBUGGING V2")
        log("Windows Server - Crawler TJSP")
        log("=" * 70)
        log("")

        # 1. Conectar ao Chrome ja aberto
        driver = connect_to_chrome_v2()

        # 2. Testar autenticacao
        success = test_authentication(driver)

        # Aguardar antes de finalizar
        log("")
        log("Aguardando 10 segundos antes de finalizar...")
        time.sleep(10)

    except Exception as e:
        log(f"ERRO DURANTE TESTE: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
        success = False

    finally:
        # NAO FECHAR driver! Chrome deve continuar rodando
        # driver.quit() <- NAO FAZER!

        log("")
        log("=" * 70)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 70)
        log(f"Log completo: {LOG_FILE}")
        log(f"Screenshots: {SCREENSHOTS_DIR}")
        log("")
        log("Chrome continua rodando.")
        log("")

    return success

# ====================
# EXECUCAO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("TESTE #1 - AUTENTICACAO VIA REMOTE DEBUGGING V2")
    print("Windows Server - Crawler TJSP")
    print("=" * 70)
    print("")
    print("VERSAO 2:")
    print("   - Usa add_experimental_option('debuggerAddress')")
    print("   - Compativel com ChromeDriver mais antigos")
    print("")
    print("IMPORTANTE:")
    print("   - Chrome DEVE estar rodando via Remote Debugging")
    print("   - Execute start_chrome_debug.bat antes")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = run_test()

    print("")
    if result:
        print("TESTE PASSOU!")
        exit(0)
    else:
        print("TESTE FALHOU!")
        exit(1)
