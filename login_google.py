#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script FOCADO APENAS no Login do Google
Objetivo: Fazer login com revisaprecatorio@gmail.com
Screenshots numerados em sequência: 01, 02, 03, etc.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote
from selenium.webdriver.common.keys import Keys

def login_google():
    """Login no Google - Foco único"""
    
    print("=" * 80)
    print("LOGIN NO GOOGLE - FOCO ÚNICO")
    print("=" * 80)
    
    # Configurar Chrome com perfil permanente
    profile_dir = "/opt/crawler_tjsp/chrome_profile_revisa"
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    # Conectar ao ChromeDriver
    chromedriver_url = "http://localhost:4444"
    print(f"\n[PASSO 1] Conectando ao ChromeDriver: {chromedriver_url}")
    print(f"          Perfil: {profile_dir}")
    
    try:
        driver = Remote(
            command_executor=chromedriver_url,
            options=opts
        )
        print("✅ Conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    try:
        wait = WebDriverWait(driver, 20)
        
        # PASSO 1: Abrir Google
        print("\n" + "=" * 80)
        print("[PASSO 2] Abrindo Google.com...")
        print("=" * 80)
        
        driver.get("https://www.google.com")
        time.sleep(3)
        
        # Screenshot 01
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/01_google_home.png")
        print("✅ Screenshot 01: Google.com")
        
        # PASSO 2: Procurar botão de login
        print("\n" + "=" * 80)
        print("[PASSO 3] Procurando botão de login...")
        print("=" * 80)
        
        # Tentar múltiplos seletores para o botão de login
        login_selectors = [
            (By.XPATH, "//a[contains(text(), 'Fazer login')]"),
            (By.XPATH, "//a[contains(text(), 'Sign in')]"),
            (By.XPATH, "//a[contains(text(), 'Entrar')]"),
            (By.XPATH, "//a[contains(@href, 'accounts.google.com')]"),
            (By.CSS_SELECTOR, "a[data-action='sign in']"),
            (By.LINK_TEXT, "Fazer login"),
            (By.LINK_TEXT, "Sign in"),
        ]
        
        login_button = None
        for i, (by, selector) in enumerate(login_selectors):
            try:
                print(f"   Tentativa {i+1}: {selector}")
                login_button = driver.find_element(by, selector)
                print(f"   ✅ Botão encontrado: '{login_button.text}'")
                break
            except:
                print(f"   ❌ Não encontrado")
                continue
        
        if not login_button:
            print("\n⚠️ Botão de login não encontrado com seletores padrão")
            print("   Tentando método alternativo: ir direto para accounts.google.com")
            
            # Método alternativo: ir direto para página de login
            driver.get("https://accounts.google.com/signin")
            time.sleep(3)
            
            # Screenshot 02
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_direct_login_page.png")
            print("✅ Screenshot 02: Página de login direta")
        else:
            # Clicar no botão de login
            print(f"\n[PASSO 4] Clicando em '{login_button.text}'...")
            login_button.click()
            time.sleep(3)
            
            # Screenshot 02
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/02_after_click_login.png")
            print("✅ Screenshot 02: Depois de clicar em login")
        
        # PASSO 3: Digitar email
        print("\n" + "=" * 80)
        print("[PASSO 5] Digitando email...")
        print("=" * 80)
        
        try:
            # Procurar campo de email
            email_selectors = [
                (By.ID, "identifierId"),
                (By.NAME, "identifier"),
                (By.XPATH, "//input[@type='email']"),
                (By.CSS_SELECTOR, "input[type='email']"),
            ]
            
            email_field = None
            for by, selector in email_selectors:
                try:
                    email_field = wait.until(EC.presence_of_element_located((by, selector)))
                    print(f"✅ Campo de email encontrado: {selector}")
                    break
                except:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys("revisaprecatorio@gmail.com")
                print("✅ Email digitado: revisaprecatorio@gmail.com")
                time.sleep(1)
                
                # Screenshot 03
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_email_typed.png")
                print("✅ Screenshot 03: Email digitado")
                
                # Pressionar Enter ou clicar em "Próximo"
                try:
                    next_button = driver.find_element(By.ID, "identifierNext")
                    next_button.click()
                    print("✅ Clicou em 'Próximo'")
                except:
                    email_field.send_keys(Keys.RETURN)
                    print("✅ Pressionou Enter")
                
                time.sleep(3)
                
                # Screenshot 04
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/04_after_email.png")
                print("✅ Screenshot 04: Depois de enviar email")
            else:
                print("❌ Campo de email não encontrado")
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_email_field_not_found.png")
                print("✅ Screenshot 03: Campo de email não encontrado")
        
        except Exception as e:
            print(f"❌ Erro ao digitar email: {e}")
        
        # PASSO 4: Digitar senha
        print("\n" + "=" * 80)
        print("[PASSO 6] Digitando senha...")
        print("=" * 80)
        
        try:
            # Procurar campo de senha
            password_selectors = [
                (By.NAME, "password"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            
            password_field = None
            for by, selector in password_selectors:
                try:
                    password_field = wait.until(EC.presence_of_element_located((by, selector)))
                    print(f"✅ Campo de senha encontrado: {selector}")
                    break
                except:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys("R3v1s@2025")
                print("✅ Senha digitada")
                time.sleep(1)
                
                # Screenshot 05
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_password_typed.png")
                print("✅ Screenshot 05: Senha digitada")
                
                # Pressionar Enter ou clicar em "Próximo"
                try:
                    next_button = driver.find_element(By.ID, "passwordNext")
                    next_button.click()
                    print("✅ Clicou em 'Próximo'")
                except:
                    password_field.send_keys(Keys.RETURN)
                    print("✅ Pressionou Enter")
                
                time.sleep(5)
                
                # Screenshot 06
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/06_after_password.png")
                print("✅ Screenshot 06: Depois de enviar senha")
            else:
                print("❌ Campo de senha não encontrado")
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_password_field_not_found.png")
                print("✅ Screenshot 05: Campo de senha não encontrado")
        
        except Exception as e:
            print(f"❌ Erro ao digitar senha: {e}")
        
        # PASSO 5: Verificar se login foi bem-sucedido
        print("\n" + "=" * 80)
        print("[PASSO 7] Verificando login...")
        print("=" * 80)
        
        # Aguardar um pouco para processar
        time.sleep(3)
        
        # Verificar URL atual
        current_url = driver.current_url
        print(f"URL atual: {current_url}")
        
        # Screenshot 07
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/07_login_result.png")
        print("✅ Screenshot 07: Resultado do login")
        
        # Verificar se está logado
        if "myaccount.google.com" in current_url or "google.com" in current_url:
            # Tentar encontrar elementos que indicam login bem-sucedido
            try:
                # Procurar avatar ou nome do usuário
                avatar = driver.find_element(By.CSS_SELECTOR, "img[alt*='Google']")
                print("\n✅ ✅ ✅ LOGIN BEM-SUCEDIDO! ✅ ✅ ✅")
                print("   Avatar do usuário encontrado")
            except:
                print("\n⚠️ Login pode ter sido bem-sucedido, mas não encontrou avatar")
                print("   Verifique o screenshot 07")
        else:
            print("\n⚠️ URL não indica login bem-sucedido")
            print("   Verifique os screenshots para diagnóstico")
        
        # Screenshot final
        driver.get("https://www.google.com")
        time.sleep(2)
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/08_google_logged_in.png")
        print("✅ Screenshot 08: Google.com após login")
        
        print("\n" + "=" * 80)
        print("PROCESSO DE LOGIN CONCLUÍDO!")
        print("=" * 80)
        print("\nScreenshots salvos em ordem:")
        print("  01_google_home.png")
        print("  02_after_click_login.png (ou 02_direct_login_page.png)")
        print("  03_email_typed.png")
        print("  04_after_email.png")
        print("  05_password_typed.png")
        print("  06_after_password.png")
        print("  07_login_result.png")
        print("  08_google_logged_in.png")
        print("\nPróximos passos:")
        print("  1. Copie os screenshots para /home/crawler/")
        print("  2. Verifique se o login foi bem-sucedido")
        print("  3. Se sim, prosseguir com Developer Mode e instalação da extensão")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o login: {e}")
        import traceback
        traceback.print_exc()
        
        # Screenshot de erro
        try:
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/99_error.png")
            print("✅ Screenshot 99: Erro capturado")
        except:
            pass
        
        return False
    
    finally:
        print("\n[PASSO 8] Mantendo navegador aberto por 60 segundos para análise...")
        time.sleep(60)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    login_google()
