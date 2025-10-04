#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste usando Chrome já aberto via Remote Debugging
Conecta ao Chrome que está rodando com --remote-debugging-port=9222
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_with_open_browser():
    """Testa usando Chrome já aberto"""
    
    print("=" * 80)
    print("TESTE COM CHROME JÁ ABERTO (Remote Debugging)")
    print("=" * 80)
    
    print("\n⚠️ IMPORTANTE:")
    print("   1. Chrome deve estar aberto com: --remote-debugging-port=9222")
    print("   2. Você deve estar LOGADO no e-SAJ")
    print("   3. Deixe o Chrome aberto durante o teste")
    
    # Configurar para conectar ao Chrome já aberto
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "localhost:9222")
    
    print("\n[1] Conectando ao Chrome aberto (porta 9222)...")
    
    try:
        driver = webdriver.Chrome(options=opts)
        print("✅ Conectado ao Chrome aberto!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("\n⚠️ Certifique-se de que o Chrome está aberto com:")
        print("   google-chrome --remote-debugging-port=9222 &")
        return False
    
    try:
        wait = WebDriverWait(driver, 15)
        
        # Verificar URL atual
        print(f"\n[2] URL atual: {driver.current_url}")
        
        # Screenshot 1
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/01_chrome_aberto.png")
        print("✅ Screenshot 01: Chrome aberto")
        
        # Se não estiver no e-SAJ, navegar
        if "esaj.tjsp.jus.br" not in driver.current_url:
            print("\n[3] Navegando para e-SAJ...")
            driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
            time.sleep(3)
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_navegou_esaj.png")
            print("✅ Screenshot 02: Navegou para e-SAJ")
        
        # Verificar se está logado
        print("\n[4] Verificando se está logado...")
        
        try:
            # Procurar elemento que indica login (ex: nome do usuário, menu, etc)
            # Ajuste conforme necessário
            page_source = driver.page_source
            
            if "sair" in page_source.lower() or "logout" in page_source.lower():
                print("✅ ESTÁ LOGADO!")
                print("   Encontrou indicador de sessão ativa")
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_logado.png")
                print("✅ Screenshot 03: Logado")
                
                # Testar busca de processo
                print("\n[5] Testando busca de processo...")
                
                try:
                    # Ir para página de consulta
                    driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
                    time.sleep(2)
                    
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/04_pagina_consulta.png")
                    print("✅ Screenshot 04: Página de consulta")
                    
                    # Tentar preencher número do processo
                    numero_processo = "1500001-02.2018.8.26.0577"
                    
                    # Procurar campo de número do processo
                    campo_selectors = [
                        (By.ID, "numeroDigitoAnoUnificado"),
                        (By.NAME, "numeroDigitoAnoUnificado"),
                        (By.CSS_SELECTOR, "input[name='numeroDigitoAnoUnificado']"),
                    ]
                    
                    campo = None
                    for by, selector in campo_selectors:
                        try:
                            campo = driver.find_element(by, selector)
                            print(f"✅ Campo encontrado: {selector}")
                            break
                        except:
                            continue
                    
                    if campo:
                        # Preencher número
                        campo.clear()
                        campo.send_keys("1500001-02.2018.8.26.0577")
                        print(f"✅ Número preenchido: {numero_processo}")
                        
                        driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_numero_preenchido.png")
                        print("✅ Screenshot 05: Número preenchido")
                        
                        # Clicar em consultar
                        btn_consultar = driver.find_element(By.ID, "pbConsultar")
                        btn_consultar.click()
                        print("✅ Clicou em Consultar")
                        
                        time.sleep(3)
                        
                        driver.save_screenshot("/opt/crawler_tjsp/screenshots/06_resultado_busca.png")
                        print("✅ Screenshot 06: Resultado da busca")
                        
                        print("\n🎉 🎉 🎉 TESTE BEM-SUCEDIDO! 🎉 🎉 🎉")
                        print("   Conseguiu buscar processo usando Chrome aberto!")
                        
                        return True
                    else:
                        print("⚠️ Campo de número não encontrado")
                
                except Exception as e:
                    print(f"⚠️ Erro ao testar busca: {e}")
            else:
                print("⚠️ NÃO está logado")
                print("   Faça login manualmente no Chrome aberto")
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_nao_logado.png")
                print("✅ Screenshot 03: Não logado")
        
        except Exception as e:
            print(f"⚠️ Erro ao verificar login: {e}")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[6] NÃO vou fechar o navegador (você está usando!)")
        print("    Apenas desconectando o Selenium...")
        driver.quit()
        print("✅ Selenium desconectado (Chrome continua aberto)")

if __name__ == "__main__":
    success = test_with_open_browser()
    
    print("\n" + "=" * 80)
    print("RESULTADO DO TESTE")
    print("=" * 80)
    
    if success:
        print("✅ TESTE BEM-SUCEDIDO!")
        print("   O crawler PODE usar Chrome aberto!")
        print("\n📋 Próximos passos:")
        print("   1. Sempre abrir Chrome com --remote-debugging-port=9222")
        print("   2. Fazer login manualmente quando necessário")
        print("   3. Crawler conecta ao Chrome aberto")
    else:
        print("❌ TESTE FALHOU")
        print("   Verifique os screenshots")
    
    print("\nScreenshots: /opt/crawler_tjsp/screenshots/")
