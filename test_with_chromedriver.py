#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste usando ChromeDriver (porta 4444) com perfil do crawler
NÃO precisa fechar o Chrome que está aberto no RDP
"""

import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def test_with_chromedriver():
    """Testa usando ChromeDriver com perfil do crawler"""
    
    print("=" * 80)
    print("TESTE COM CHROMEDRIVER + PERFIL DO CRAWLER")
    print("=" * 80)
    
    print("\n⚠️ IMPORTANTE:")
    print("   - NÃO vai fechar o Chrome do RDP")
    print("   - Usa o MESMO perfil que está logado")
    print("   - Pode dar conflito se o perfil estiver em uso")
    
    # PASSO 1: Verificar se há Chrome usando o perfil
    print("\n[1] Verificando se Chrome está usando o perfil...")
    result = subprocess.run(
        ["ps", "aux"], 
        capture_output=True, 
        text=True
    )
    
    chrome_processes = [line for line in result.stdout.split('\n') if 'google-chrome' in line and '/home/crawler/.config/google-chrome' in line]
    
    if chrome_processes:
        print(f"⚠️ Encontrado {len(chrome_processes)} processo(s) Chrome usando o perfil")
        print("   Isso pode causar conflito...")
        print("\n   OPÇÕES:")
        print("   A) Continuar mesmo assim (pode dar erro)")
        print("   B) Usar um perfil TEMPORÁRIO (não terá login do Google)")
        print("   C) Fechar Chrome do RDP e reabrir com debugging")
        
        # Vamos tentar usar um perfil temporário para não interferir
        print("\n   Escolhendo OPÇÃO B: Perfil temporário")
        profile_dir = "/tmp/chrome_profile_test"
        print(f"   Usando perfil temporário: {profile_dir}")
    else:
        print("✅ Nenhum Chrome usando o perfil")
        profile_dir = "/home/crawler/.config/google-chrome"
        print(f"   Usando perfil do crawler: {profile_dir}")
    
    # PASSO 2: Configurar Selenium
    print("\n[2] Configurando Selenium...")
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    chromedriver_url = "http://localhost:4444"
    print(f"   ChromeDriver: {chromedriver_url}")
    print(f"   Perfil: {profile_dir}")
    
    try:
        driver = Remote(
            command_executor=chromedriver_url,
            options=opts
        )
        print("✅ Conectado ao ChromeDriver!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    try:
        wait = WebDriverWait(driver, 20)
        
        # PASSO 3: Acessar e-SAJ
        print("\n[3] Acessando e-SAJ...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/01_esaj_home.png")
        print("✅ Screenshot 01: e-SAJ home")
        
        # PASSO 4: Clicar na aba Certificado Digital
        print("\n[4] Clicando na aba 'Certificado digital'...")
        try:
            aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
            aba_cert.click()
            print("✅ Clicou na aba certificado")
            time.sleep(5)  # Aguardar mais tempo para Web Signer carregar
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_aba_certificado.png")
            print("✅ Screenshot 02: Aba certificado")
        except Exception as e:
            print(f"⚠️ Erro ao clicar na aba: {e}")
        
        # PASSO 5: Verificar dropdown de certificados
        print("\n[5] Verificando dropdown de certificados...")
        try:
            dropdown = driver.find_element(By.ID, "certificados")
            options = dropdown.find_elements(By.TAG_NAME, "option")
            
            print(f"   Opções encontradas: {len(options)}")
            for i, opt in enumerate(options):
                text = opt.text.strip()
                value = opt.get_attribute("value") or ""
                print(f"   [{i}] '{text}' (value: '{value}')")
            
            # Verificar se tem certificado válido
            valid_certs = [opt for opt in options if opt.get_attribute("value") and "carregando" not in opt.text.lower()]
            
            if valid_certs:
                print(f"\n✅ CERTIFICADOS ENCONTRADOS: {len(valid_certs)}")
                print("\n🎉 🎉 🎉 SUCESSO! 🎉 🎉 🎉")
                print("   Web Signer está funcionando!")
                print("   Certificado detectado pelo Selenium!")
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_certificado_encontrado.png")
                print("✅ Screenshot 03: Certificado encontrado")
                
                return True
            else:
                print("\n❌ NENHUM CERTIFICADO VÁLIDO ENCONTRADO")
                print("   Dropdown está vazio ou só tem 'Carregando...'")
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_sem_certificados.png")
                print("✅ Screenshot 03: Sem certificados")
                
                return False
        
        except Exception as e:
            print(f"⚠️ Erro ao verificar dropdown: {e}")
            
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_erro_dropdown.png")
            print("✅ Screenshot 03: Erro no dropdown")
            
            return False
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[6] Mantendo navegador aberto por 30 segundos...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    success = test_with_chromedriver()
    
    print("\n" + "=" * 80)
    print("RESULTADO DO TESTE")
    print("=" * 80)
    
    if success:
        print("✅ TESTE BEM-SUCEDIDO!")
        print("   Web Signer funciona com Selenium!")
        print("   Certificado foi detectado!")
    else:
        print("❌ TESTE FALHOU")
        print("   Verifique os screenshots")
    
    print("\nScreenshots: /opt/crawler_tjsp/screenshots/")
