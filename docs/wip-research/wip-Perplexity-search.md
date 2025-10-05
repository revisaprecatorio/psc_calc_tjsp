Agora vou analisar os arquivos do projeto e criar uma resposta abrangente com soluções alternativas.

## Soluções para o Problema do Web Crawler TJSP em Ambiente Ubuntu Headless

Baseado na análise dos seus arquivos e na pesquisa realizada, identifiquei o problema raiz e apresento várias alternativas para resolver a questão do Web Signer em ambiente headless.

### 📊 Análise do Problema Atual

Seu projeto está enfrentando o **bloqueio crítico** confirmado no `DEPLOY_TRACKING.md`: a **comunicação Native Messaging entre a extensão Chrome e o Web Signer está sendo bloqueada** em ambiente headless. O problema não é de configuração, mas uma limitação arquitetural:

1. ✅ **Infrastructure funciona**: Xvfb, ChromeDriver, certificado digital importado
2. ✅ **Web Signer instalado**: Executável rodando, manifesto configurado  
3. ✅ **Extensão Chrome carregada**: Via `--load-extension`
4. ❌ **Native Messaging falha**: Log do Web Signer vazio, sem comunicação

### 🚀 **Solução 1: Alternativa com Chrome Policy (RECOMENDADA)**

A solução mais promissora é usar **Chrome Policies** para auto-seleção de certificados, bypass do Web Signer:

#### Implementação:

```bash
# 1. Criar diretório de políticas
mkdir -p /etc/opt/chrome/policies/managed

# 2. Configurar auto-seleção de certificados
cat > /etc/opt/chrome/policies/managed/certificates.json << 'EOF'
{
  "AutoSelectCertificateForUrls": [
    "{\"pattern\":\"https://esaj.tjsp.jus.br/*\",\"filter\":{\"ISSUER\":{\"CN\":\"AC Certisign RFB G5\"}}}"
  ]
}
EOF

# 3. Garantir permissões
chmod 644 /etc/opt/chrome/policies/managed/certificates.json
```

#### Modificação no crawler:

```python
def _build_chrome(attach, user_data_dir, cert_issuer_cn, cert_subject_cn,
                 debugger_address=None, headless=False, download_dir="downloads"):
    
    # Remover dependência do Web Signer
    opts = Options()
    
    # Configurar certificado via policy (em vez de Web Signer)
    if cert_issuer_cn or cert_subject_cn:
        # Policy já configurada no sistema, Chrome vai auto-selecionar
        pass
    
    # Forçar uso do NSS database
    opts.add_argument("--user-data-dir=/root/.config/google-chrome")
    
    # NÃO carregar extensão Web Signer (causa do problema)
    # opts.add_argument("--load-extension=...")  # REMOVER
    
    return webdriver.Chrome(options=opts)
```

### 🔧 **Solução 2: Implementação com Requests + Client Certificate**

Alternativa robusta usando **Python Requests** com autenticação por certificado, bypass total do navegador:

```python
import requests
from requests.adapters import HTTPAdapter
import ssl

class TJSPClient:
    def __init__(self, cert_path, key_path, cert_password=None):
        self.session = requests.Session()
        
        # Configurar certificado cliente
        if cert_password:
            # Se certificado .p12/.pfx
            self.session.cert = (cert_path, key_path)
        else:
            # Se certificado PEM
            self.session.cert = cert_path
            
        # Configurar SSL
        self.session.verify = True
        
    def authenticate_tjsp(self):
        """Autentica no TJSP usando certificado"""
        login_url = "https://esaj.tjsp.jus.br/sajcas/login"
        
        response = self.session.get(login_url)
        if response.status_code == 200:
            return True
        return False
    
    def query_process(self, cpf_cnpj):
        """Consulta processos por CPF/CNPJ"""
        query_url = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
        
        data = {
            'dadosConsulta.valorConsulta': cpf_cnpj,
            # Outros parâmetros necessários
        }
        
        response = self.session.post(query_url, data=data)
        return response.text

# Uso:
client = TJSPClient('/opt/crawler_tjsp/certs/cert.pem', 
                   '/opt/crawler_tjsp/certs/key.pem')
if client.authenticate_tjsp():
    results = client.query_process('12345678900')
```

