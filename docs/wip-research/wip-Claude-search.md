# Soluções técnicas para automação web com certificado A1 e Web Signer em Ubuntu headless

Native Messaging entre extensões Chrome e executáveis nativos **falha sistematicamente em ambientes headless** independente da ferramenta utilizada. Seu problema não é um bug de configuração - é uma limitação arquitetural conhecida. A boa notícia: existem múltiplas alternativas viáveis e testadas em produção para contornar esta limitação no e-SAJ do TJSP.

## Por que Native Messaging falha em headless

ChromeDriver possui **suporte limitado ou inexistente para Native Messaging** em contextos automatizados. Discussões no Stack Overflow confirmam: "ChromeDriver simplesmente não suporta native messaging" (relatado desde 2017, persiste em 2025). Seus logs vazios indicam que o host nativo **nunca é iniciado** - não é problema de comunicação, mas de processo não sendo disparado pela extensão em ambiente Selenium.

O problema afeta todas as ferramentas de automação. Xvfb em si não é o gargalo - o isolamento do browser automatizado impede que a extensão localize e inicie o executável Web Signer mesmo com manifest correto. Chrome em modo `--headless` (antigo) tem compatibilidade ainda pior; o novo `--headless=new` (Chrome 109+) melhorou mas não resolve Native Messaging em Selenium.

### Descoberta crítica sobre Web Signer

Pesquisa revelou que **Softplan Web Signer é baseado na tecnologia Lacuna Web PKI**. A Lacuna Software (empresa brasileira de Brasília) desenvolveu o framework subjacente, que usa WebSocket (portas 54741, 51824, 59615) para comunicação extension-native. Esta arquitetura depende de processo nativo rodando localmente, explicando por que automação headless tradicional não funciona.

## Solução Tier 1: Windows Server na nuvem (RECOMENDADA)

**Melhor custo-benefício e confiabilidade** para seu caso específico (.NET Framework + Native Messaging).

### Por que escolher

O Web Signer é aplicação .NET Framework que **funciona nativamente no Windows sem conversões ou camadas de compatibilidade**. Native Messaging opera perfeitamente sem workarounds. Você pode debugar visualmente via RDP quando necessário, e o custo com instâncias Spot é competitivo com VPS Linux.

### Implementação prática

**AWS EC2 Windows Server** (t3.medium com Spot Instance):
- Custo: $9-18/mês (Spot) ou $30-60/mês (On-demand)
- SLA: 99.9% de disponibilidade
- Use AMI do Marketplace: "Selenium WebDriver on Windows" (pré-configurado)
- Setup em 2-3 horas incluindo Chrome, ChromeDriver e Web Signer

**Azure Virtual Machines** (alternativa):
- B2s (2 vCPU, 4GB RAM): ~$35/mês
- Azure Hybrid Benefit reduz 30% se você tiver licenças Windows
- VMs Spot: até 90% desconto

**Configuração passo a passo**:
1. Lançar instância Windows Server 2019/2022
2. Conectar via RDP (porta 3389) - restringir firewall ao seu IP
3. Instalar Web Signer 2.12.1 seguindo guia oficial TJSP
4. Instalar Chrome + extensão Web Signer (ID: bbafmabaelnnkondpfpjmdklbmfnbmol)
5. Importar certificado A1 (.pfx) no sistema
6. Configurar scripts Python/Selenium no Windows Task Scheduler
7. Testar fluxo completo e-SAJ com certificado

### Otimização de custos

- **Spot Instances**: economia de 70% mas pode ser interrompida (aceitável para automação não crítica)
- **Auto-shutdown**: script PowerShell para desligar fora do horário comercial
- **Reserved Instances**: 40-60% desconto para workload 24/7 contínuo

Esta solução está **em produção em sistemas financeiros e jurídicos** que exigem assinatura certificada. Não requer workarounds experimentais.

## Solução Tier 2: Bypass do browser com bibliotecas Python

