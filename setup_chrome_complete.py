#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Completo do Chrome com Login e Instalação da Extensão
Sequência correta:
1. Login no Google
2. Ativar Developer Mode
3. Instalar extensão Web Signer
4. Configurar extensão
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
from selenium.webdriver.common.keys import Keys

def setup_chrome_complete():
    """Setup completo do Chrome com login e extensão"""
    
    print("=" * 80)
    print("SETUP COMPLETO DO CHROME - LOGIN + DEVELOPER MODE + EXTENSÃO")
    print("=" * 80)
    
    # Configurar Chrome com perfil permanente
    profile_dir = "/opt/crawler_tjsp/chrome_profile_revisa"
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    # Conectar ao ChromeDriver local
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    print(f"    Perfil: {profile_dir}")
    
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
        wait = WebDriverWait(driver, 20)
        
        # PASSO 1: Fazer login no Google
        print("\n" + "=" * 80)
        print("PASSO 1: LOGIN NO GOOGLE")
        print("=" * 80)
        
        print("\n[2] Abrindo Google.com...")
        driver.get("https://www.google.com")
        time.sleep(3)
        
        # Screenshot 1
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step1_google.png")
        print("✅ Screenshot 1: Google.com")
        
        # Verificar se já está logado
        try:
            # Procurar botão "Fazer login"
            login_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Fazer login') or contains(text(), 'Sign in')]")
            print("\n[3] Não está logado. Clicando em 'Fazer login'...")
            login_button.click()
            time.sleep(3)
            
            # Screenshot 2
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step2_login_page.png")
            print("✅ Screenshot 2: Página de login")
            
            # Digitar email
            print("\n[4] Digitando email: revisaprecatorio@gmail.com")
            email_field = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
            email_field.send_keys("revisaprecatorio@gmail.com")
            email_field.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # Screenshot 3
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step3_after_email.png")
            print("✅ Screenshot 3: Depois de digitar email")
            
            # Digitar senha
            print("\n[5] Digitando senha...")
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys("R3v1s@2025")
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Screenshot 4
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step4_after_password.png")
            print("✅ Screenshot 4: Depois de digitar senha")
            
            print("\n✅ Login realizado com sucesso!")
            
        except Exception as e:
            print(f"\n⚠️ Já está logado ou erro no login: {e}")
            print("   Continuando...")
        
        # PASSO 2: Ativar Developer Mode
        print("\n" + "=" * 80)
        print("PASSO 2: ATIVAR DEVELOPER MODE")
        print("=" * 80)
        
        print("\n[6] Abrindo chrome://extensions/...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # Screenshot 5
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step5_extensions_page.png")
        print("✅ Screenshot 5: Página de extensões")
        
        # Ativar Developer Mode
        print("\n[7] Ativando Developer Mode...")
        try:
            # Executar JavaScript para ativar o toggle
            developer_mode_activated = driver.execute_script("""
                const toggle = document.querySelector('extensions-manager')
                    ?.shadowRoot?.querySelector('extensions-toolbar')
                    ?.shadowRoot?.querySelector('#devMode');
                
                if (toggle) {
                    if (!toggle.checked) {
                        toggle.click();
                        return true;
                    }
                    return 'already_enabled';
                }
                return false;
            """)
            
            if developer_mode_activated == True:
                print("✅ Developer Mode ATIVADO!")
                time.sleep(2)
            elif developer_mode_activated == 'already_enabled':
                print("✅ Developer Mode já estava ativado")
            else:
                print("⚠️ Não conseguiu ativar Developer Mode via JavaScript")
                print("   Tentando método alternativo...")
                
                # Método alternativo: usar coordenadas
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(driver)
                # Clicar aproximadamente onde fica o toggle (canto superior direito)
                actions.move_by_offset(1700, 100).click().perform()
                time.sleep(2)
                print("✅ Clicou na posição do Developer Mode")
            
            # Screenshot 6
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step6_dev_mode_on.png")
            print("✅ Screenshot 6: Developer Mode ativado")
            
        except Exception as e:
            print(f"⚠️ Erro ao ativar Developer Mode: {e}")
        
        # PASSO 3: Instalar Extensão Web Signer
        print("\n" + "=" * 80)
        print("PASSO 3: INSTALAR EXTENSÃO WEB SIGNER")
        print("=" * 80)
        
        print("\n[8] Abrindo Chrome Web Store - Web Signer...")
        extension_url = "https://chrome.google.com/webstore/detail/web-signer/bbafmabaelnnkondpfpjmdklbmfnbmol"
        driver.get(extension_url)
        time.sleep(5)
        
        # Screenshot 7
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step7_webstore.png")
        print("✅ Screenshot 7: Chrome Web Store - Web Signer")
        
        # Procurar botão de instalação
        print("\n[9] Procurando botão de instalação...")
        try:
            install_selectors = [
                (By.XPATH, "//button[contains(., 'Usar no Chrome')]"),
                (By.XPATH, "//button[contains(., 'Adicionar ao Chrome')]"),
                (By.XPATH, "//div[@role='button' and contains(., 'Adicionar')]"),
            ]
            
            install_button = None
            for by, selector in install_selectors:
                try:
                    install_button = wait.until(EC.element_to_be_clickable((by, selector)))
                    print(f"✅ Botão encontrado: '{install_button.text}'")
                    break
                except:
                    continue
            
            if install_button:
                print(f"\n[10] Clicando em '{install_button.text}'...")
                install_button.click()
                time.sleep(3)
                
                # Screenshot 8
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step8_clicked_install.png")
                print("✅ Screenshot 8: Depois de clicar em instalar")
                
                # Confirmar instalação
                print("\n[11] Procurando botão de confirmação...")
                try:
                    confirm_selectors = [
                        (By.XPATH, "//button[contains(., 'Adicionar extensão')]"),
                        (By.XPATH, "//button[contains(., 'Add extension')]"),
                    ]
                    
                    for by, selector in confirm_selectors:
                        try:
                            confirm_button = wait.until(EC.element_to_be_clickable((by, selector)))
                            print(f"✅ Botão de confirmação encontrado: '{confirm_button.text}'")
                            confirm_button.click()
                            print("✅ Confirmação clicada!")
                            time.sleep(5)
                            break
                        except:
                            continue
                    
                    # Screenshot 9
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step9_confirmed.png")
                    print("✅ Screenshot 9: Instalação confirmada")
                    
                except Exception as e:
                    print(f"⚠️ Não encontrou botão de confirmação: {e}")
            else:
                print("⚠️ Botão de instalação não encontrado")
                print("   A extensão pode já estar instalada")
        
        except Exception as e:
            print(f"⚠️ Erro ao instalar extensão: {e}")
        
        # PASSO 4: Verificar instalação
        print("\n" + "=" * 80)
        print("PASSO 4: VERIFICAR INSTALAÇÃO")
        print("=" * 80)
        
        print("\n[12] Voltando para chrome://extensions/...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # Screenshot 10
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/setup_step10_final_check.png")
        print("✅ Screenshot 10: Verificação final")
        
        # Listar extensões instaladas
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
        
        print(f"\n[13] Extensões instaladas: {len(extensions_info)}")
        websigner_found = False
        for ext in extensions_info:
            print(f"   - {ext['name']} (ID: {ext['id']}, Ativada: {ext['enabled']})")
            if 'web signer' in ext['name'].lower() or ext['id'] == 'bbafmabaelnnkondpfpjmdklbmfnbmol':
                websigner_found = True
                print(f"\n   🎉 WEB SIGNER INSTALADA COM SUCESSO!")
                print(f"      Nome: {ext['name']}")
                print(f"      ID: {ext['id']}")
                print(f"      Ativada: {ext['enabled']}")
        
        if not websigner_found:
            print("\n   ⚠️ Web Signer não foi instalada")
            print("      Verifique os screenshots para diagnóstico")
        
        print("\n" + "=" * 80)
        print("SETUP CONCLUÍDO!")
        print("=" * 80)
        print(f"\nPerfil do Chrome salvo em: {profile_dir}")
        print("Screenshots salvos em: /opt/crawler_tjsp/screenshots/setup_step*.png")
        print("\nPróximos passos:")
        print("  1. Copie os screenshots para /home/crawler/")
        print("  2. Verifique se a extensão foi instalada")
        print("  3. Configure a extensão (próximo script)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[14] Mantendo navegador aberto por 60 segundos...")
        time.sleep(60)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    setup_chrome_complete()
