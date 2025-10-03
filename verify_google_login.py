#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Verificar Login no Google
Usa o perfil já logado manualmente via RDP
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def verify_google_login():
    """Verifica se o Google está logado no perfil"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DE LOGIN NO GOOGLE")
    print("=" * 80)
    
    # Usar o perfil do usuário crawler (que tem acesso via RDP)
    profile_dir = "/home/crawler/.config/google-chrome"
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    print(f"    Perfil: {profile_dir}")
    
    try:
        driver = Remote(
            command_executor=chromedriver_url,
            options=opts
        )
        print("✅ Conectado!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    try:
        wait = WebDriverWait(driver, 15)
        
        # Verificar Google
        print("\n[2] Abrindo Google.com...")
        driver.get("https://www.google.com")
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/01_verify_google.png")
        print("✅ Screenshot 01: Google.com")
        
        # Verificar se está logado
        print("\n[3] Verificando login...")
        
        try:
            # Procurar avatar/foto do usuário (indica que está logado)
            avatar = driver.find_element(By.CSS_SELECTOR, "a[aria-label*='Conta do Google']")
            print("✅ ✅ ✅ GOOGLE ESTÁ LOGADO! ✅ ✅ ✅")
            print("   Avatar do usuário encontrado")
            logged_in = True
        except:
            print("❌ Google NÃO está logado")
            print("   Avatar não encontrado")
            logged_in = False
        
        # Verificar My Account
        print("\n[4] Verificando Google Account...")
        driver.get("https://myaccount.google.com")
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_verify_myaccount.png")
        print("✅ Screenshot 02: My Account")
        
        # Verificar Extensions
        print("\n[5] Verificando chrome://extensions/...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_verify_extensions.png")
        print("✅ Screenshot 03: Extensions")
        
        # Verificar Developer Mode
        dev_mode = driver.execute_script("""
            const toggle = document.querySelector('extensions-manager')
                ?.shadowRoot?.querySelector('extensions-toolbar')
                ?.shadowRoot?.querySelector('#devMode');
            return toggle ? toggle.checked : false;
        """)
        
        if dev_mode:
            print("✅ Developer Mode ATIVADO")
        else:
            print("⚠️ Developer Mode NÃO ativado")
        
        # Verificar extensões instaladas
        extensions = driver.execute_script("""
            const items = document.querySelectorAll('extensions-item');
            const extensions = [];
            items.forEach(item => {
                const name = item.querySelector('#name')?.textContent || '';
                const id = item.id || '';
                extensions.push({name: name, id: id});
            });
            return extensions;
        """)
        
        print(f"\n[6] Extensões instaladas: {len(extensions)}")
        for ext in extensions:
            print(f"   - {ext['name']} (ID: {ext['id']})")
        
        # Resultado final
        print("\n" + "=" * 80)
        print("RESULTADO DA VERIFICAÇÃO")
        print("=" * 80)
        
        if logged_in:
            print("✅ Google: LOGADO")
        else:
            print("❌ Google: NÃO LOGADO - Execute login manual via RDP")
        
        if dev_mode:
            print("✅ Developer Mode: ATIVADO")
        else:
            print("⚠️ Developer Mode: NÃO ATIVADO - Ative manualmente")
        
        print(f"📊 Extensões: {len(extensions)} instalada(s)")
        
        print("\nScreenshots salvos:")
        print("  01_verify_google.png")
        print("  02_verify_myaccount.png")
        print("  03_verify_extensions.png")
        
        return logged_in
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[7] Mantendo navegador aberto por 30 segundos...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    verify_google_login()