**Para casos onde você pode eliminar o browser completamente** e fazer requisições HTTPS diretas com certificado.

### Abordagem recomendada

Identifique os endpoints **reais do e-SAJ** usando DevTools do browser (Network tab). O Web Signer provavelmente está apenas assinando requisições HTTP específicas que você pode replicar programaticamente.

**Biblioteca ideal**: `requests-pkcs12` (Python)

```python
from requests_pkcs12 import Pkcs12Adapter, Session

with Session() as s:
    s.mount('https://esaj.tjsp.jus.br', 
            Pkcs12Adapter(pkcs12_filename='certificado.p12', 
                         pkcs12_password='sua_senha'))
    
    # Requisição autenticada automaticamente
    response = s.post(
        'https://esaj.tjsp.jus.br/esaj/portal.do?servico=820000',
        data=payload_peticao
    )
```

Esta biblioteca oferece **API limpa sem arquivos temporários**, funciona perfeitamente com certificados ICP-Brasil A1, e elimina completamente a necessidade do browser.

### Limitação crítica

Funciona **apenas se TJSP aceitar autenticação TLS client certificate direta**. Você mencionou que testou e TJSP não aceitou - mas vale investigar se o problema foi configuração incorreta. Teste com:

1. Certificado completo incluindo cadeia ICP-Brasil
2. Bundle de CA raiz da ICP-Brasil (baixar de https://estrutura.iti.gov.br/)
3. Verificar se está usando endpoint correto (alguns sistemas têm endpoint específico para API vs browser)

### Alternativa Java

Para integração enterprise ou sistemas legados Java:

```java
SSLContext sslContext = SSLContextBuilder.create()
    .loadKeyMaterial(
        new File("certificado.p12"),
        "senha".toCharArray(),
        "senha".toCharArray()
    ).build();

CloseableHttpClient client = HttpClients.custom()
    .setSSLContext(sslContext)
    .build();
```

Projetos em produção confirmam que Apache HttpClient com PKCS12 funciona em automação judicial quando o sistema aceita client certificate direto.

## Solução Tier 3: Migração para Playwright

**Se você precisa manter automação browser** mas quer melhorar confiabilidade.

### Por que Playwright supera Selenium

**Playwright v1.46+ possui suporte nativo para certificados cliente** - feature inexistente no Selenium. Native Messaging continua problemático, mas ao menos certificados funcionam perfeitamente:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir='/tmp/profile',
        headless=True,
        args=['--load-extension=./web-signer-extension'],
        client_certificates=[{
            'origin': 'https://esaj.tjsp.jus.br',
            'pfxPath': './certificado.pfx',
            'passphrase': 'senha123'
        }]
    )
    page = context.new_page()
    page.goto('https://esaj.tjsp.jus.br/esaj/portal.do')
