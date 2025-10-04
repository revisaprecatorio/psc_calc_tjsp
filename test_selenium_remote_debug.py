#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste SELENIUM via REMOTE DEBUGGING
Conecta ao Chrome que já está rodando no RDP
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_remote_debugging():
    """Testa Selenium conectando ao Chrome do RDP via Remote Debugging"""
    
    print("=" * 80)
    print("TESTE SELENIUM via REMOTE DEBUGGING")
    print("=" * 80)
    
    # Configurar Chrome para conectar via remote debugging
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    print(f"\n[1] Conectando ao Chrome via Remote Debugging")
    print(f"    Endereço: 127.0.0.1:9222")
    print(f"    ⚠️ Chrome DEVE estar rodando com --remote-debugging-port=9222")
    
    try:
        driver = webdriver.Chrome(options=opts)
        wait = WebDriverWait(driver, 20)
        
        print("    ✅ Conectado ao Chrome!")
        
        # Verificar extensão
        print("\n[2] Verificando extensão Web Signer...")
        check_ext = driver.execute_script("""
            return {
                hasWebSigner: typeof window.WebSigner !== 'undefined',
                webSignerVersion: window.WebSigner ? window.WebSigner.version : null,
                extensions: chrome && chrome.runtime ? 'chrome.runtime disponível' : 'não disponível'
            };
        """)
        print(f"    window.WebSigner existe: {check_ext.get('hasWebSigner')}")
        print(f"    Versão: {check_ext.get('webSignerVersion')}")
        print(f"    Chrome runtime: {check_ext.get('extensions')}")
        
        # Acessar e-SAJ
        print("\n[3] Acessando e-SAJ...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_01_inicial.png")
        print("    ✅ Screenshot: rdebug_01_inicial.png")
        
        # Clicar em "Certificado digital"
        print("\n[4] Clicando em 'Certificado digital'...")
        try:
            aba_cert = wait.until(
                EC.element_to_be_clickable((By.ID, "linkAbaCertificado"))
            )
            aba_cert.click()
            print("    ✅ Clicou na aba")
            time.sleep(3)
        except Exception as e:
            print(f"    ⚠️ Erro ao clicar: {e}")
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_02_aba_cert.png")
        print("    ✅ Screenshot: rdebug_02_aba_cert.png")
        
        # Verificar dropdown
        print("\n[5] Verificando dropdown de certificados...")
        
        # Aguardar dropdown ser populado
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
                    if attempt % 5 == 0:
                        print(f"    ⏳ Tentativa {attempt + 1}/{max_attempts}...")
            except:
                if attempt % 5 == 0:
                    print(f"    ⏳ Tentativa {attempt + 1}/{max_attempts}...")
        
        # Verificar opções
        dropdown = driver.find_element(By.ID, "certificados")
        options = dropdown.find_elements(By.TAG_NAME, "option")
        
        print(f"\n[6] Opções encontradas: {len(options)}")
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
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_03_cert_selecionado.png")
            print("    ✅ Screenshot: rdebug_03_cert_selecionado.png")
            
            # Clicar em Entrar
            print("\n[8] Clicando em 'Entrar'...")
            btn_entrar = wait.until(
                EC.element_to_be_clickable((By.ID, "btnEntrar"))
            )
            btn_entrar.click()
            print("    ✅ Clicou em Entrar")
            
            # Aguardar popup de autorização
            print("\n[9] Aguardando popup de autorização...")
            time.sleep(5)
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_04_popup.png")
            print("    ✅ Screenshot: rdebug_04_popup.png")
            
            # Tentar clicar em Authorize
            print("\n[10] Procurando botão 'Authorize'...")
            try:
                # Tentar alert
                try:
                    alert = driver.switch_to.alert
                    print(f"    Alert detectado: {alert.text}")
                    alert.accept()
                    print("    ✅ Alert aceito")
                except:
                    pass
                
                # Tentar botão
                try:
                    authorize_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Authorize') or contains(text(), 'Autorizar')]"))
                    )
                    authorize_btn.click()
                    print("    ✅ Botão Authorize clicado")
                except:
                    print("    ⚠️ Botão Authorize não encontrado (pode ter sido automático)")
                
                time.sleep(5)
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_05_apos_authorize.png")
                print("    ✅ Screenshot: rdebug_05_apos_authorize.png")
                
                # Verificar login
                print("\n[11] Verificando login...")
                current_url = driver.current_url
                print(f"    URL atual: {current_url}")
                
                if "cpopg" in current_url or "consulta" in current_url.lower():
                    print("\n    🎉🎉🎉 LOGIN BEM-SUCEDIDO! 🎉🎉🎉")
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_06_logado.png")
                    print("    ✅ Screenshot: rdebug_06_logado.png")
                    return True
                else:
                    print(f"\n    ⚠️ URL inesperada: {current_url}")
                    return False
                    
            except Exception as e:
                print(f"    ⚠️ Erro ao processar popup: {e}")
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_05_erro_popup.png")
                return False
        else:
            print(f"\n    ❌ Certificado não apareceu")
            
            # Debug
            print("\n[7] Debug...")
            debug_info = driver.execute_script("""
                return {
                    hasWebSigner: typeof window.WebSigner !== 'undefined',
                    webSignerMethods: typeof window.WebSigner === 'object' ? Object.keys(window.WebSigner) : [],
                    extensionLoaded: document.querySelector('script[src*="chrome-extension"]') !== null,
                    allScripts: Array.from(document.scripts).map(s => s.src).filter(s => s.includes('chrome-extension'))
                };
            """)
            print(f"    window.WebSigner: {debug_info.get('hasWebSigner')}")
            print(f"    Métodos: {debug_info.get('webSignerMethods')}")
            print(f"    Extensão detectada: {debug_info.get('extensionLoaded')}")
            print(f"    Scripts de extensão: {debug_info.get('allScripts')}")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/rdebug_99_erro.png")
        except:
            pass
        return False
    
    finally:
        print("\n[12] Mantendo sessão aberta por 10 segundos...")
        print("    ⚠️ Chrome NÃO será fechado (remote debugging)")
        time.sleep(10)
        try:
            # Não fechar driver - apenas desconectar
            driver.quit()
        except:
            pass
        print("✅ Teste concluído (Chrome continua rodando)")

if __name__ == "__main__":
    print("\n⚠️ PRÉ-REQUISITOS:")
    print("   1. Chrome rodando com: bash start_chrome_debug.sh")
    print("   2. Servidor WebSocket rodando (porta 8765)")
    print("   3. Extensão Web Signer instalada no Chrome")
    print("   4. Chrome logado no Google (se necessário)")
    print("\n")
    
    success = test_remote_debugging()
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    
    if success:
        print("🎉 SUCESSO! Login realizado via Remote Debugging!")
        print("\n✅ Próximos passos:")
        print("   1. Integrar ao crawler principal")
        print("   2. Testar busca de processos")
        print("   3. Validar extração de dados")
    else:
        print("❌ Teste falhou")
        print("\n🔍 Verifique:")
        print("   - Chrome está rodando com remote debugging?")
        print("   - curl http://localhost:9222/json")
        print("   - Extensão Web Signer está instalada?")
        print("   - Screenshots em /opt/crawler_tjsp/screenshots/")
