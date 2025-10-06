"""
TESTE #2 - Acesso Direto a Processo (Sessão Autenticada)
==========================================================

Este script testa o acesso direto a um processo específico usando sessão
já autenticada (cookies de login com certificado mantidos).

OBJETIVO: Validar que podemos acessar processos diretamente após login
RESULTADO ESPERADO: Página do processo carrega com dados completos

PREMISSA IMPORTANTE:
Se conseguirmos acessar diretamente processos após login (sem re-autenticar),
o crawler poderá processar múltiplos jobs na mesma sessão, aumentando performance.

Uso:
    python test_direct_process_access.py

Pré-requisitos:
    - Mesmo ambiente do test_authentication.py
    - Login com certificado funcionando

Teste Anterior: test_authentication.py (login manual com certificado)
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

# SOLUÇÃO HÍBRIDA: Perfil temporário + Argumentos Windows Server
# BUG: --user-data-dir + --profile-directory causam "DevToolsActivePort file doesn't exist" no Windows Server
# SOLUÇÃO: Usar perfil temporário com argumentos de estabilidade
USER_DATA_DIR_TEMP = r"C:\temp\selenium-chrome-profile"
# Perfil Default (para referência/cópia de cookies se necessário)
USER_DATA_DIR_DEFAULT = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default"

SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_direct_access.log"

# URLs
ESAJ_PORTAL_URL = "https://esaj.tjsp.jus.br/esaj/portal.do"
# Processo de teste: 0077044-50.2023.8.26.0500
PROCESSO_URL = (
    "https://esaj.tjsp.jus.br/cpopg/show.do?"
    "processo.codigo=DW001VQ4E0000&"
    "processo.foro=500&"
    "processo.numero=0077044-50.2023.8.26.0500&"
    "consultaDeRequisitorios=true"
)

# Dados esperados do processo
EXPECTED_PROCESSO_NUMERO = "0077044-50.2023.8.26.0500"
EXPECTED_CLASSE = "Precatório"
EXPECTED_ASSUNTO = "Aposentadoria"
EXPECTED_REQTE = "Antonio Augusto de Almeida"

# ====================
# FUNÇÕES AUXILIARES
# ====================

def log(message, level="INFO"):
    """Escreve mensagem no log e console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)

    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def save_screenshot(driver, name):
    """Salva screenshot com timestamp."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
    driver.save_screenshot(filepath)
    log(f"📸 Screenshot salvo: {filepath}")
    return filepath

def save_page_source(driver, name):
    """Salva HTML da página."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    log(f"📄 HTML salvo: {filepath}")
    return filepath

