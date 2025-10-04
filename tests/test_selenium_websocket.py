#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste COMPLETO: Selenium + WebSocket + e-SAJ
Valida login no e-SAJ usando extensão WebSocket customizada
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
import time

def test_selenium_with_websocket():
    """Testa Selenium com extensão WebSocket"""
    
    print("=" * 80)
    print("TESTE SELENIUM + WEBSOCKET + e-SAJ")
    print("=" * 80)
    
    # Configurar Chrome com extensão
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    
    # CRÍTICO: Carregar extensão customizada
    opts.add_argument("--load-extension=/opt/crawler_tjsp/chrome_extension")
    
    # Conectar ao ChromeDriver
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    print(f"    Extensão: /opt/crawler_tjsp/chrome_extension")
    
    driver = Remote(command_executor=chromedriver_url, options=opts)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Acessar e-SAJ
        print("\n[2] Acessando e-SAJ...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        # Screenshot inicial
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/01_pagina_inicial.png")
        print("    ✅ Screenshot: 01_pagina_inicial.png")
        
        # Clicar em "Certificado digital"
        print("\n[3] Clicando em 'Certificado digital'...")
        try:
            aba_cert = wait.until(
                EC.element_to_be_clickable((By.ID, "linkAbaCertificado"))
            )
            aba_cert.click()
            print("    ✅ Clicou na aba")
            time.sleep(5)  # Aguardar WebSocket carregar certificados
        except Exception as e:
            print(f"    ❌ Erro ao clicar: {e}")
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_erro_aba.png")
            return False
        
        # Screenshot após clicar
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_aba_certificado.png")
        print("    ✅ Screenshot: 02_aba_certificado.png")
        
        # Verificar dropdown de certificados
        print("\n[4] Verificando dropdown de certificados...")
        try:
            dropdown = wait.until(
                EC.presence_of_element_located((By.ID, "certificados"))
            )
            
            options = dropdown.find_elements(By.TAG_NAME, "option")
            print(f"    Opções encontradas: {len(options)}")
            
            for opt in options:
                text = opt.text
                value = opt.get_attribute("value")
                print(f"      - {text} (value: {value})")
            
            # Verificar se há certificado válido
            valid_certs = [opt for opt in options if opt.get_attribute("value") and opt.get_attribute("value") != ""]
            
            if valid_certs:
                print(f"\n    ✅ {len(valid_certs)} certificado(s) válido(s) encontrado(s)!")
                
                # Selecionar primeiro certificado
                print("\n[5] Selecionando certificado...")
                valid_certs[0].click()
                time.sleep(2)
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_certificado_selecionado.png")
                print("    ✅ Screenshot: 03_certificado_selecionado.png")
                
                # Clicar em "Entrar"
                print("\n[6] Clicando em 'Entrar'...")
                try:
                    btn_entrar = wait.until(
                        EC.element_to_be_clickable((By.ID, "btnEntrar"))
                    )
                    btn_entrar.click()
                    print("    ✅ Clicou em Entrar")
                    time.sleep(5)  # Aguardar login
                    
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/04_apos_entrar.png")
                    print("    ✅ Screenshot: 04_apos_entrar.png")
                    
                    # Verificar se logou
                    print("\n[7] Verificando se login foi bem-sucedido...")
                    
                    # Verificar URL (deve mudar após login)
                    current_url = driver.current_url
                    print(f"    URL atual: {current_url}")
                    
                    # Verificar se está na página de consulta
                    if "cpopg" in current_url or "consulta" in current_url.lower():
                        print("\n    🎉 LOGIN BEM-SUCEDIDO!")
                        
                        driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_logado.png")
                        print("    ✅ Screenshot: 05_logado.png")
                        
                        return True
                    else:
                        print(f"\n    ⚠️ URL inesperada: {current_url}")
                        return False
                    
                except Exception as e:
                    print(f"    ❌ Erro ao clicar em Entrar: {e}")
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/04_erro_entrar.png")
                    return False
            else:
                print(f"\n    ❌ Nenhum certificado válido encontrado!")
                return False
                
        except Exception as e:
            print(f"    ❌ Erro ao verificar dropdown: {e}")
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_erro_dropdown.png")
            return False
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/99_erro_geral.png")
        return False
    
    finally:
        print("\n[8] Mantendo navegador aberto por 10 segundos...")
        time.sleep(10)
        driver.quit()
        print("✅ Teste concluído")

if __name__ == "__main__":
    print("\n⚠️ IMPORTANTE: Certifique-se de que:")
    print("   1. Servidor WebSocket está rodando (porta 8765)")
    print("   2. ChromeDriver está rodando (porta 4444)")
    print("   3. Extensão está em /opt/crawler_tjsp/chrome_extension")
    print("\n")
    
    success = test_selenium_with_websocket()
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    
    if success:
        print("🎉 SUCESSO TOTAL! Login no e-SAJ via Selenium + WebSocket funcionando!")
        print("\n✅ Próximos passos:")
        print("   1. Integrar ao crawler principal")
        print("   2. Testar busca de processos")
        print("   3. Validar extração de dados")
    else:
        print("❌ Teste falhou. Verifique screenshots em /opt/crawler_tjsp/screenshots/")
        print("   E logs do servidor WebSocket")
