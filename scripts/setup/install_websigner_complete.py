#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Completo de Instalação do Web Signer
Automatiza TODA a instalação: popup + extensão + configuração
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def install_websigner_complete():
    """Instalação completa do Web Signer"""
    
    print("=" * 80)
    print("INSTALAÇÃO COMPLETA DO WEB SIGNER")
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
        wait = WebDriverWait(driver, 15)
        
        # PASSO 1: Acessar página de login
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        print(f"\n[2] Acessando: {url}")
        driver.get(url)
        time.sleep(3)
        
        # PASSO 2: Clicar na aba "Certificado digital"
        print("\n[3] Clicando na aba 'Certificado digital'...")
        aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
        aba_cert.click()
        time.sleep(2)
        
        # PASSO 3: Clicar no botão "Instalar" do popup
        print("\n[4] Clicando no botão 'Instalar' do popup...")
        botao_instalar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Instalar')]")))
        botao_instalar.click()
        time.sleep(3)
        
        # Screenshot: Página de instalação
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_step1_pagina_instalacao.png")
        print("✅ Screenshot: Página de instalação")
        
        # PASSO 4: Aguardar página de instalação carregar
        print("\n[5] Aguardando página de instalação do Web Signer...")
        time.sleep(3)
        
        # PASSO 5: Procurar e clicar no botão "Adicionar Softplan Web Signer na Chrome Store"
        print("\n[6] Procurando botão 'Add to Chrome'...")
        
        # Possíveis seletores para o botão
        selectors = [
            (By.XPATH, "//button[contains(text(), 'Adicionar')]"),
            (By.XPATH, "//button[contains(text(), 'Add to Chrome')]"),
            (By.CSS_SELECTOR, "button[onclick*='chrome.google.com']"),
            (By.XPATH, "//a[contains(@href, 'chrome.google.com/webstore')]"),
        ]
        
        botao_chrome_store = None
        for by, selector in selectors:
            try:
                botao_chrome_store = wait.until(EC.element_to_be_clickable((by, selector)))
                print(f"✅ Botão encontrado com seletor: {selector}")
                break
            except:
                continue
        
        if not botao_chrome_store:
            print("⚠️ Botão 'Add to Chrome' não encontrado automaticamente")
            print("   Tentando abrir Chrome Web Store diretamente...")
            
            # Abrir Chrome Web Store diretamente
            extension_url = "https://chrome.google.com/webstore/detail/web-signer/bbafmabaelnnkondpfpjmdklbmfnbmol"
            driver.get(extension_url)
            time.sleep(3)
        else:
            # Clicar no botão encontrado
            print("\n[7] Clicando no botão para abrir Chrome Web Store...")
            
            # Guardar a janela atual
            main_window = driver.current_window_handle
            
            # Clicar no botão
            botao_chrome_store.click()
            time.sleep(3)
            
            # Verificar se abriu nova aba
            if len(driver.window_handles) > 1:
                print("✅ Nova aba aberta (Chrome Web Store)")
                driver.switch_to.window(driver.window_handles[-1])
            
        # Screenshot: Chrome Web Store
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_step2_chrome_store.png")
        print("✅ Screenshot: Chrome Web Store")
        
        # PASSO 6: Clicar em "Adicionar ao Chrome" na Web Store
        print("\n[8] Procurando botão 'Adicionar ao Chrome' na Web Store...")
        time.sleep(2)
        
        try:
            # Tentar encontrar o botão "Adicionar ao Chrome"
            add_button_selectors = [
                (By.XPATH, "//button[contains(., 'Usar no Chrome')]"),
                (By.XPATH, "//button[contains(., 'Adicionar ao Chrome')]"),
                (By.XPATH, "//div[@role='button' and contains(., 'Adicionar')]"),
            ]
            
            add_button = None
            for by, selector in add_button_selectors:
                try:
                    add_button = wait.until(EC.element_to_be_clickable((by, selector)))
                    print(f"✅ Botão 'Adicionar' encontrado: {selector}")
                    break
                except:
                    continue
            
            if add_button:
                print("\n[9] Clicando em 'Adicionar ao Chrome'...")
                add_button.click()
                time.sleep(2)
                
                # Screenshot: Depois de clicar
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_step3_depois_adicionar.png")
                print("✅ Screenshot: Depois de adicionar")
                
                # PASSO 7: Confirmar instalação (popup de confirmação)
                print("\n[10] Procurando botão de confirmação...")
                try:
                    confirm_selectors = [
                        (By.XPATH, "//button[contains(., 'Adicionar extensão')]"),
                        (By.XPATH, "//button[contains(., 'Add extension')]"),
                    ]
                    
                    for by, selector in confirm_selectors:
                        try:
                            confirm_button = wait.until(EC.element_to_be_clickable((by, selector)))
                            print(f"✅ Botão de confirmação encontrado: {selector}")
                            confirm_button.click()
                            print("✅ Extensão sendo instalada...")
                            time.sleep(5)
                            break
                        except:
                            continue
                    
                    # Screenshot: Instalação concluída
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_step4_instalacao_concluida.png")
                    print("✅ Screenshot: Instalação concluída")
                    
                except Exception as e:
                    print(f"⚠️ Não encontrou botão de confirmação: {e}")
            else:
                print("⚠️ Botão 'Adicionar ao Chrome' não encontrado")
                print("   A extensão pode já estar instalada!")
        
        except Exception as e:
            print(f"⚠️ Erro ao tentar adicionar extensão: {e}")
        
        # PASSO 8: Voltar para a página de login e testar
        print("\n[11] Voltando para página de login para testar...")
        driver.get(url)
        time.sleep(3)
        
        # Clicar na aba certificado novamente
        aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
        aba_cert.click()
        time.sleep(3)
        
        # Screenshot final
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/install_step5_teste_final.png")
        print("✅ Screenshot: Teste final")
        
        print("\n" + "=" * 80)
        print("INSTALAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print("\nScreenshots salvos em: /opt/crawler_tjsp/screenshots/install_step*.png")
        print("\nPróximos passos:")
        print("1. Copie os screenshots para /home/crawler/")
        print("2. Verifique se a extensão foi instalada")
        print("3. Teste o login com certificado")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a instalação: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[12] Mantendo navegador aberto por 30 segundos para análise...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    install_websigner_complete()
