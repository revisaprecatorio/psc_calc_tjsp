"""
TESTE #1 - Autenticação e-SAJ (REMOTE DEBUGGING)
================================================

Este script CONECTA em Chrome já aberto via Remote Debugging.

PREMISSA:
- Chrome foi aberto com: start_chrome_remote_debugging.ps1
- Chrome está rodando com perfil revisa.precatorio@gmail.com
- Web Signer já está carregado
- Remote debugging porta 9222 ativa

Uso:
    1. Execute start_chrome_remote_debugging.ps1 PRIMEIRO
    2. Execute: python test_authentication_remote.py
"""

from selenium import webdriver
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

REMOTE_DEBUGGING_URL = "http://localhost:9222"
SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_auth_remote.log"
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

def connect_to_chrome():
    """Conecta ao Chrome já aberto via Remote Debugging."""
    log("Conectando ao Chrome via Remote Debugging...")
    log(f"  URL: {REMOTE_DEBUGGING_URL}")

    chrome_options = Options()
    chrome_options.debugger_address = "localhost:9222"

    try:
        driver = webdriver.Chrome(options=chrome_options)
        log("  Conectado com sucesso!")

        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        return driver
    except Exception as e:
        log(f"  ERRO ao conectar: {e}", "ERROR")
        log("", "ERROR")
        log("TROUBLESHOOTING:", "ERROR")
        log("  1. Chrome esta aberto?", "ERROR")
        log("  2. Execute: start_chrome_remote_debugging.ps1", "ERROR")
        log("  3. Verifique porta 9222 esta livre", "ERROR")
        raise

def test_authentication(driver):
    """Testa autenticação com certificado digital."""
    log("=" * 70)
    log("TESTE DE AUTENTICACAO - e-SAJ TJSP")
    log("=" * 70)

    # Acessar portal e-SAJ
    log("Acessando portal e-SAJ...")
    driver.get(ESAJ_URL)
    time.sleep(3)
    log(f"  Pagina carregada: {driver.title}")
    save_screenshot(driver, "01_portal_esaj")

    # Verificar se já está logado
    current_url = driver.current_url
    if "servico=" in current_url or "painel" in current_url.lower():
        log("=" * 70)
        log("JA ESTA LOGADO! Sessao mantida do perfil Default!", "SUCCESS")
        log("=" * 70)
        log(f"URL: {current_url}")
        save_screenshot(driver, "02_already_logged_in")
        return True

    # Procurar botão "Certificado Digital"
    log("Procurando botao 'Certificado Digital'...")
    try:
        cert_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
        )
        log("  Botao 'Certificado Digital' encontrado!")
    except Exception as e:
        log(f"  Botao nao encontrado: {e}", "ERROR")
        save_screenshot(driver, "02_button_not_found")

        # Verificar se Web Signer está carregado
        log("")
        log("Verificando extensoes Chrome...", "WARNING")
        driver.get("chrome://extensions/")
        time.sleep(2)
        save_screenshot(driver, "03_extensions_check")

        return False

    # Clicar no botão
    log("Clicando em 'Certificado Digital'...")
    cert_button.click()
    time.sleep(2)
    save_screenshot(driver, "04_after_click_cert")

    # Aguardar seleção manual do certificado
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
        save_screenshot(driver, "05_login_success")
        return True
    else:
        log("=" * 70)
        log("LOGIN FALHOU", "ERROR")
        log("=" * 70)
        save_screenshot(driver, "05_login_failed")
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
        log("TESTE #1 - AUTENTICACAO VIA REMOTE DEBUGGING")
        log("Windows Server - Crawler TJSP")
        log("=" * 70)
        log("")

        # 1. Conectar ao Chrome já aberto
        driver = connect_to_chrome()

        # 2. Testar autenticação
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
        # NÃO FECHAR driver! Chrome deve continuar rodando
        # driver.quit() <- NAO FAZER ISSO!

        log("")
        log("=" * 70)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 70)
        log(f"Log completo: {LOG_FILE}")
        log(f"Screenshots: {SCREENSHOTS_DIR}")
        log("")
        log("Chrome continua rodando para proximos testes.")
        log("")

    return success

# ====================
# EXECUÇÃO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("TESTE #1 - AUTENTICACAO VIA REMOTE DEBUGGING")
    print("Windows Server - Crawler TJSP")
    print("=" * 70)
    print("")
    print("IMPORTANTE:")
    print("   - Chrome DEVE estar rodando via Remote Debugging")
    print("   - Execute start_chrome_remote_debugging.ps1 antes")
    print("   - Web Signer deve estar carregado")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = run_test()

    print("")
    if result:
        print("TESTE PASSOU! Autenticacao funcionou!")
        print("")
        print("PROXIMOS PASSOS:")
        print("   1. Execute test_direct_process_access_remote.py")
        print("   2. Valide sessao persiste entre requests")
        print("")
        exit(0)
    else:
        print("TESTE FALHOU! Verificar logs.")
        print("")
        print("TROUBLESHOOTING:")
        print("   1. Chrome esta rodando com Remote Debugging?")
        print("   2. Web Signer esta carregado?")
        print("   3. Certificado esta instalado?")
        print("")
        exit(1)