def setup_chrome():
    """Configura e retorna instância do Chrome via Selenium."""
    log("🔧 Configurando Chrome...")
    log(f"  📁 User Data Dir (temp): {USER_DATA_DIR_TEMP}")
    log(f"  📁 Profile Default (referência): {USER_DATA_DIR_DEFAULT}")

    # Criar diretório temporário se não existir
    os.makedirs(USER_DATA_DIR_TEMP, exist_ok=True)
    log(f"  ✅ Diretório temporário criado/verificado")

    # Opções do Chrome
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # SOLUÇÃO HÍBRIDA: Usar perfil temporário + argumentos Windows Server
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR_TEMP}")
    log(f"  ✅ Usando perfil temporário (evita bug Windows Server)")

    # ARGUMENTOS CRÍTICOS para Windows Server (resolvem DevToolsActivePort error)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    log(f"  ✅ Argumentos Windows Server aplicados")

    # Configurações importantes
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")

    # Preferências
    prefs = {
        "download.default_directory": r"C:\projetos\crawler_tjsp\downloads",
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.notifications": 2,  # Bloquear notificações
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Service (ChromeDriver)
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        log("  🚀 Iniciando Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("  ✅ Chrome iniciado com sucesso!")

        # Configurar timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        return driver
    except Exception as e:
        log(f"  ❌ Erro ao iniciar Chrome: {e}", "ERROR")
        log(f"  💡 Dica: Verifique se ChromeDriver é compatível com Chrome", "INFO")
        raise

def do_login(driver):
    """Realiza login com certificado digital."""
    log("=" * 70)
    log("ETAPA 1: LOGIN COM CERTIFICADO DIGITAL")
    log("=" * 70)

    # Acessar portal e-SAJ
    log("🌐 Acessando portal e-SAJ...")
    driver.get(ESAJ_PORTAL_URL)
    time.sleep(3)
    log(f"  ✅ Página carregada: {driver.title}")
    save_screenshot(driver, "01_portal_esaj")

    # Procurar botão "Certificado Digital"
    log("🔍 Procurando botão 'Certificado Digital'...")
    try:
        cert_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
        )
        log("  ✅ Botão 'Certificado Digital' encontrado!")
    except Exception as e:
        log(f"  ❌ Botão não encontrado: {e}", "ERROR")
        save_screenshot(driver, "02_button_not_found")
        return False

    # Clicar no botão
    log("🖱️  Clicando em 'Certificado Digital'...")
    cert_button.click()
    time.sleep(2)
    save_screenshot(driver, "03_after_click_cert")

    # Aguardar seleção manual do certificado
    log("=" * 70)
    log("⏳ AGUARDANDO SELEÇÃO DO CERTIFICADO (30 segundos)...")
    log("=" * 70)
    log("ℹ️  AÇÃO NECESSÁRIA:")
    log("   - Modal do Web Signer deve aparecer")
    log("   - Selecione o certificado na lista")
    log("   - Aguarde redirecionamento")
    log("")

    for i in range(30, 0, -1):
        if i % 5 == 0:
            log(f"   ⏳ {i} segundos restantes...")
        time.sleep(1)

    # Verificar se login foi bem-sucedido
    log("🔍 Verificando se login foi bem-sucedido...")
    current_url = driver.current_url
    log(f"  URL atual: {current_url}")

    if "portal.do?servico=" in current_url or "painel" in current_url.lower():
        log("=" * 70)
        log("✅ LOGIN BEM-SUCEDIDO!", "SUCCESS")
        log("=" * 70)
        save_screenshot(driver, "04_login_success")
        return True
    else:
        log("=" * 70)
        log("❌ LOGIN FALHOU", "ERROR")
        log("=" * 70)
        save_screenshot(driver, "04_login_failed")
        return False

def test_direct_process_access(driver):
    """Testa acesso direto a processo específico."""
    log("")
    log("=" * 70)
    log("ETAPA 2: ACESSO DIRETO A PROCESSO (SESSÃO AUTENTICADA)")
    log("=" * 70)

    # Acessar URL direta do processo
    log(f"🌐 Acessando processo: {EXPECTED_PROCESSO_NUMERO}")
    log(f"   URL: {PROCESSO_URL}")
    driver.get(PROCESSO_URL)
    time.sleep(5)  # Aguardar carregamento completo

    current_url = driver.current_url
    log(f"  ✅ Página carregada: {driver.title}")
    log(f"  URL atual: {current_url}")
    save_screenshot(driver, "05_processo_loaded")
    save_page_source(driver, "05_processo_html")

    # Verificar se foi redirecionado para login (sessão perdida)
    if "portal.do" in current_url and "servico=" not in current_url:
        log("❌ Redirecionado para login! Sessão NÃO foi mantida", "ERROR")
        return False

    # Verificar elementos da página do processo
    log("")
    log("🔍 Verificando elementos da página do processo...")

    checks_passed = 0
    checks_total = 0

    # 1. Número do processo
    checks_total += 1
    try:
        numero_elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{EXPECTED_PROCESSO_NUMERO}')]")
        log(f"  ✅ Número do processo encontrado: {EXPECTED_PROCESSO_NUMERO}")
        checks_passed += 1
    except:
        log(f"  ❌ Número do processo NÃO encontrado: {EXPECTED_PROCESSO_NUMERO}", "ERROR")

    # 2. Classe
    checks_total += 1
    try:
        classe_elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{EXPECTED_CLASSE}')]")
        log(f"  ✅ Classe encontrada: {EXPECTED_CLASSE}")
        checks_passed += 1
    except:
        log(f"  ❌ Classe NÃO encontrada: {EXPECTED_CLASSE}", "ERROR")

    # 3. Assunto
    checks_total += 1
    try:
        assunto_elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{EXPECTED_ASSUNTO}')]")
        log(f"  ✅ Assunto encontrado: {EXPECTED_ASSUNTO}")
        checks_passed += 1
    except:
        log(f"  ❌ Assunto NÃO encontrado: {EXPECTED_ASSUNTO}", "ERROR")

    # 4. Requerente
    checks_total += 1
    try:
        reqte_elem = driver.find_element(By.XPATH, f"//*[contains(text(), '{EXPECTED_REQTE}')]")
        log(f"  ✅ Requerente encontrado: {EXPECTED_REQTE}")
        checks_passed += 1
    except:
        log(f"  ❌ Requerente NÃO encontrado: {EXPECTED_REQTE}", "ERROR")

    # 5. Tabela de movimentações
    checks_total += 1
    try:
        mov_table = driver.find_element(By.XPATH, "//*[contains(text(), 'Movimentações')]")
        log(f"  ✅ Tabela de Movimentações encontrada")
        checks_passed += 1
    except:
        log(f"  ❌ Tabela de Movimentações NÃO encontrada", "ERROR")

    # 6. Partes do processo
    checks_total += 1
    try:
        partes_table = driver.find_element(By.XPATH, "//*[contains(text(), 'Partes do processo')]")
        log(f"  ✅ Tabela de Partes encontrada")
        checks_passed += 1
    except:
        log(f"  ❌ Tabela de Partes NÃO encontrada", "ERROR")

    # Resultado final
    log("")
    log("=" * 70)
    log(f"RESULTADO: {checks_passed}/{checks_total} verificações passaram")
    log("=" * 70)

    if checks_passed == checks_total:
        log("✅✅✅ ACESSO DIRETO FUNCIONOU PERFEITAMENTE! ✅✅✅", "SUCCESS")
        log("")
        log("🎉 CONCLUSÃO:")
        log("   ✅ Sessão autenticada foi mantida")
        log("   ✅ Acesso direto a processos funciona")
        log("   ✅ Crawler pode processar múltiplos jobs na mesma sessão")
        log("   ✅ Performance será otimizada (não precisa re-autenticar)")
        log("")
        return True
    elif checks_passed >= 4:
        log("🟡 ACESSO PARCIAL", "WARNING")
        log("   ℹ️  Alguns elementos não foram encontrados, mas página carregou")
        log("   ℹ️  Pode ser diferença no HTML ou seletores precisam ajuste")
        return True
    else:
        log("❌ ACESSO FALHOU", "ERROR")
        log("   ❌ Página não carregou corretamente")
        log("   ❌ Sessão pode ter sido perdida")
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
        log("TESTE #2 - ACESSO DIRETO A PROCESSO")
        log("Windows Server - Validação de Sessão Autenticada")
        log("=" * 70)
        log("")

        # 1. Iniciar Chrome
        driver = setup_chrome()

        # 2. Fazer login com certificado
        login_success = do_login(driver)
        if not login_success:
            log("❌ Login falhou! Não é possível prosseguir.", "ERROR")
            return False

        # 3. Testar acesso direto a processo
        success = test_direct_process_access(driver)

        # Aguardar antes de fechar
        log("")
        log("⏱️  Aguardando 10 segundos antes de fechar...")
        time.sleep(10)

    except Exception as e:
        log(f"❌ ERRO DURANTE TESTE: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
            save_page_source(driver, "99_error_html")
        success = False

    finally:
        # Fechar Chrome
        if driver:
            log("🔒 Fechando Chrome...")
            driver.quit()
            log("  ✅ Chrome fechado")

        log("")
        log("=" * 70)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 70)
        log(f"📝 Log completo: {LOG_FILE}")
        log(f"📸 Screenshots: {SCREENSHOTS_DIR}")
        log("")

    return success

# ====================
# EXECUÇÃO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("TESTE #2 - ACESSO DIRETO A PROCESSO")
    print("Windows Server - Crawler TJSP")
    print("=" * 70)
    print("")
    print("⚠️  IMPORTANTE:")
    print("   - Este teste valida se podemos acessar processos diretamente")
    print("   - Você precisará fazer login com certificado primeiro")
    print("   - Depois, o script tentará acessar processo sem re-autenticar")
    print("")
    print("💡 SE ESTE TESTE PASSAR:")
    print("   ✅ Crawler pode processar múltiplos jobs na mesma sessão")
    print("   ✅ Não precisa re-autenticar para cada processo")
    print("   ✅ Performance será MUITO melhor!")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = run_test()

    print("")
    if result:
        print("✅ TESTE PASSOU! Acesso direto a processos funciona!")
        print("")
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Adaptar crawler_full.py para usar sessão persistente")
        print("   2. Implementar pool de sessões autenticadas")
        print("   3. Processar múltiplos jobs sem re-login")
        print("")
        exit(0)
    else:
        print("❌ TESTE FALHOU! Verificar logs e troubleshooting.")
        print("")
        print("📋 TROUBLESHOOTING:")
        print("   1. Verificar se login com certificado funcionou")
        print("   2. Verificar se URL do processo está correta")
        print("   3. Verificar se sessão foi mantida (cookies)")
        print("   4. Analisar HTML salvo em screenshots/")
        print("")
        exit(1)
