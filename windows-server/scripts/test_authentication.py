"""
Test de Autenticação - e-SAJ TJSP com Certificado Digital
=========================================================

Este script testa a autenticação no e-SAJ usando certificado digital A1
via Web Signer (Native Messaging Protocol).

IMPORTANTE: Este é o teste crítico que valida se a migração para Windows
resolveu o bloqueio do Native Messaging Protocol.

Uso:
    python test_authentication.py

Pré-requisitos:
    - Chrome instalado
    - ChromeDriver instalado e no PATH
    - Web Signer rodando
    - Certificado A1 importado no Windows Certificate Store
    - Extensão Web Signer carregada no Chrome
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
# NÃO USAR user-data-dir customizado! Deixar Chrome usar perfil padrão (onde Web Signer está instalado)
USER_DATA_DIR = None  # Alterado de r"C:\temp\chrome-profile-test"
EXTENSION_PATH = r"C:\projetos\crawler_tjsp\chrome_extension"
SCREENSHOTS_DIR = r"C:\projetos\crawler_tjsp\screenshots"
LOG_FILE = r"C:\projetos\crawler_tjsp\logs\test_auth.log"

ESAJ_URL = "https://esaj.tjsp.jus.br/esaj/portal.do"

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

def setup_chrome():
    """Configura e retorna instância do Chrome via Selenium."""
    log("🔧 Configurando Chrome...")

    # Opções do Chrome
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY

    # Configurações importantes
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # NÃO adicionar --user-data-dir! Deixar Chrome usar perfil padrão (revisa.precatorio@gmail.com)
    # Isso replica o comportamento do PowerShell Start-Process que abre o perfil correto
    # Se adicionarmos user-data-dir, Chrome cria perfil novo sem Web Signer
    if USER_DATA_DIR:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        log(f"  ⚠️ Usando perfil customizado: {USER_DATA_DIR}")
    else:
        log(f"  ✅ Usando perfil padrão do Chrome (onde Web Signer está instalado)")

    # Carregar extensão Web Signer (se existir localmente)
    if os.path.exists(EXTENSION_PATH):
        chrome_options.add_argument(f"--load-extension={EXTENSION_PATH}")
        log(f"  ✅ Extensão carregada: {EXTENSION_PATH}")
    else:
        log(f"  ⚠️ Extensão não encontrada em: {EXTENSION_PATH}", "WARNING")
        log(f"  ℹ️  A extensão pode estar instalada via Chrome Web Store", "INFO")

    # Preferências
    prefs = {
        "download.default_directory": r"C:\projetos\crawler_tjsp\downloads",
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Service (ChromeDriver)
    service = Service(executable_path=CHROMEDRIVER_PATH)

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log("  ✅ Chrome iniciado com sucesso!")
        return driver
    except Exception as e:
        log(f"  ❌ Erro ao iniciar Chrome: {e}", "ERROR")
        raise

# ====================
# TESTE PRINCIPAL
# ====================

def test_authentication():
    """
    Teste de autenticação com certificado digital.

    Retorna:
        True se login bem-sucedido, False caso contrário
    """
    driver = None
    success = False

    try:
        log("=" * 60)
        log("TESTE DE AUTENTICAÇÃO - e-SAJ TJSP")
        log("=" * 60)

        # 1. Iniciar Chrome
        driver = setup_chrome()

        # 2. Acessar e-SAJ
        log("🌐 Acessando e-SAJ...")
        driver.get(ESAJ_URL)
        time.sleep(3)

        log(f"  ✅ Página carregada: {driver.title}")
        save_screenshot(driver, "01_esaj_homepage")

        # 3. Verificar se página carregou
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            log("  ✅ Página e-SAJ carregada corretamente")
        except Exception as e:
            log(f"  ❌ Erro ao carregar página: {e}", "ERROR")
            return False

        # 4. Procurar botão "Certificado Digital"
        log("🔍 Procurando botão 'Certificado Digital'...")
        try:
            cert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Certificado Digital"))
            )
            log("  ✅ Botão 'Certificado Digital' encontrado!")
        except Exception as e:
            log(f"  ❌ Botão não encontrado: {e}", "ERROR")
            log("  ℹ️  Possíveis causas:", "INFO")
            log("     - Página mudou de layout", "INFO")
            log("     - Seletor precisa ser atualizado", "INFO")
            save_screenshot(driver, "02_button_not_found")
            return False

        # 5. Clicar no botão "Certificado Digital"
        log("🖱️  Clicando em 'Certificado Digital'...")
        cert_button.click()
        time.sleep(2)
        save_screenshot(driver, "03_after_click_cert")

        # 6. MOMENTO CRÍTICO: Web Signer deve abrir modal
        log("=" * 60)
        log("⏳ AGUARDANDO WEB SIGNER ABRIR MODAL DE SELEÇÃO...")
        log("=" * 60)
        log("ℹ️  Neste momento, o Native Messaging Protocol será testado:")
        log("   1. Extensão Chrome → envia mensagem → Web Signer")
        log("   2. Web Signer → abre modal nativo → usuário seleciona certificado")
        log("   3. Web Signer → retorna certificado → Extensão Chrome")
        log("   4. Login bem-sucedido no e-SAJ")
        log("")
        log("⚠️  AÇÃO NECESSÁRIA:")
        log("   - Modal do Web Signer deve aparecer automaticamente")
        log("   - Selecione o certificado na lista")
        log("   - Aguarde redirecionamento")
        log("")

        # Aguardar 30 segundos para seleção manual do certificado
        log("⏱️  Aguardando 30 segundos para seleção do certificado...")
        for i in range(30, 0, -1):
            if i % 5 == 0:
                log(f"   ⏳ {i} segundos restantes...")
            time.sleep(1)

        # 7. Verificar se login foi bem-sucedido
        log("🔍 Verificando se login foi bem-sucedido...")
        current_url = driver.current_url
        log(f"  URL atual: {current_url}")

        # Se URL mudou para portal autenticado
        if "portal.do?servico=" in current_url or "painel" in current_url.lower():
            log("=" * 60)
            log("✅✅✅ LOGIN COM CERTIFICADO BEM-SUCEDIDO! ✅✅✅", "SUCCESS")
            log("=" * 60)
            log(f"URL pós-login: {current_url}")
            save_screenshot(driver, "04_login_success")
            success = True

            # TESTE PASSOU! Native Messaging funcionou!
            log("")
            log("🎉 RESULTADO DO TESTE: SUCESSO! 🎉")
            log("✅ Native Messaging Protocol funcionou corretamente!")
            log("✅ Web Signer comunicou com extensão Chrome!")
            log("✅ Autenticação via certificado digital operacional!")
            log("")
            log("📋 Próximos passos:")
            log("   1. Configurar orchestrator_subprocess.py")
            log("   2. Criar Windows Service")
            log("   3. Testar crawler_full.py completo")
            log("   4. Iniciar processamento de jobs")
            log("")

        else:
            log("=" * 60)
            log("❌ LOGIN FALHOU OU AINDA NA TELA DE AUTENTICAÇÃO", "ERROR")
            log("=" * 60)
            log(f"URL esperada: https://esaj.tjsp.jus.br/esaj/portal.do?servico=...")
            log(f"URL obtida:   {current_url}")
            save_screenshot(driver, "04_login_failed")

            log("")
            log("❌ RESULTADO DO TESTE: FALHA")
            log("Possíveis causas:")
            log("   1. Modal do Web Signer não abriu (Native Messaging falhou)")
            log("   2. Certificado não foi selecionado")
            log("   3. Certificado expirado ou inválido")
            log("   4. Web Signer não está rodando")
            log("   5. Extensão não está carregada no Chrome")
            log("")
            log("🔧 Troubleshooting:")
            log("   - Verificar se Web Signer está rodando (bandeja do sistema)")
            log("   - Verificar extensão em chrome://extensions/")
            log("   - Verificar certificado em certmgr.msc")
            log("   - Tentar login manual para comparar comportamento")
            log("")

        # Aguardar antes de fechar
        log("⏱️  Aguardando 10 segundos antes de fechar...")
        time.sleep(10)

    except Exception as e:
        log(f"❌ ERRO DURANTE TESTE: {e}", "ERROR")
        if driver:
            save_screenshot(driver, "99_error")
        success = False

    finally:
        # Fechar Chrome
        if driver:
            log("🔒 Fechando Chrome...")
            driver.quit()
            log("  ✅ Chrome fechado")

        log("=" * 60)
        log(f"TESTE FINALIZADO: {'SUCESSO' if success else 'FALHA'}")
        log("=" * 60)
        log(f"📝 Log completo: {LOG_FILE}")
        log(f"📸 Screenshots: {SCREENSHOTS_DIR}")

    return success

# ====================
# EXECUÇÃO
# ====================

if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("TESTE DE AUTENTICAÇÃO - CRAWLER TJSP")
    print("Windows Server - Validação de Native Messaging")
    print("=" * 60)
    print("")
    print("⚠️  IMPORTANTE:")
    print("   - Certifique-se de que Web Signer está rodando")
    print("   - Certifique-se de que certificado está importado")
    print("   - Você precisará selecionar o certificado manualmente")
    print("")
    input("Pressione Enter para iniciar o teste...")
    print("")

    result = test_authentication()

    print("")
    if result:
        print("✅ TESTE PASSOU! Migração para Windows foi bem-sucedida!")
        exit(0)
    else:
        print("❌ TESTE FALHOU! Verificar logs e troubleshooting.")
        exit(1)