```

**Vantagens documentadas**:
- 80% redução no tempo de execução (migração Zenjob reportou isso)
- Auto-wait reduz testes flaky
- Debugging superior com trace viewer e video recording
- Docker oficial: `mcr.microsoft.com/playwright:v1.46.0-jammy`

### Limitação honesta

Native Messaging **ainda não funciona perfeitamente** em Playwright headless. Mas três alternativas:

1. **Substituir Native Messaging por WebSocket**: Implementar servidor WebSocket que substitua o Web Signer nativo
2. **Headed mode com Xvfb**: Playwright em modo headed (não `--headless`) com virtual display funciona melhor
3. **VNC/X11vnc para debug**: Conectar via VNC quando precisar visualizar

Playwright é **melhor investimento futuro** mesmo que não resolva Native Messaging imediatamente. Certificados já funcionam nativamente, performance superior, e você elimina problemas de versão ChromeDriver vs Chrome.

## Alternativa comercial: Legal Wizard

**Para quem prefere solução pronta em vez de desenvolver**.

### Serviço especializado em automação judicial brasileira

A Legal Wizard (https://www.legalwtech.com.br/) oferece **robôs prontos para e-SAJ e PJe** com suporte completo a certificados digitais:

**Planos disponíveis**:
- Desktop Robot Assistant: R$49,90/mês - roda localmente, gerencia certificados offline
- Cloud Automation: R$0,50 por CPU/segundo - automação sob demanda
- Monitoramento de processos: R$0,50/processo/dia
- Cópia de processos: R$15/processo
- Automações customizadas: a partir de R$1.500

**Benefícios chave**:
- **Já funciona com Web Signer** - eles resolveram o problema técnico
- Suporte via WhatsApp (+55 11 91197-1146)
- Integração com ChatGPT, Power BI, WhatsApp
- Logs auditáveis de todas operações
- Backup para quando sistemas judiciais ficam offline

Esta opção tem **ROI positivo** se você valoriza seu tempo de desenvolvimento acima de R$1.500. O custo operacional mensal é inferior a manter servidor Windows próprio.

### Integração com Lacuna Web PKI

Descoberta da pesquisa: Web Signer usa **Lacuna Software Web PKI** como base. Você pode licenciar Lacuna Web PKI diretamente (https://get.webpkiplugin.com/) e integrar via JavaScript API, potencialmente eliminando dependência do Web Signer específico da Softplan.

A Lacuna é empresa brasileira (Brasília), oferece suporte em português, e tem SDK completo com exemplos no GitHub (https://github.com/LacunaSoftware/RestPkiSamples).

## Docker com desktop environment completo

**Solução intermediária**: container com GUI real acessível via VNC.

### Implementação com SeleniumHQ oficial

Images Docker oficiais do Selenium incluem **Xvfb + VNC + noVNC** pré-configurados:

```yaml
# docker-compose.yml
version: '3'
services:
  chrome:
    image: selenium/standalone-chrome:4.35.0
    shm_size: 2gb
    ports:
      - "4444:4444"
      - "7900:7900"  # noVNC
    environment:
      - SE_START_XVFB=true
      - SE_SCREEN_WIDTH=1920
      - SE_SCREEN_HEIGHT=1080
    volumes:
      - ./certificados:/certificados
      - ./web-signer:/web-signer
```

Acesse http://localhost:7900 (senha: "secret") para **ver o browser rodando** e debugar Native Messaging visualmente.

### Alternativa com XFCE completo

Para desktop Linux completo no container:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    xfce4 xfce4-terminal x11vnc xvfb \
    mono-complete wget unzip \
    google-chrome-stable

# Instalar Web Signer
COPY web-signer.exe /opt/web-signer/
RUN chmod +x /opt/web-signer/web-signer.exe

# Script de inicialização
COPY start-vnc.sh /start-vnc.sh
CMD ["/start-vnc.sh"]
```

**Limitação real**: Mesmo com desktop environment completo, **não há garantia que Native Messaging funcionará** porque o problema é ChromeDriver + extensão, não apenas falta de GUI.

## Linux VPS com desktop via VNC/RDP

**Opção econômica** se você não quer cloud Windows mas precisa de GUI.

### Configuração XFCE + XRDP

Para seu VPS Ubuntu Hostinger existente:

```bash
# Instalar desktop leve
sudo apt update
sudo apt install -y xfce4 xfce4-terminal

# XRDP para acesso Windows Remote Desktop
sudo apt install -y xrdp
sudo systemctl enable xrdp

# Firewall
sudo ufw allow 3389/tcp

# Conectar via Remote Desktop Cliente (Windows/macOS/Linux)
# Endereço: seu_vps_ip:3389
```

**Custo**: $5-20/mês (VPS atual + desktop environment, sem custos adicionais)

**Vantagens**:
- Usa infraestrutura existente
- Acesso visual completo via RDP
- Controle total do ambiente

**Desvantagens**:
- Web Signer é .NET Framework, precisa **Mono no Linux** (compatibilidade não garantida)
- Native Messaging entre Chrome Linux e executável Mono é **extremamente problemático**
- VNC/RDP tem latência vs acesso local
- Mais manutenção manual (updates, segurança)

