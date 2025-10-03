#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação da Extensão Web Signer
Verifica se a extensão foi instalada corretamente
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def verify_extension():
    """Verifica se a extensão Web Signer está instalada"""
    
    print("=" * 80)
    print("VERIFICAÇÃO DA EXTENSÃO WEB SIGNER")
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
        
        # MÉTODO 1: Verificar via chrome://extensions/
        print("\n[2] Abrindo página de extensões...")
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        # Screenshot da página de extensões
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/verify_extensions_page.png")
        print("✅ Screenshot: Página de extensões")
        
        # Tentar encontrar a extensão Web Signer
        print("\n[3] Procurando extensão 'Web Signer'...")
        
        # Executar JavaScript para buscar a extensão
        extensions_info = driver.execute_script("""
            const items = document.querySelectorAll('extensions-item');
            const extensions = [];
            items.forEach(item => {
                const name = item.querySelector('#name')?.textContent || '';
                const id = item.id || '';
                extensions.push({name: name, id: id});
            });
            return extensions;
        """)
        
        print(f"\n[4] Extensões encontradas: {len(extensions_info)}")
        for ext in extensions_info:
            print(f"   - {ext['name']} (ID: {ext['id']})")
            if 'web signer' in ext['name'].lower():
                print(f"\n✅ EXTENSÃO WEB SIGNER ENCONTRADA!")
                print(f"   Nome: {ext['name']}")
                print(f"   ID: {ext['id']}")
        
        # MÉTODO 2: Testar na página de login
        print("\n[5] Testando na página de login do e-SAJ...")
        url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check"
        driver.get(url)
        time.sleep(3)
        
        # Clicar na aba certificado
        print("\n[6] Clicando na aba 'Certificado digital'...")
        aba_cert = wait.until(EC.element_to_be_clickable((By.ID, "linkAbaCertificado")))
        aba_cert.click()
        time.sleep(5)  # Aguardar mais tempo para carregar certificados
        
        # Screenshot da aba certificado
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/verify_cert_tab.png")
        print("✅ Screenshot: Aba certificado")
        
        # Verificar dropdown de certificados
        print("\n[7] Verificando dropdown de certificados...")
        
        try:
            dropdown = driver.find_element(By.ID, "certificados")
            options = dropdown.find_elements(By.TAG_NAME, "option")
            
            print(f"\n[8] Opções no dropdown: {len(options)}")
            for i, opt in enumerate(options):
                text = opt.text.strip()
                value = opt.get_attribute("value") or ""
                print(f"   [{i}] Texto: '{text}' | Valor: '{value}'")
            
            # Verificar se tem certificados válidos
            valid_certs = [opt for opt in options if opt.get_attribute("value") and "carregando" not in opt.text.lower()]
            
            if valid_certs:
                print(f"\n✅ CERTIFICADOS ENCONTRADOS: {len(valid_certs)}")
                for cert in valid_certs:
                    print(f"   - {cert.text}")
            else:
                print("\n⚠️ Nenhum certificado válido encontrado")
                print("   Possíveis causas:")
                print("   1. Web Signer não está rodando")
                print("   2. Certificado não está importado no NSS database")
                print("   3. Extensão não está se comunicando com Web Signer")
        
        except Exception as e:
            print(f"⚠️ Erro ao verificar dropdown: {e}")
        
        # Verificar se há popup de erro
        print("\n[9] Verificando se há popup de instalação...")
        try:
            popup = driver.find_element(By.XPATH, "//button[contains(text(), 'Instalar')]")
            print("⚠️ POPUP DE INSTALAÇÃO AINDA APARECE!")
            print("   Isso significa que a extensão NÃO está funcionando corretamente")
            
            # Screenshot do popup
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/verify_popup_erro.png")
            print("✅ Screenshot: Popup de erro")
        except:
            print("✅ Nenhum popup de instalação encontrado")
        
        print("\n" + "=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print("\nScreenshots salvos em: /opt/crawler_tjsp/screenshots/verify_*.png")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n[10] Mantendo navegador aberto por 30 segundos para análise...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    verify_extension()
