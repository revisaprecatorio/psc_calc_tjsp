#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Login no e-SAJ usando perfil do crawler
Usa o perfil que já está configurado via RDP
"""

import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote

def test_esaj_login():
    """Testa login no e-SAJ com certificado"""
    
    print("=" * 80)
    print("TESTE DE LOGIN NO e-SAJ COM CERTIFICADO")
    print("=" * 80)
    
    # PASSO 1: Fechar qualquer Chrome aberto
    print("\n[1] Fechando qualquer Chrome aberto...")
    try:
        subprocess.run(["pkill", "-9", "chrome"], check=False)
        subprocess.run(["pkill", "-9", "google-chrome"], check=False)
        time.sleep(2)
        print("✅ Chrome fechado")
    except Exception as e:
        print(f"⚠️ Erro ao fechar Chrome: {e}")
    
    # PASSO 2: Configurar Selenium
    print("\n[2] Configurando Selenium...")
    
    # Usar perfil do crawler (que já está configurado via RDP)
    profile_dir = "/home/crawler/.config/google-chrome"
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    # Importante: usar o perfil Default
    opts.add_argument("--profile-directory=Default")
    
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
            time.sleep(3)
            
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
                
                # Selecionar o primeiro certificado
                cert = valid_certs[0]
                print(f"   Selecionando: {cert.text}")
                cert.click()
                time.sleep(2)
                
                driver.save_screenshot("/opt/crawler_tjsp/screenshots/03_certificado_selecionado.png")
                print("✅ Screenshot 03: Certificado selecionado")
                
                # PASSO 6: Clicar em Entrar
                print("\n[6] Clicando em 'Entrar'...")
                try:
                    btn_entrar = driver.find_element(By.ID, "pbEntrar")
                    btn_entrar.click()
                    print("✅ Clicou em Entrar")
                    time.sleep(5)
                    
                    driver.save_screenshot("/opt/crawler_tjsp/screenshots/04_depois_entrar.png")
                    print("✅ Screenshot 04: Depois de clicar em Entrar")
                    
                    # PASSO 7: Verificar se logou
                    print("\n[7] Verificando login...")
                    current_url = driver.current_url
                    print(f"   URL atual: {current_url}")
                    
                    if "cpopg" in current_url:
                        print("\n🎉 🎉 🎉 LOGIN BEM-SUCEDIDO! 🎉 🎉 🎉")
                        print("   Redirecionado para o sistema!")
                        
                        driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_logado_sucesso.png")
                        print("✅ Screenshot 05: Login bem-sucedido")
                        
                        return True
                    else:
                        print("\n⚠️ Login pode não ter funcionado")
                        print("   Verifique os screenshots")
                        
                        driver.save_screenshot("/opt/crawler_tjsp/screenshots/05_login_falhou.png")
                        print("✅ Screenshot 05: Possível falha no login")
                        
                        return False
                    
                except Exception as e:
                    print(f"⚠️ Erro ao clicar em Entrar: {e}")
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
        
        try:
            driver.save_screenshot("/opt/crawler_tjsp/screenshots/99_erro.png")
            print("✅ Screenshot 99: Erro")
        except:
            pass
        
        return False
    
    finally:
        print("\n[8] Mantendo navegador aberto por 30 segundos...")
        time.sleep(30)
        driver.quit()
        print("✅ Navegador fechado")

if __name__ == "__main__":
    success = test_esaj_login()
    
    print("\n" + "=" * 80)
    print("RESULTADO DO TESTE")
    print("=" * 80)
    
    if success:
        print("✅ TESTE BEM-SUCEDIDO!")
        print("   O crawler pode usar esse perfil para fazer login!")
    else:
        print("❌ TESTE FALHOU")
        print("   Verifique os screenshots para diagnóstico")
    
    print("\nScreenshots salvos em: /opt/crawler_tjsp/screenshots/")
    print("Copie para /home/crawler/ para visualizar via RDP")