### 🐳 **Solução 3: Container com Firefox + NSS Database**

Use **Firefox** em vez de Chrome, que tem melhor suporte para certificados em headless:

#### Dockerfile modificado:

```dockerfile
FROM ubuntu:22.04

# Instalar Firefox em vez de Chrome
RUN apt-get update && apt-get install -y \
    firefox \
    firefox-geckodriver \
    libnss3-tools \
    xvfb

# Configurar certificado no NSS database
COPY certs/cert.pem /app/certs/
COPY certs/key.pem /app/certs/

RUN mkdir -p /root/.mozilla/firefox/default.profile \
    && certutil -N -d /root/.mozilla/firefox/default.profile --empty-password \
    && pk12util -i /app/certs/25424636_pf.pfx -d /root/.mozilla/firefox/default.profile -W ""

# Configurar profile Firefox
RUN echo 'user_pref("security.default_personal_cert", "Select Automatically");' >> /root/.mozilla/firefox/default.profile/prefs.js
```

#### Modificação no crawler para Firefox:

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def _build_firefox():
    options = Options()
    options.headless = True
    
    # Usar profile com certificado
    profile = webdriver.FirefoxProfile('/root/.mozilla/firefox/default.profile')
    profile.set_preference("security.default_personal_cert", "Select Automatically")
    
    return webdriver.Firefox(options=options, firefox_profile=profile)
```

### ⚡ **Solução 4: API REST Reversa (Approach Avançado)**

Interceptar e replicar as chamadas AJAX do TJSP:

```python
import requests
import json
from urllib.parse import urlencode