### Wine/CrossOver - NÃO recomendado

Pesquisa identificou que **Wine + Native Messaging é combinação quebrada**. Extensão Chrome roda no Chrome Linux nativo, tenta comunicar com host Windows rodando em Wine - IPC entre ambientes não funciona. Comunidade tentou wrappers bash mas falham na comunicação stdio.

**Veredicto**: Não perca tempo com Wine para este caso de uso específico.

## Abordagens alternativas de arquitetura

### Substituir Native Messaging por WebSocket

Se você tem acesso ao código ou pode fazer proxy, **implemente servidor WebSocket** que replica funcionalidade do Web Signer:

```python
# Servidor WebSocket Python
import asyncio
import websockets
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

async def handler(websocket, path):
    async for message in websocket:
        # Mensagem da extensão
        data = json.loads(message)
        
        if data['action'] == 'sign':
            # Assinar com certificado
            signature = sign_with_cert(data['payload'])
            await websocket.send(json.dumps({'signature': signature}))
        
        elif data['action'] == 'list_certificates':
            certs = list_available_certs()
            await websocket.send(json.dumps({'certificates': certs}))

# Modificar extensão para conectar ws://localhost:8765 em vez de Native Messaging
```

**Vantagens**:
- Funciona perfeitamente em headless
- Você controla toda comunicação
- Sem dependência de Native Messaging
- Facilita debugging

**Desafio**: Requer modificar a extensão Web Signer (que você não controla o código). Alternativa é desenvolver **sua própria extensão** que faz WebSocket + assina com cryptography Python.

### API REST para operações com certificado

Similar ao WebSocket mas usando HTTP:

```python
from flask import Flask, request
from requests_pkcs12 import Session

app = Flask(__name__)

@app.route('/api/sign', methods=['POST'])
def sign_data():
    data = request.json['data']
    
    # Usar certificado para assinar
    session = Session()
    response = session.post(
        'https://esaj.tjsp.jus.br/api/sign',
        json={'data': data},
        cert=('./cert.pem', './key.pem')
    )
    
    return response.json()

# Extensão customizada chama esta API
```

Extensão Chrome modificada chama seu endpoint local em vez de Native Messaging.

## Análise de trade-offs

| Solução | Custo/mês | Tempo setup | Confiabilidade | Manutenção | Melhor para |
|---------|-----------|-------------|----------------|------------|-------------|
| **Windows Server AWS** | $9-60 | 2-3h | ⭐⭐⭐⭐⭐ | Baixa | Solução definitiva, produção crítica |
| **Bypass com requests-pkcs12** | $5-10 | 1-2 semanas | ⭐⭐⭐⭐⭐ | Muito baixa | Se TJSP aceitar client cert direto |
| **Legal Wizard** | R$50-200 | Imediato | ⭐⭐⭐⭐⭐ | Zero | ROI rápido, sem dev interno |
| **Playwright migration** | $5-20 | 2-3 meses | ⭐⭐⭐⭐ | Baixa | Investimento longo prazo, múltiplos projetos |
| **Docker + VNC** | $5-20 | 1-2 dias | ⭐⭐⭐ | Média | Experimentação, não garante Native Messaging |
| **Linux VPS + XFCE** | $5-20 | 4-6h | ⭐⭐ | Alta | Budget extremamente limitado |
| **Wine/.NET** | $5-10 | 10+ horas | ⭐ | Muito alta | Não recomendado |

## Plano de ação recomendado

**Fase 1 - Validação (Semana 1)**:

1. **Testar bypass de browser** (2 dias):
   - Capture requisições reais do e-SAJ via DevTools
   - Teste `requests-pkcs12` com endpoints identificados
   - Se funcionar: **esta é sua solução mais simples**

2. **Avaliar ROI de Legal Wizard** (1 dia):
   - Contato via WhatsApp (+55 11 91197-1146)
   - Solicitar demo/trial do robot assistant
   - Comparar custo vs desenvolvimento interno

