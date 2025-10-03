#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Instalar Extensão Web Signer Permanentemente
Instala a extensão no perfil do Chrome para que fique disponível sempre
"""

import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def install_extension_permanent():
    """Instala a extensão Web Signer permanentemente"""
    
    print("=" * 80)
    print("INSTALAÇÃO PERMANENTE DA EXTENSÃO WEB SIGNER")
    print("=" * 80)
    
    # ID da extensão Web Signer na Chrome Web Store
    extension_id = "bbafmabaelnnkondpfpjmdklbmfnbmol"
    extension_url = f"https://chrome.google.com/webstore/detail/web-signer/{extension_id}"
    
    print(f"\n[1] Extensão Web Signer")
    print(f"   ID: {extension_id}")
    print(f"   URL: {extension_url}")
    
    # Criar diretório de perfil permanente
    profile_dir = "/opt/crawler_tjsp/chrome_profile"
    os.makedirs(profile_dir, exist_ok=True)
    print(f"\n[2] Diretório de perfil: {profile_dir}")
    
    # Configurar Chrome com perfil permanente
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    
    # IMPORTANTE: Adicionar a extensão via linha de comando
    # Método 1: Forçar instalação da extensão
    opts.add_extension("/opt/crawler_tjsp/websigner_extension.crx") if os.path.exists("/opt/crawler_tjsp/websigner_extension.crx") else None
    
    # Conectar ao ChromeDriver local
    chromedriver_url = "http://localhost:4444"
    print(f"\n[3] Conectando ao ChromeDriver: {chromedriver_url}")
    
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
        
        # PASSO 1: Ir direto para a Chrome Web Store
        print(f"\n[4] Abrindo Chrome Web Store...")
        driver.get(extension_url)
        time.sleep(5)
        
        # Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_perm_step1_webstore.png")
        print("✅ Screenshot: Chrome Web Store")
        
        # PASSO 2: Procurar botão "Usar no Chrome" ou "Adicionar ao Chrome"
        print("\n[5] Procurando botão de instalação...")
        
        button_selectors = [
            (By.XPATH, "//button[contains(., 'Usar no Chrome')]"),
            (By.XPATH, "//button[contains(., 'Adicionar ao Chrome')]"),
            (By.XPATH, "//div[@role='button' and contains(., 'Adicionar')]"),
            (By.CSS_SELECTOR, "div[role='button']"),
        ]
        
        install_button = None
        for by, selector in button_selectors:
            try:
                install_button = wait.until(EC.element_to_be_clickable((by, selector)))
                button_text = install_button.text
                print(f"✅ Botão encontrado: '{button_text}'")
                
                # Verificar se é o botão correto
                if any(word in button_text.lower() for word in ['adicionar', 'usar', 'add', 'install']):
                    break
                else:
                    install_button = None
            except:
                continue
        
        if not install_button:
            print("⚠️ Botão de instalação não encontrado")
            print("   A extensão pode já estar instalada ou a página mudou")
            
            # Verificar se já está instalada
            try:
                installed_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'Remover') or contains(text(), 'Remove')]")
                print("✅ EXTENSÃO JÁ ESTÁ INSTALADA!")
            except:
                print("❌ Não conseguiu determinar o status da extensão")
        else:
            # PASSO 3: Clicar no botão de instalação
            print(f"\n[6] Clicando em '{install_button.text}'...")
            install_button.click()
            time.sleep(3)
            
            # Screenshot
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_perm_step2_clicked.png")
            print("✅ Screenshot: Depois de clicar")
            
            # PASSO 4: Confirmar instalação (popup)
            print("\n[7] Procurando popup de confirmação...")
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
                
                # Screenshot
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_perm_step3_confirmed.png")
                print("✅ Screenshot: Confirmação")
                
            except Exception as e:
                print(f"⚠️ Popup de confirmação não encontrado: {e}")
        
        # PASSO 5: Verificar se foi instalada
        print("\n[8] Verificando instalação...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_perm_step4_extensions.png")
        print("✅ Screenshot: Página de extensões")
        
        # Executar JavaScript para verificar
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
        
        print(f"\n[9] Extensões instaladas: {len(extensions_info)}")
        websigner_found = False
        for ext in extensions_info:
            print(f"   - {ext['name']} (ID: {ext['id']}, Ativada: {ext['enabled']})")
            if 'web signer' in ext['name'].lower():
                websigner_found = True
                print(f"\n✅ ✅ ✅ EXTENSÃO WEB SIGNER INSTALADA COM SUCESSO! ✅ ✅ ✅")
                print(f"   Nome: {ext['name']}")
                print(f"   ID: {ext['id']}")
                print(f"   Ativada: {ext['enabled']}")
        
        if not websigner_found:
            print("\n❌ EXTENSÃO WEB SIGNER NÃO FOI INSTALADA")
            print("   Verifique os screenshots para diagnóstico")
        
        # PASSO 6: Testar na página de login
        print("\n[10] Testando na página de login...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        # Clicar na aba certificado
        aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
        aba_cert.click()
        time.sleep(5)
        
        # Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_perm_step5_login_test.png")
        print("✅ Screenshot: Teste de login")
        
        # Verificar se popup ainda aparece
        try:
            popup = driver.find_element(By.XPATH, "//button[contains(text(), 'Instalar')]")
            print("\n⚠️ POPUP DE INSTALAÇÃO AINDA APARECE")
            print("   Isso significa que a extensão não está funcionando corretamente")
        except:
            print("\n✅ POPUP DE INSTALAÇÃO NÃO APARECE!")
            print("   A extensão parece estar funcionando!")
        
        print("\n" + "=" * 80)
        print("INSTALAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print(f"\nPerfil do Chrome salvo em: {profile_dir}")
        print("Screenshots salvos em: /opt/crawler_tjsp/screenshots/install_perm_step*.png")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a instalação: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[11] Mantendo navegador aberto por 30 segundos...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    install_extension_permanent()
