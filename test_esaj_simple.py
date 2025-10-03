#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste SIMPLES: Verifica se e-SAJ checa Extension ID específico
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Remote
import time

def test_esaj_simple():
    """Teste simples e direto"""
    
    print("=" * 80)
    print("TESTE SIMPLES: Verificação de Extension ID no e-SAJ")
    print("=" * 80)
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    chromedriver_url = "http://localhost:4444"
    print(f"\n[1] Conectando ao ChromeDriver: {chromedriver_url}")
    driver = Remote(command_executor=chromedriver_url, options=opts)
    
    try:
        # Acessar e-SAJ
        print("\n[2] Acessando e-SAJ...")
        driver.get("https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check")
        time.sleep(3)
        
        # Clicar em "Certificado digital"
        print("\n[3] Clicando em 'Certificado digital'...")
        try:
            aba_cert = driver.find_element(By.ID, "linkAbaCertificado")
            aba_cert.click()
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Erro ao clicar: {e}")
        
        # Verificar código-fonte
        print("\n[4] Analisando código-fonte da página...")
        
        page_source = driver.page_source
        
        # Verificações simples
        checks = {
            'tem_websigner_js': 'WebSigner' in page_source,
            'verifica_extension_id': 'bbafmabaelnnkondpfpjmdklbmfnbmol' in page_source,
            'tem_chrome_runtime': 'chrome.runtime' in page_source,
            'tem_native_messaging': 'nativeMessaging' in page_source or 'native_messaging' in page_source,
        }
        
        print(f"\n📋 Verificações:")
        print(f"   Menciona 'WebSigner': {checks['tem_websigner_js']}")
        print(f"   Menciona Extension ID específico: {checks['verifica_extension_id']}")
        print(f"   Menciona 'chrome.runtime': {checks['tem_chrome_runtime']}")
        print(f"   Menciona 'nativeMessaging': {checks['tem_native_messaging']}")
        
        # Verificar scripts externos
        print("\n[5] Verificando scripts carregados...")
        scripts = driver.find_elements(By.TAG_NAME, "script")
        
        websigner_scripts = []
        for script in scripts:
            src = script.get_attribute("src")
            if src and ('websigner' in src.lower() or 'web-signer' in src.lower()):
                websigner_scripts.append(src)
        
        if websigner_scripts:
            print(f"   Scripts Web Signer encontrados:")
            for s in websigner_scripts:
                print(f"     - {s}")
        else:
            print(f"   Nenhum script Web Signer externo encontrado")
        
        # Verificar console
        print("\n[6] Verificando console do browser...")
        logs = driver.get_log('browser')
        
        websigner_logs = [log for log in logs if 'websigner' in log['message'].lower() or 'web-signer' in log['message'].lower()]
        
        if websigner_logs:
            print(f"   Logs relacionados ao Web Signer:")
            for log in websigner_logs[:5]:  # Primeiros 5
                print(f"     [{log['level']}] {log['message'][:100]}")
        else:
            print(f"   Nenhum log Web Signer no console")
        
        # Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/test_simple.png")
        print("\n✅ Screenshot salvo: test_simple.png")
        
        # CONCLUSÃO
        print("\n" + "=" * 80)
        print("CONCLUSÃO")
        print("=" * 80)
        
        if checks['verifica_extension_id']:
            print("\n❌ e-SAJ VERIFICA Extension ID ESPECÍFICO!")
            print("   Encontrado: 'bbafmabaelnnkondpfpjmdklbmfnbmol' no código")
            print("   Solução WebSocket NÃO FUNCIONARÁ sem modificar extensão original")
            print("\n   ➡️ RECOMENDAÇÃO: Usar Windows Server")
        else:
            print("\n✅ e-SAJ NÃO verifica Extension ID específico!")
            print("   Não encontrado 'bbafmabaelnnkondpfpjmdklbmfnbmol' no código")
            print("   Solução WebSocket PODE FUNCIONAR!")
            print("\n   ➡️ RECOMENDAÇÃO: Vale testar WebSocket antes de Windows Server")
        
        if checks['tem_websigner_js']:
            print("\n📌 Web Signer está sendo usado na página")
        
        return checks
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        print("\n[7] Mantendo navegador aberto por 10 segundos...")
        time.sleep(10)
        driver.quit()
        print("✅ Teste concluído")

if __name__ == "__main__":
    test_esaj_simple()