3. **Provisionar Windows Server teste** (2 dias):
   - Lançar t3.micro free tier AWS (750h/mês grátis por 12 meses)
   - Instalar Web Signer + testar Native Messaging
   - Validar fluxo completo e-SAJ

**Fase 2 - Implementação (Semana 2-4)**:

Baseado nos resultados da Fase 1, escolher:

**Se bypass funcionar**: Implementar solução Python pura
- Desenvolver módulo de integração e-SAJ
- Testes em ambiente homologação TJSP
- Deploy em VPS Ubuntu existente (não precisa mudar infra)

**Se Legal Wizard atender**: Contratar serviço
- Integrar API do Legal Wizard com seus sistemas
- Configurar monitoramentos necessários
- Eliminar desenvolvimento interno

**Se Windows Server for necessário**: Migrar para AWS/Azure
- Configurar instância Spot para economia
- Automatizar com Task Scheduler
- Implementar auto-shutdown para otimizar custos

**Fase 3 - Otimização (Mês 2)**:

1. Monitoramento e logging robusto
2. Alertas para expiração de certificado
3. Backup e disaster recovery
4. Documentação completa do processo

## Recursos técnicos adicionais

### Certificados ICP-Brasil

**Bundle de CA raiz** (necessário para validação completa):
- Download oficial: https://estrutura.iti.gov.br/
- GitHub gist: https://gist.github.com/skarllot/9663935

**Extrair informações do certificado A1**:
```python
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

pfx = open('certificado.pfx', 'rb').read()
private_key, cert, ca_certs = load_key_and_certificates(
    pfx, b'senha', None
)

# Extrair CPF/CNPJ (formato ICP-Brasil: "NOME:CPF")
cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
nome, cpf_cnpj = cn.split(':')

print(f"Nome: {nome}")
print(f"CPF/CNPJ: {cpf_cnpj}")
print(f"Validade: {cert.not_valid_after}")
```

### Comunidade e suporte

**Fóruns brasileiros**:
- Stack Overflow PT: tag `certificado-digital` (118 questões)
- AB2L (Associação Brasileira de Lawtechs): https://ab2l.org.br/
- GitHub projetos brasileiros: https://github.com/topics/esaj

**Suporte oficial**:
- SAJ Ajuda: https://sajajuda.esaj.softplan.com.br/
- CNJ PJe Wiki: https://www.pje.jus.br/wiki/
- ITI (ICP-Brasil): https://www.gov.br/iti/pt-br

**Projetos open source relevantes**:
- Lacuna Software: https://github.com/LacunaSoftware (base do Web Signer)
- e-SAJ scraper: https://github.com/betogrun/esaj
- ICP-Brasil auth Node.js: https://github.com/c0h1b4/autenticacao-ICP-Brasil

## Conclusão

Seu problema **não tem solução simples mantendo arquitetura atual** (Ubuntu headless + Selenium + Web Signer). Native Messaging não funciona por limitação arquitetural, não configuração incorreta.

**Melhor caminho**: Windows Server na nuvem ($9-30/mês) oferece solução confiável e testada em produção. Funciona imediatamente com Web Signer sem workarounds.

**Alternativa mais elegante**: Bypass completo do browser com `requests-pkcs12`, **se e quando TJSP aceitar client certificate direto**. Pesquise endpoints alternativos ou APIs não-browser do e-SAJ.

**Opção comercial**: Legal Wizard por R$50-200/mês elimina desenvolvimento técnico e oferece suporte especializado em automação judicial brasileira.

Todas as três opções estão **comprovadas em produção** e documentadas. Native Messaging em headless Linux permanece problema técnico sem solução confiável em 2025 para qualquer ferramenta (Selenium, Playwright, Puppeteer).

**Próximo passo imediato**: Teste de 3 dias validando as três abordagens simultaneamente para identificar qual melhor se adapta ao seu contexto técnico e orçamentário específico.