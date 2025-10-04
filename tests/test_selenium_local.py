#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste SELENIUM LOCAL + WEBSOCKET
Usa ChromeDriver local (não remoto) para permitir carregamento de extensões
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def test_selenium_local():
    """Testa Selenium com ChromeDriver local"""
    
    print("=" * 80)
    print("TESTE SELENIUM LOCAL + WEBSOCKET")
    print("=" * 80)
    
    # Configurar Chrome
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    
    # CRÍTICO: Carregar extensão
    extension_path = "/opt/crawler_tjsp/chrome_extension"
    opts.add_argument(f"--load-extension={extension_path}")
    
    # Permitir WebSocket
    opts.add_argument("--allow-insecure-localhost")
    
    # Usar Xvfb display
    os.environ['DISPLAY'] = ':99'
    
    # Criar serviço do ChromeDriver
    service = Service('/usr/local/bin/chromedriver')
    
    print(f"\n[1] Iniciando ChromeDriver LOCAL")
    print(f"    Display: {os.environ.get('DISPLAY')}")
    print(f"    Extensão: {extension_path}")
    
    try:
        driver = webdriver.Chrome(service=service, options=opts)
        wait = WebDriverWait(driver, 20)
        
        print("    ✅ ChromeDriver iniciado")
        
        # Aguardar extensão carregar
        print("\n[2] Aguardando extensão carregar...")
        time.sleep(5)
        
        # Verificar WebSocket
        print("\n[3] Verificando window.WebSigner...")
        check_ws = driver.execute_script("""
            return {
                hasWebSigner: typeof window.WebSigner !== 'undefined',
                webSignerType: typeof window.WebSigner
            };
        """)
        print(f"    window.WebSigner existe: {check_ws.get('hasWebSigner')}")
        print(f"    Tipo: {check_ws.get('webSignerType')}")
        
        # Acessar e-SAJ
        print("\n[4] Acessando e-SAJ...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_01_inicial.png")
        print("    ✅ Screenshot: local_01_inicial.png")
        
        # Clicar em "Certificado digital"
        print("\n[5] Clicando em 'Certificado digital'...")
        aba_cert = wait.until(
            EC.element_to_be_clickable((By.ID, "linkAbaCertificado"))
        )
        aba_cert.click()
        print("    ✅ Clicou na aba")
        
        # Polling do dropdown
        print("    ⏳ Aguardando dropdown ser populado...")
        
        max_attempts = 20
        dropdown_populated = False
        
        for attempt in range(max_attempts):
            time.sleep(1)
            
            try:
                dropdown = driver.find_element(By.ID, "certificados")
                options = dropdown.find_elements(By.TAG_NAME, "option")
                
                valid_options = [opt for opt in options if opt.get_attribute("value") and opt.get_attribute("value") != ""]
                
                if valid_options:
                    print(f"    ✅ Dropdown populado após {attempt + 1} segundos!")
                    dropdown_populated = True
                    break
                else:
                    if attempt % 5 == 0:  # Mostrar a cada 5 segundos
                        print(f"    ⏳ Tentativa {attempt + 1}/{max_attempts}...")
            except:
                if attempt % 5 == 0:
                    print(f"    ⏳ Tentativa {attempt + 1}/{max_attempts}...")
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_02_aba_cert.png")
        print("    ✅ Screenshot: local_02_aba_cert.png")
        
        # Verificar dropdown
        print("\n[6] Verificando dropdown...")
        dropdown = driver.find_element(By.ID, "certificados")
        options = dropdown.find_elements(By.TAG_NAME, "option")
        
        print(f"    Opções encontradas: {len(options)}")
        for opt in options:
            text = opt.text
            value = opt.get_attribute("value")
            print(f"      - '{text}' (value: '{value}')")
        
        valid_certs = [opt for opt in options if opt.get_attribute("value") and opt.get_attribute("value") != ""]
        
        if valid_certs:
            print(f"\n    🎉 {len(valid_certs)} certificado(s) válido(s)!")
            
            # Selecionar certificado
            print("\n[7] Selecionando certificado...")
            valid_certs[0].click()
            time.sleep(2)
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_03_cert_selecionado.png")
            
            # Clicar em Entrar
            print("\n[8] Clicando em 'Entrar'...")
            btn_entrar = wait.until(
                EC.element_to_be_clickable((By.ID, "btnEntrar"))
            )
            btn_entrar.click()
            print("    ✅ Clicou em Entrar")
            
            # Aguardar popup
            print("\n[9] Aguardando popup de autorização...")
            time.sleep(5)
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_04_popup.png")
            print("    ✅ Screenshot: local_04_popup.png")
            
            # Tentar clicar em Authorize
            print("\n[10] Procurando botão 'Authorize'...")
            try:
                authorize_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Authorize') or contains(text(), 'Autorizar')]"))
                )
                authorize_btn.click()
                print("    ✅ Botão Authorize clicado")
                
                time.sleep(5)
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_05_apos_authorize.png")
                
                # Verificar login
                current_url = driver.current_url
                print(f"\n[11] URL atual: {current_url}")
                
                if "cpopg" in current_url or "consulta" in current_url.lower():
                    print("\n    🎉🎉🎉 LOGIN BEM-SUCEDIDO! 🎉🎉🎉")
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_06_logado.png")
                    return True
                else:
                    print(f"\n    ⚠️ URL inesperada: {current_url}")
                    return False
                    
            except Exception as e:
                print(f"    ⚠️ Erro ao processar popup: {e}")
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_05_erro_popup.png")
                return False
        else:
            print(f"\n    ❌ Certificado não apareceu")
            
            # Debug
            print("\n[7] Debug...")
            debug_info = driver.execute_script("""
                return {
                    hasWebSigner: typeof window.WebSigner !== 'undefined',
                    webSignerMethods: typeof window.WebSigner === 'object' ? Object.keys(window.WebSigner) : [],
                    extensionLoaded: document.querySelector('script[src*="chrome-extension"]') !== null
                };
            """)
            print(f"    window.WebSigner: {debug_info.get('hasWebSigner')}")
            print(f"    Métodos: {debug_info.get('webSignerMethods')}")
            print(f"    Extensão detectada: {debug_info.get('extensionLoaded')}")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/local_99_erro.png")
        except:
            pass
        return False
    
    finally:
        print("\n[12] Mantendo navegador aberto por 10 segundos...")
        time.sleep(10)
        try:
            driver.quit()
        except:
            pass
        print("✅ Teste concluído")

if __name__ == "__main__":
    print("\n⚠️ IMPORTANTE:")
    print("   1. Servidor WebSocket rodando (porta 8765)")
    print("   2. Xvfb rodando (display :99)")
    print("   3. ChromeDriver instalado em /usr/bin/chromedriver")
    print("\n")
    
    success = test_selenium_local()
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    
    if success:
        print("🎉 SUCESSO! Login realizado via Selenium LOCAL + WebSocket!")
    else:
        print("❌ Teste falhou")
        print("\n🔍 Verifique:")
        print("   - Screenshots em /opt/crawler_tjsp/screenshots/")
        print("   - Logs: sudo journalctl -u websocket-cert -n 50")
