#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir EXATAMENTE o que o e-SAJ verifica
Testa se podemos substituir Web Signer por solução customizada
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

def test_esaj_requirements():
    """Testa requisitos do e-SAJ para Web Signer"""
    
    print("=" * 80)
    print("TESTE: Requisitos do e-SAJ para Web Signer")
    print("=" * 80)
    
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    
    # Usar ChromeDriver remoto (porta 4444)
    from selenium.webdriver import Remote
    chromedriver_url = "http://localhost:4444"
    
    print(f"\n[0] Conectando ao ChromeDriver: {chromedriver_url}")
    driver = Remote(command_executor=chromedriver_url, options=opts)
    
    try:
        # 1. Acessar e-SAJ
        print("\n[1] Acessando e-SAJ...")
        driver.get("https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2Fj_spring_cas_security_check")
        time.sleep(3)
        
        # 2. Clicar em "Certificado digital"
        print("\n[2] Clicando em 'Certificado digital'...")
        try:
            aba_cert = driver.find_element(By.ID, "linkAbaCertificado")
            aba_cert.click()
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Erro ao clicar: {e}")
        
        # 3. Injetar script de teste
        print("\n[3] Injetando script de teste...")
        
        test_script = """
        // Criar objeto fake do Web Signer
        window.WebSignerFake = {
            listCertificates: function() {
                return Promise.resolve([{
                    subject: 'TESTE:12345678900',
                    issuer: 'AC TESTE',
                    serial: '123456',
                    notBefore: '2024-01-01',
                    notAfter: '2025-12-31'
                }]);
            },
            sign: function(data) {
                return Promise.resolve({
                    signature: 'fake_signature_base64',
                    certificate: {
                        subject: 'TESTE:12345678900'
                    }
                });
            },
            isAvailable: function() {
                return Promise.resolve(true);
            }
        };
        
        // Tentar substituir Web Signer original
        if (typeof window.WebSigner === 'undefined') {
            window.WebSigner = window.WebSignerFake;
            console.log('✅ Web Signer fake injetado (original não existe)');
        } else {
            console.log('⚠️ Web Signer original já existe');
        }
        
        // Retornar informações
        return {
            hasOriginal: typeof window.WebSigner !== 'undefined',
            canOverride: true,
            extensionId: chrome?.runtime?.id || 'N/A'
        };
        """
        
        result = driver.execute_script(test_script)
        print(f"\n📊 Resultado:")
        print(f"   Web Signer original existe: {result.get('hasOriginal')}")
        print(f"   Extension ID: {result.get('extensionId')}")
        
        # 4. Verificar se página detecta fake
        print("\n[4] Verificando se página aceita fake...")
        
        check_script = """
        // Tentar listar certificados
        if (window.WebSigner && window.WebSigner.listCertificates) {
            return window.WebSigner.listCertificates()
                .then(certs => {
                    return {
                        success: true,
                        certificates: certs,
                        message: 'Web Signer respondeu'
                    };
                })
                .catch(err => {
                    return {
                        success: false,
                        error: err.toString()
                    };
                });
        } else {
            return {
                success: false,
                error: 'Web Signer não disponível'
            };
        }
        """
        
        check_result = driver.execute_async_script("""
            var callback = arguments[arguments.length - 1];
            """ + check_script + """.then(callback);
        """)
        
        print(f"\n📋 Teste de chamada:")
        print(f"   Sucesso: {check_result.get('success')}")
        if check_result.get('success'):
            print(f"   Certificados: {check_result.get('certificates')}")
        else:
            print(f"   Erro: {check_result.get('error')}")
        
        # 5. Verificar código-fonte da página
        print("\n[5] Analisando código-fonte...")
        
        analyze_script = """
        // Procurar por verificações de extensão
        const scripts = Array.from(document.scripts);
        const checks = {
            hasExtensionIdCheck: false,
            hasSignatureCheck: false,
            hasVersionCheck: false,
            webSignerCalls: []
        };
        
        scripts.forEach(script => {
            const content = script.textContent || script.innerHTML;
            
            // Verificar se checa ID da extensão
            if (content.includes('bbafmabaelnnkondpfpjmdklbmfnbmol')) {
                checks.hasExtensionIdCheck = true;
            }
            
            // Verificar se checa assinatura
            if (content.includes('signature') || content.includes('verify')) {
                checks.hasSignatureCheck = true;
            }
            
            // Verificar se checa versão
            if (content.includes('getVersion') || content.includes('version')) {
                checks.hasVersionCheck = true;
            }
            
            // Encontrar chamadas ao Web Signer
            const matches = content.match(/WebSigner\\.\\w+/g);
            if (matches) {
                checks.webSignerCalls.push(...matches);
            }
        });
        
        return checks;
        """
        
        analysis = driver.execute_script(analyze_script)
        
        print(f"\n🔍 Análise de verificações:")
        print(f"   Verifica Extension ID: {analysis.get('hasExtensionIdCheck')}")
        print(f"   Verifica assinatura: {analysis.get('hasSignatureCheck')}")
        print(f"   Verifica versão: {analysis.get('hasVersionCheck')}")
        print(f"   Chamadas Web Signer: {set(analysis.get('webSignerCalls', []))}")
        
        # 6. Screenshot
        driver.save_screenshot("/opt/crawler_tjsp/screenshots/test_requirements.png")
        print("\n✅ Screenshot salvo: test_requirements.png")
        
        # 7. Conclusão
        print("\n" + "=" * 80)
        print("CONCLUSÃO")
        print("=" * 80)
        
        if analysis.get('hasExtensionIdCheck'):
            print("❌ e-SAJ VERIFICA Extension ID específico")
            print("   Solução WebSocket NÃO FUNCIONARÁ sem modificar extensão original")
        else:
            print("✅ e-SAJ NÃO verifica Extension ID")
            print("   Solução WebSocket PODE FUNCIONAR!")
        
        if not analysis.get('webSignerCalls'):
            print("⚠️ Nenhuma chamada Web Signer detectada")
            print("   Pode ser carregado dinamicamente")
        
        return analysis
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        print("\n[6] Mantendo navegador aberto por 30 segundos...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    test_esaj_requirements()
