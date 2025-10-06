"""
TESTE FINAL - Autenticacao e-SAJ (SEM Remote Debugging)
========================================================

CONCLUSAO DIAGNOSTICO:
- Remote Debugging NAO funciona no Windows Server 2016
- Bug/limitacao do Chrome 131 em ambiente Server

SOLUCAO FINAL:
- Selenium inicia Chrome normalmente (sem Remote Debugging)
- Perfil temporario (evita bug DevToolsActivePort)
- Login manual com certificado UMA VEZ
- Sessao salva no perfil temporario
- Reutilizacao de sessao em execucoes futuras

Uso:
    python test_authentication_final.py
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

CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver.exe"

# PERFIL PERSISTENTE: Mantem sessao entre execucoes
USER_DATA_DIR = r"C:\projetos\crawler_tjsp\chrome-profile-persistent"

SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_auth_final.log"
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
    log(f"Screenshot: {filepath}")
    return filepath

def setup_chrome():
    """Configura e inicia Chrome via Selenium."""
    log("Configurando Chrome...")
    log(f"  Perfil persistente: {USER_DATA_DIR}")

    # Criar diretorio se nao existir
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    # Opcoes Chrome
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # Perfil persistente (sessao mantida)
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")

    # Argumentos Windows Server (estabilidade)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")

    # Configuracoes
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-web-security")

    # Preferencias
    prefs = {
        "download.default_directory": r"C:\projetos\crawler_tjsp\downloads",
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Service
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        log("  Iniciando Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("  Chrome iniciado!")

        # Timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        return driver

    except Exception as e:
        log(f"  ERRO: {e}", "ERROR")
        raise

def check_if_logged_in(driver):
    """Verifica se ja esta logado."""
    current_url = driver.current_url

    # Indicadores de login
    if "servico=" in current_url:
        return True
    if "painel" in current_url.lower():
        return True

    # Verificar se tem nome de usuario
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'Sair')]")
        return True
    except:
        pass

    return False

def test_authentication(driver):
    """Testa autenticacao com certificado digital."""
    log("=" * 70)
    log("TESTE DE AUTENTICACAO - e-SAJ TJSP")
    log("=" * 70)

    # Acessar portal
    log("Acessando portal e-SAJ...")
    driver.get(ESAJ_URL)
    time.sleep(3)
    log(f"  Titulo: {driver.title}")
    save_screenshot(driver, "01_portal")

    # Verificar se ja esta logado
    if check_if_logged_in(driver):
        log("=" * 70)
        log("JA ESTA LOGADO! Sessao mantida do perfil persistente!", "SUCCESS")
        log("=" * 70)
        log(f"URL: {driver.current_url}")
        save_screenshot(driver, "02_already_logged")
        return True

    # Procurar botao Certificado Digital
    log("Procurando botao 'Certificado Digital'...")
    try:
        cert_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
        )
        log("  Botao encontrado!")
    except Exception as e:
        log(f"  Botao NAO encontrado: {e}", "ERROR")
        save_screenshot(driver, "03_button_not_found")

        # Verificar extensoes
        log("")
        log("Verificando extensoes Chrome...", "WARNING")
        driver.get("chrome://extensions/")
        time.sleep(2)
        save_screenshot(driver, "04_extensions")

        log("")
        log("AVISO:", "WARNING")
        log("  Web Signer nao esta instalado neste perfil.", "WARNING")
        log("  SOLUCAO:", "WARNING")
        log("    1. Instale Web Signer manualmente:", "WARNING")
        log("       https://chrome.google.com/webstore/detail/web-signer", "WARNING")
        log("    2. Execute este script novamente", "WARNING")
        log("")

        return False

    # Clicar no botao
    log("Clicando em 'Certificado Digital'...")
    cert_button.click()
    time.sleep(2)
    save_screenshot(driver, "05_after_click")

    # Aguardar selecao manual
    log("=" * 70)
    log("AGUARDANDO SELECAO DO CERTIFICADO (30 segundos)...")
    log("=" * 70)
    log("ACAO NECESSARIA:")
    log("  - Modal do Web Signer deve aparecer")
    log("  - Selecione o certificado na lista")
    log("  - Digite a senha se solicitado")
    log("  - Aguarde redirecionamento")
    log("")

    for i in range(30, 0, -1):
        if i % 5 == 0:
            log(f"   {i} segundos restantes...")
        time.sleep(1)

    # Verificar login
    log("Verificando login...")
    current_url = driver.current_url
    log(f"  URL atual: {current_url}")

    if check_if_logged_in(driver):
        log("=" * 70)
        log("LOGIN BEM-SUCEDIDO!", "SUCCESS")
        log("=" * 70)
        log("")
        log("IMPORTANTE:")
        log("  Sessao salva em: {USER_DATA_DIR}")
        log("  Proximas execucoes NAO precisarao de login manual!")
        log("")
        save_screenshot(driver, "06_login_success")
        return True
    else:
        log("=" * 70)
        log("LOGIN FALHOU", "ERROR")
        log("=" * 70)
        save_screenshot(driver, "06_login_failed")
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
        log("TESTE FINAL - AUTENTICACAO e-SAJ")
        log("Windows Server - Solucao sem Remote Debugging")
        log("=" * 70)
        log("")

        # 1. Iniciar Chrome
        driver = setup_chrome()

        # 2. Testar autenticacao
        success = test_authentication(driver)

        # Aguardar
        log("")
        log("Aguardando 10 segundos...")
        time.sleep(10)

    except Exception as e:
        log(f"ERRO: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
        success = False

    finally:
        # Fechar Chrome
        if driver:
            log("Fechando Chrome...")
            driver.quit()
            log("  Chrome fechado")

        log("")
        log("=" * 70)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 70)
        log(f"Log: {LOG_FILE}")
        log(f"Screenshots: {SCREENSHOTS_DIR}")
        log("")

    return success

# ====================
# EXECUCAO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("TESTE FINAL - AUTENTICACAO e-SAJ")
    print("Windows Server - Crawler TJSP")
    print("=" * 70)
    print("")
    print("SOLUCAO FINAL:")
    print("  - Selenium inicia Chrome normalmente")
    print("  - Perfil persistente (sessao mantida)")
    print("  - Login manual necessario apenas na PRIMEIRA vez")
    print("  - Proximas execucoes: login automatico")
    print("")
    print("DIAGNOSTICO ANTERIOR:")
    print("  Remote Debugging nao funciona no Windows Server 2016")
    print("  Esta solucao contorna essa limitacao")
    print("")
    input("Pressione Enter para iniciar...")
    print("")

    result = run_test()

    print("")
    if result:
        print("TESTE PASSOU! Autenticacao funcionou!")
        print("")
        print("PROXIMOS PASSOS:")
        print("  1. Testar acesso direto a processos")
        print("  2. Validar sessao persistente")
        print("  3. Integrar com crawler principal")
        print("")
        exit(0)
    else:
        print("TESTE FALHOU!")
        print("")
        print("TROUBLESHOOTING:")
        print("  1. Web Signer instalado? (chrome://extensions)")
        print("  2. Certificado importado? (certmgr.msc)")
        print("  3. Verificar logs e screenshots")
        print("")
        exit(1)