class TJSPApiClient:
    def __init__(self, session_cookies):
        self.session = requests.Session()
        self.session.cookies.update(session_cookies)
        
    def direct_query(self, cpf_cnpj):
        """Chamada direta à API interna do TJSP"""
        
        # URL da API interna (descoberta via DevTools)
        api_url = "https://esaj.tjsp.jus.br/cpopg/search.do"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://esaj.tjsp.jus.br/cpopg/open.do'
        }
        
        data = {
            'conversationId': '',
            'dadosConsulta.valorConsulta': cpf_cnpj,
            'dadosConsulta.tipoNuProcesso': 'UNIFICADO',
            'dadosConsulta.valorConsultaUnificado': cpf_cnpj,
            'uuidCaptcha': '',
            'vlCaptcha': '',
            'novoVlCaptcha': ''
        }
        
        response = self.session.post(api_url, headers=headers, data=data)
        return self._parse_response(response.text)
    
    def _parse_response(self, html_content):
        """Parse da resposta HTML para extrair dados estruturados"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        processes = []
        for row in soup.select('tr.fundocinza1, tr.fundocinza2'):
            process_data = {
                'numero': row.select_one('td:nth-child(1)').text.strip(),
                'classe': row.select_one('td:nth-child(2)').text.strip(),
                'assunto': row.select_one('td:nth-child(3)').text.strip(),
            }
            processes.append(process_data)
        
        return processes
```

### 🌐 **Solução 5: VPS com Interface Gráfica**

Se as soluções headless não funcionarem, considere uma **VPS com ambiente gráfico**:

#### Opções de provedores:

1. **DigitalOcean**: Droplets com Ubuntu Desktop
2. **AWS EC2**: Instâncias com interface gráfica via RDP/VNC
3. **Google Cloud**: VM com desktop environment
4. **Azure**: Virtual Desktop Infrastructure

#### Configuração (Ubuntu Desktop na VPS):

```bash
# Instalar ambiente desktop
sudo apt update
sudo apt install ubuntu-desktop-minimal

# Configurar VNC server
sudo apt install tightvncserver
vncserver :1 -geometry 1920x1080 -depth 24

# Instalar Chrome com interface
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable

# Executar crawler via VNC
DISPLAY=:1 python crawler_full.py --doc "12345678900"
```

### 📋 **Recomendação de Implementação**

**Prioridade 1**: Implementar **Solução 1** (Chrome Policies) - mais rápida e mantém arquitetura atual

**Prioridade 2**: Se Solução 1 falhar, implementar **Solução 2** (Requests) - mais robusta e independente de navegador

**Prioridade 3**: **Solução 5** (VPS Desktop) como fallback garantido

### 🔄 **Plano de Migração**

1. **Fase 1** (1-2 dias): Testar Solução 1 no ambiente atual
2. **Fase 2** (2-3 dias): Se necessário, implementar Solução 2  
3. **Fase 3** (1 dia): Documentar e deploy da solução funcionando
4. **Fase 4**: Monitoramento e ajustes finos

### 💡 **Considerações Importantes**

- **Segurança**: Todas as soluções mantêm a autenticação por certificado digital
- **Performance**: Solução 2 (Requests) será mais rápida que Selenium
- **Manutenção**: Solução 1 tem menor overhead de manutenção
- **Flexibilidade**: Solução 2 permite maior controle sobre requisições

A análise dos seus arquivos mostra que o projeto está muito bem estruturado. O problema é especificamente a incompatibilidade do Web Signer com ambiente headless, que pode ser contornada com essas alternativas.[1][2]

[1](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging)
[2](https://forum.robotframework.org/t/autoselectcertificateforurls-is-not-working-in-headless-chrome-with-robot-framework/3899)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6061823/76f93e0e-8416-4ac3-b734-33e09f943e17/docker-compose.yml)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6061823/2af5b8fd-5041-4570-be56-df7ad1299ddc/crawler_full.py)
[5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6061823/98998e11-b09a-4981-946f-ad7c0f00384e/DEPLOY_TRACKING.md)
[6](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6061823/b0d61e76-8289-4c0e-8842-0ab328ec56e2/README.md)
[7](https://www.tjsp.jus.br/PublicacaoADM/Handlers/FileFetch.ashx?id_arquivo=78781)
[8](https://aur.archlinux.org/packages/softplan-websigner)
[9](https://www.youtube.com/watch?v=XM3UdLFsqgw)
[10](https://www.youtube.com/watch?v=wAMSeS0nHP8)
[11](https://chromewebstore.google.com/detail/web-signer/bbafmabaelnnkondpfpjmdklbmfnbmol)
[12](https://sajajuda.esaj.softplan.com.br/hc/pt-br/articles/12917516417687-Como-instalo-o-Web-Signer-do-Portal-e-SAJ-no-Google-Chrome)
[13](https://www.tjsp.jus.br/Download/Portal/Coronavirus/ManuaisTI/Instala%C3%A7%C3%A3o%20web%20signer.pdf)
[14](https://websigner.softplan.com.br/Help)
[15](https://www.tjsp.jus.br/PeticionamentoJEC/PeticionamentoJEC/CertificacaoDigital)
[16](https://www.youtube.com/watch?v=pPVrIIMb3Ro)
[17](https://www.vivaolinux.com.br/dica/Instalando-o-softplan-websigner-no-Void-Linux-para-acesso-ao-ESAJ-Chromium)
[18](https://www.tjsp.jus.br/webconnection)
[19](http://dje.tjsp.jus.br/WebHelp/id_pre_requisitos.htm)
[20](https://websigner.softplan.com.br/Setup?brand=&jslib=&browser=Firefox&returnUrl=)
[21](https://dje.tjsp.jus.br/WebHelp/id_perguntas_frequentes_certificado_digital.htm)
[22](http://dje.tjsp.jus.br/WebHelp/apresentacao_web_signer.htm)
[23](https://get.websignerplugin.com)
[24](https://www.tjsp.jus.br/Download/Instalador/InstalandoAIC.pdf)
[25](https://consultasaj.tjam.jus.br/WebHelp/id_instalacao_lacuna.htm)
[26](https://www.tjsp.jus.br/Download/Instalador/Novo/GuiaInstalacaoWebConnection.pdf)
[27](https://aojesp.org.br/tjsp-institui-o-uso-da-autenticacao-multifator-como-medida-de-seguranca/)
[28](https://developer.chrome.com/docs/apps/nativeMessaging)
[29](https://stackoverflow.com/questions/78006454/how-to-set-up-google-chrome-extension-native-messaging-and-sending-parameters-to)
[30](https://www.registroxangrila.com.br/noticias/2023/tj-sp-valida-assinatura-digital-de-empresa-nao-credenciada-ao-icp?page=1)
[31](https://stackoverflow.com/questions/21956679/chrome-native-messaging-api-not-working-on-linux)
[32](https://github.com/browserpass/browserpass-native/issues/41)
[33](https://websigner.softplan.com.br)
[34](https://websigner.softplan.com.br/Help?brand=tjsp)
[35](https://issues.chromium.org/40084236)
[36](https://www.tjsp.jus.br/RHF/AutenticarDocumentos/)
[37](https://groups.google.com/a/chromium.org/g/chromium-discuss/c/leGSzllbP8g)
[38](https://barrosoadv.com.br/tj-sp-valida-assinatura-em-plataforma-nao-credenciada-ao-icp-brasil/)
[39](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)
[40](https://websigner.softplan.com.br/?brand=tjsp&jslib=)
[41](https://www.projuris.com.br/blog/plugin-web-signer-peticionamento-eletronico/)
[42](https://scrapeops.io/python-web-scraping-playbook/python-requests-fix-ssl-error/)
[43](https://stackoverflow.com/questions/56055156/select-client-certificate-for-authorization-in-chrome-headless-mode)
[44](https://stackoverflow.com/questions/62543584/is-there-an-alternative-to-headless-chrome-to-use-extensions)
[45](https://scrapingant.com/blog/requests-ignore-ssl)
[46](https://azure.microsoft.com/en-us/blog/exploring-mtls-setup-to-send-a-client-certificate-to-the-backend-and-ocsp-validation/)
[47](https://github.com/keepassxreboot/keepassxc/issues/287)
[48](https://www.reddit.com/r/learnpython/comments/1kxjppm/how_to_accessprovide_security_certificates_when/)
[49](https://learn.microsoft.com/en-us/answers/questions/5518657/how-to-use-client-certificate-authentication-in-az)
[50](https://github.com/efchatz/Covert-C2)
[51](https://stackoverflow.com/questions/17576324/python-requests-ssl-error-for-client-side-cert)
[52](https://help.sap.com/docs/btp/sap-business-technology-platform/configuring-client-certificate-authentication)
[53](https://docs.python.org/3/library/ssl.html)
[54](https://github.com/puppeteer/puppeteer/issues/5275)
[55](https://latenode.com/blog/how-headless-browser-detection-works-and-how-to-bypass-it)
[56](https://proxiesapi.com/articles/how-to-fix-sslerror-in-python-requests)
[57](https://github.com/puppeteer/puppeteer/issues/1319)
[58](https://www.reddit.com/r/learnpython/comments/3w2v1x/ssl_client_authentication_only_on_specific_routes/)
[59](https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/)
[60](https://www.aasp.org.br/comunicado/tjsp-comunica-indisponibilidade-no-e-saj-em-14-11/)
[61](https://msendpointmgr.com/2023/03/11/certificate-based-authentication-aad/)
[62](https://github.com/jespimentel/esaj_2_grau)
[63](https://documentation.botcity.dev/how-to/ssl-auth/)
[64](https://github.com/puppeteer/puppeteer/issues/5946)
[65](https://www.w3.org/TR/webauthn-3/)
[66](https://sajajuda.tribunais.softplan.com.br/hc/pt-br/articles/12983758727831-Como-realizo-a-instala%C3%A7%C3%A3o-do-Sistema-SAJ-Web-Connection-no-TJSP)
[67](https://groups.google.com/a/chromium.org/g/chromium-discuss/c/oBuvub4m_zs)
[68](https://www.codecentric.de/en/knowledge-hub/blog/selenium-and-ssl-certificates)
[69](https://www.tjsp.jus.br/eproc/Duvidas)
[70](https://github.com/enrialonso/playwright-auto-select-certificates-for-url)
[71](https://stackoverflow.com/questions/70835911/web-automation-login-with-certificate-chrome-python)
[72](https://esaj.tjsp.jus.br/sajcas/login)
[73](https://community.latenode.com/t/how-can-i-bypass-ssl-certificate-verification-in-a-headless-chrome-browser-using-codeception/1123)
[74](https://www.reddit.com/r/selfhosted/comments/17n4p1w/obtaining_valid_ssl_certs_for_internal_network/)
[75](https://www.tjsp.jus.br/Certidoes/Certidoes/CertidoesPrimeiraInstancia)
[76](https://issues.chromium.org/40830578)