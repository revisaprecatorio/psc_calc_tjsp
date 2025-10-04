#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script APENAS para Verificar e Configurar a Extensão
NÃO tenta fazer login - foca apenas na extensão
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
from selenium.webdriver.common.action_chains import ActionChains

def check_extension_only():
    """Verifica e prepara para configurar a extensão"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DA EXTENSÃO WEB SIGNER - SEM TENTAR LOGIN")
    print("=" * 80)
    
    # Configurar Chrome com perfil do root
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--user-data-dir=/root/.config/google-chrome")
    
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
        wait = WebDriverWait(driver, 15)
        
        # PASSO 1: Abrir página de extensões
        print("\n[2] Abrindo chrome://extensions/...")
        driver.get("chrome://extensions/")
        time.sleep(5)
        
        # Screenshot 1: Página de extensões
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/ext_check_step1_extensions_page.png")
        print("✅ Screenshot 1: Página de extensões")
        
        # PASSO 2: Verificar se a extensão aparece
        print("\n[3] Verificando se Web Signer aparece...")
        
        extensions_info = driver.execute_script("""
            const items = document.querySelectorAll('extensions-item');
            const extensions = [];
            items.forEach(item => {
                const name = item.querySelector('#name')?.textContent || '';
                const id = item.id || '';
                const enabled = item.querySelector('#enableToggle')?.checked || false;
                extensions.push({name: name, id: id, enabled: enabled});
            });
            return extensions;
        """)
        
        print(f"\n[4] Extensões encontradas: {len(extensions_info)}")
        websigner_found = False
        for ext in extensions_info:
            print(f"   - {ext['name']} (ID: {ext['id']}, Ativada: {ext['enabled']})")
            if 'web signer' in ext['name'].lower() or ext['id'] == 'bbafmabaelnnkondpfpjmdklbmfnbmol':
                websigner_found = True
                print(f"\n   ✅ WEB SIGNER ENCONTRADA!")
                print(f"      Nome: {ext['name']}")
                print(f"      ID: {ext['id']}")
                print(f"      Ativada: {ext['enabled']}")
        
        if not websigner_found:
            print("\n   ❌ Web Signer NÃO encontrada na lista de extensões")
        
        # PASSO 3: Abrir uma página qualquer para ver o ícone de extensões
        print("\n[5] Abrindo página em branco para acessar ícone de extensões...")
        driver.get("about:blank")
        time.sleep(2)
        
        # Screenshot 2: Página em branco (mostra barra de ferramentas)
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/ext_check_step2_blank_page.png")
        print("✅ Screenshot 2: Página em branco (barra de ferramentas visível)")
        
        # PASSO 4: Tentar clicar no ícone de extensões (puzzle piece)
        print("\n[6] Tentando clicar no ícone de extensões...")
        
        # Executar JavaScript para clicar no botão de extensões
        # O ícone de extensões geralmente está no topo direito
        try:
            # Tentar encontrar o botão de extensões via coordenadas
            # (geralmente fica no canto superior direito)
            actions = ActionChains(driver)
            
            # Clicar no canto superior direito onde fica o ícone de extensões
            # Coordenadas aproximadas: x=1850, y=50
            actions.move_by_offset(1850, 50).click().perform()
            time.sleep(2)
            
            # Screenshot 3: Depois de clicar
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/ext_check_step3_extensions_menu.png")
            print("✅ Screenshot 3: Menu de extensões (se abriu)")
            
        except Exception as e:
            print(f"⚠️ Não conseguiu clicar no ícone de extensões: {e}")
            print("   Isso é normal - vamos verificar via screenshot")
        
        # PASSO 5: Abrir página do Google para ter uma URL válida
        print("\n[7] Abrindo Google.com para ter uma página válida...")
        driver.get("https://www.google.com")
        time.sleep(3)
        
        # Screenshot 4: Google.com
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/ext_check_step4_google.png")
        print("✅ Screenshot 4: Google.com (para ver ícone de extensões)")
        
        print("\n" + "=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print("\nScreenshots salvos:")
        print("  1. ext_check_step1_extensions_page.png - Página chrome://extensions/")
        print("  2. ext_check_step2_blank_page.png - Página em branco")
        print("  3. ext_check_step3_extensions_menu.png - Menu de extensões")
        print("  4. ext_check_step4_google.png - Google.com")
        print("\nPróximos passos:")
        print("  1. Copie os screenshots para /home/crawler/")
        print("  2. Abra via RDP e analise cada screenshot")
        print("  3. Me informe:")
        print("     - A extensão Web Signer aparece em chrome://extensions/?")
        print("     - O ícone de extensões (puzzle) aparece na barra?")
        print("     - Consegue ver o ícone do Web Signer?")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[8] Mantendo navegador aberto por 60 segundos para análise...")
        print("    Você pode usar esse tempo para verificar manualmente via RDP")
        time.sleep(60)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    check_extension_only()
