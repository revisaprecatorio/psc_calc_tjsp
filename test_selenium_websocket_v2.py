#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste SELENIUM + WEBSOCKET v2
Usa perfil persistente para manter extensão configurada
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
import time

def test_selenium_with_persistent_profile():
    """Testa Selenium com perfil persistente"""
    
    print("=" * 80)
    print("TESTE SELENIUM + WEBSOCKET v2 (Perfil Persistente)")
    print("=" * 80)
    
    # Configurar Chrome com perfil persistente
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    
    # Usar perfil persistente (onde extensão já está instalada)
    profile_dir = "/tmp/selenium_websocket_profile"
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    # Carregar extensão
    opts.add_argument("--load-extension=/opt/crawler_tjsp/chrome_extension")
    
    # Permitir WebSocket em contexto inseguro (localhost)
    opts.add_argument("--allow-insecure-localhost")
    opts.add_argument("--unsafely-treat-insecure-origin-as-secure=ws://localhost:8765")
    
    # Conectar ao ChromeDriver
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    print(f"    Perfil: {profile_dir}")
    print(f"    Extensão: /opt/crawler_tjsp/chrome_extension")
    
    driver = Remote(command_executor=chromedriver_url, options=opts)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Aguardar extensão carregar
        print("\n[2] Aguardando extensão carregar...")
        time.sleep(5)
        
        # Verificar se WebSocket está conectado via JavaScript
        print("\n[3] Verificando conexão WebSocket...")
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
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/v2_01_pagina_inicial.png")
        print("    ✅ Screenshot: v2_01_pagina_inicial.png")
        
        # Clicar em "Certificado digital"
        print("\n[5] Clicando em 'Certificado digital'...")
        aba_cert = wait.until(
            EC.element_to_be_clickable((By.ID, "linkAbaCertificado"))
        )
        aba_cert.click()
        print("    ✅ Clicou na aba")
        
        # Aguardar mais tempo para WebSocket
        print("    ⏳ Aguardando 10 segundos para WebSocket...")
        time.sleep(10)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/v2_02_aba_certificado.png")
        print("    ✅ Screenshot: v2_02_aba_certificado.png")
        
        # Verificar dropdown
        print("\n[6] Verificando dropdown de certificados...")
        dropdown = wait.until(
            EC.presence_of_element_located((By.ID, "certificados"))
        )
        
        options = dropdown.find_elements(By.TAG_NAME, "option")
        print(f"    Opções encontradas: {len(options)}")
        
        for opt in options:
            text = opt.text
            value = opt.get_attribute("value")
            print(f"      - '{text}' (value: '{value}')")
        
        # Verificar console do browser
        print("\n[7] Verificando console do browser...")
        try:
            logs = driver.get_log('browser')
            websocket_logs = [log for log in logs if 'websocket' in log['message'].lower() or 'web signer' in log['message'].lower()]
            
            if websocket_logs:
                print("    Logs WebSocket encontrados:")
                for log in websocket_logs[:10]:
                    print(f"      [{log['level']}] {log['message'][:150]}")
            else:
                print("    ⚠️ Nenhum log WebSocket encontrado")
        except Exception as e:
            print(f"    ⚠️ Não foi possível obter logs: {e}")
        
        # Verificar se certificado apareceu
        valid_certs = [opt for opt in options if opt.get_attribute("value") and opt.get_attribute("value") != ""]
        
        if valid_certs:
            print(f"\n    ✅ {len(valid_certs)} certificado(s) válido(s)!")
            return True
        else:
            print(f"\n    ❌ Certificado não apareceu")
            
            # Debug: Verificar se window.WebSigner está disponível
            print("\n[8] Debug: Verificando window.WebSigner...")
            debug_info = driver.execute_script("""
                return {
                    hasWebSigner: typeof window.WebSigner !== 'undefined',
                    webSignerMethods: typeof window.WebSigner === 'object' ? Object.keys(window.WebSigner) : [],
                    extensionLoaded: document.querySelector('script[src*="chrome-extension"]') !== null
                };
            """)
            print(f"    window.WebSigner existe: {debug_info.get('hasWebSigner')}")
            print(f"    Métodos: {debug_info.get('webSignerMethods')}")
            print(f"    Extensão detectada: {debug_info.get('extensionLoaded')}")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/v2_99_erro.png")
        return False
    
    finally:
        print("\n[9] Mantendo navegador aberto por 10 segundos...")
        time.sleep(10)
        driver.quit()
        print("✅ Teste concluído")

if __name__ == "__main__":
    success = test_selenium_with_persistent_profile()
    
    print("\n" + "=" * 80)
    print("RESULTADO")
    print("=" * 80)
    
    if success:
        print("🎉 SUCESSO! Certificado detectado via Selenium!")
    else:
        print("❌ FALHOU! Certificado não apareceu")
        print("\n📋 Possíveis causas:")
        print("   1. Extensão não carrega em modo automatizado")
        print("   2. WebSocket bloqueado pelo ChromeDriver")
        print("   3. Content Security Policy bloqueando conexão")
        print("\n🔍 Verifique:")
        print("   - Screenshots em /opt/crawler_tjsp/screenshots/")
        print("   - Logs do servidor: sudo journalctl -u websocket-cert -n 50")
