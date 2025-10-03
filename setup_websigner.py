#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Setup do Web Signer
Automatiza a instalação do Web Signer via Selenium
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def setup_websigner():
    """Configura o Web Signer via Selenium"""
    
    print("=" * 80)
    print("SETUP WEB SIGNER - Instalação Automatizada")
    print("=" * 80)
    
    # Configurar Chrome
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    
    # Conectar ao ChromeDriver local
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    
    try:
        driver = Remote(
            command_executor=chromedriver_url,
            options=opts
        )
        print("✅ Conectado ao ChromeDriver com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    try:
        # Acessar página de login
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        print(f"\n[2] Acessando: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Screenshot 1: Página inicial
        screenshot_path = "/app/screenshots/setup_step1_inicial.png"
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot salvo: {screenshot_path}")
        
        # Clicar na aba "Certificado digital"
        print("\n[3] Procurando aba 'Certificado digital'...")
        wait = WebDriverWait(driver, 10)
        
        try:
            aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
            aba_cert.click()
            print("✅ Clicou na aba 'Certificado digital'")
            time.sleep(2)
            
            # Screenshot 2: Aba certificado
            screenshot_path = "/app/screenshots/setup_step2_aba_certificado.png"
            driver.save_screenshot(screenshot_path)
            print(f"✅ Screenshot salvo: {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Não encontrou aba certificado: {e}")
        
        # Procurar popup do Web Signer
        print("\n[4] Procurando popup do Web Signer...")
        time.sleep(2)
        
        # Screenshot 3: Estado atual
        screenshot_path = "/app/screenshots/setup_step3_popup.png"
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot salvo: {screenshot_path}")
        
        # Tentar encontrar o botão "Instalar"
        print("\n[5] Procurando botão 'Instalar'...")
        
        # Possíveis seletores para o botão Instalar
        selectors = [
            (By.XPATH, "//button[contains(text(), 'Instalar')]"),
            (By.XPATH, "//button[text()='Instalar']"),
            (By.CSS_SELECTOR, "button.swal2-confirm"),
            (By.XPATH, "//button[@class='swal2-confirm swal2-styled']"),
        ]
        
        botao_encontrado = False
        for by, selector in selectors:
            try:
                botao = wait.until(EC.element_to_be_clickable((by, selector)))
                print(f"✅ Botão encontrado com seletor: {selector}")
                
                # Screenshot 4: Antes de clicar
                screenshot_path = "/app/screenshots/setup_step4_antes_clicar.png"
                driver.save_screenshot(screenshot_path)
                print(f"✅ Screenshot salvo: {screenshot_path}")
                
                # Clicar no botão
                print("\n[6] Clicando no botão 'Instalar'...")
                botao.click()
                botao_encontrado = True
                time.sleep(3)
                
                # Screenshot 5: Depois de clicar
                screenshot_path = "/app/screenshots/setup_step5_depois_clicar.png"
                driver.save_screenshot(screenshot_path)
                print(f"✅ Screenshot salvo: {screenshot_path}")
                
                break
            except Exception as e:
                continue
        
        if not botao_encontrado:
            print("⚠️ Botão 'Instalar' não encontrado. Veja os screenshots.")
        
        # Aguardar e tirar screenshot final
        print("\n[7] Aguardando 5 segundos...")
        time.sleep(5)
        
        screenshot_path = "/app/screenshots/setup_step6_final.png"
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot final salvo: {screenshot_path}")
        
        print("\n" + "=" * 80)
        print("SETUP CONCLUÍDO!")
        print("=" * 80)
        print("\nScreenshots salvos em: /app/screenshots/setup_step*.png")
        print("No host: /opt/crawler_tjsp/screenshots/setup_step*.png")
        print("\nPróximos passos:")
        print("1. Copie os screenshots para /home/crawler/")
        print("2. Abra via RDP e analise cada passo")
        print("3. Me informe o que apareceu em cada screenshot")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[8] Mantendo navegador aberto por 30 segundos para análise...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    setup_websigner()
