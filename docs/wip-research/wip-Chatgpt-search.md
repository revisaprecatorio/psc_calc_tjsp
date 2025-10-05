Perfeito — abaixo está o plano revisto **sem** as alternativas de *CPF/Senha + token por e-mail* e **sem** APIs/dados abertos. Foquei apenas em caminhos que preservam o uso do **certificado A1 + Softplan Web Signer** e que funcionam em VM/VPS.

---

# Estratégias viáveis (mantendo Web Signer)

## A) Ubuntu “headless” com **ambiente gráfico virtual** (recomendado primeiro)

A ideia é deixar o servidor “com cara” de desktop (X11 + window manager + VNC/RDP), executar o **Chrome normal (não headless)** com a **extensão do Web Signer** e o **host nativo** instalado, e então automatizar via Selenium/Playwright. Extensões não são suportadas no headless clássico; com Xvfb/desktop virtual elas passam a funcionar como em um desktop real. ([Google Groups][1])

### Passo a passo (Ubuntu 22.04/24.04)

1. **Pacotes base + desktop leve**

   ```bash
   sudo apt-get update
   sudo apt-get install -y xfce4 xfce4-goodies xorg dbus-x11 xrdp \
       xvfb unzip curl ca-certificates
   sudo systemctl enable xrdp && sudo systemctl restart xrdp
   ```

   (Você pode usar VNC em vez de xrdp, se preferir.)

2. **Chrome + ChromeDriver**

   ```bash
   wget -qO- https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | \
     sudo tee /etc/apt/sources.list.d/google-chrome.list
   sudo apt-get update && sudo apt-get install -y google-chrome-stable
   CHROME_VER=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
   wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VER.0.0/linux64/chromedriver-linux64.zip"
   unzip -o /tmp/chromedriver.zip -d /tmp && sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin && sudo chmod +x /usr/local/bin/chromedriver
   ```

3. **Instalar o Softplan Web Signer (Linux .deb)**
   Baixe do site oficial e instale: ([WebSigner][2])

   ```bash
   wget -O /tmp/websigner.deb https://websigner.softplan.com.br/download?os=debian
   sudo apt-get install -y /tmp/websigner.deb
   ```

   > Se o pacote exigir dependências (.NET/mono runtime), instale-as conforme o instalador solicitar.

4. **Manifesto de *Native Messaging***
   Confirme que o **JSON do host nativo** (Web Signer) está em um caminho válido para o Chrome. No Linux, o Chrome procura manifestos **no perfil do usuário** (subpasta `NativeMessagingHosts` do perfil) ou **no sistema** (ex.: `/etc/opt/chrome/native-messaging-hosts/`). ([Chrome for Developers][3])

   * Verifique o campo `"allowed_origins"` com **o ID exato da extensão** Web Signer.
   * Verifique o campo `"path"` apontando para o binário `websigner` e permissões `+x`.

5. **Instalar a extensão Web Signer no Chrome**

   * Se a .crx não estiver na Chrome Web Store, use `--load-extension=/caminho/da/extensao` ou instale **via perfil persistente**.
   * Depois, **entre no desktop remoto** (RDP/VNC), abra `chrome://extensions`, ative **Developer mode** e confira a extensão ativa.

6. **Importar o certificado A1 no Chrome/NSS**

   * Se for **.pfx**: importe pelo **Chrome GUI** (Settings → Privacy & Security → Security → Manage certificates → Your certificates → Import).
   * Você pode também usar `certutil` (NSS) se já faz isso no seu fluxo.

7. **Auto-seleção do certificado (sem diálogos)**
   Aplique a política **`AutoSelectCertificateForUrls`** para o domínio do TJSP, evitando pop-ups de escolha de certificado:

   * Em ambientes gerenciados, configure a política Chrome Enterprise. ([Chrome Enterprise][4])
   * Em host único, você pode injetar a política no **perfil** (arquivo `Policies/Managed/policies.json`) com o padrão do domínio e filtro por emissor/assunto do seu certificado.

8. **Iniciar o Chrome na sessão gráfica virtual**

   * Evite `--headless`. Use flags que reduzem atritos de automação:

     ```
     google-chrome \
       --no-first-run --no-default-browser-check \
       --disable-features=DialMediaRouteProvider \
       --disable-blink-features=AutomationControlled \
       --user-data-dir=/home/ubuntu/chrome-profile \
       --remote-debugging-port=9222
     ```

     (A flag `AutomationControlled` e técnicas tipo **undetected-chromedriver** ajudam a evitar bloqueios básicos por detecção de automação.) ([ZenRows][5])

9. **Validar comunicação do Web Signer**

   * Acesse a página de teste/instalação do Web Signer; o site detecta se o componente está OK. ([WebSigner][6])
   * O TJSP tem manuais que mostram o fluxo esperado após a instalação. ([TJSP][7])
   * Se “não instalado” persistir, revise **manifesto**, **ID da extensão** e **permissões**; verifique logs lançando o Chrome com `--enable-logging=stderr --v=1`.
   * Lembre-se: **extensões não funcionam no headless clássico** — por isso precisamos da sessão gráfica. ([Google Groups][1])

10. **Automatizar (Selenium/Playwright)**

    * Use **perfil persistente** (`--user-data-dir`) para manter cookies e o certificado.
    * Aponte o **WebDriver** para o binário do Chrome dessa sessão.
    * Se necessário, use *anti-bot hardening* (undetected-chromedriver).

> **Observação**: instalar um **window manager** (XFCE/LXDE) e usar **xrdp/VNC** tende a ser mais estável do que só `xvfb-run`. Muitas vezes o host nativo/DBus espera componentes que um desktop real fornece.

---

## B) VM **Windows Server** (compatibilidade máxima)

Se o Linux continuar bloqueando o *native messaging*, use uma VM Windows (AWS/GCP/Azure/Hostinger com Windows Server). O Web Signer é plenamente suportado em Windows (documentação e manuais do TJSP focam muito nesse ambiente). ([TJSP][7])

### Passos resumidos

1. **Provisionar** Windows Server + RDP.
2. **Instalar** Google Chrome + Web Signer (executável) + **extensão**. ([WebSigner][2])
3. **Importar** seu **.pfx** no **repositório do usuário** (MMC → Certificates) **ou** via Chrome GUI.
4. **Configurar `AutoSelectCertificateForUrls`** via Política de Grupo/Registry para o domínio do TJSP (evita prompt de seleção). ([Chrome Enterprise][4])
5. **Testar manualmente** no RDP (ver se o portal reconhece o plugin/cert). ([E-SAJ][8])
6. **Automatizar** com Selenium/Playwright (Chrome normal).

   * Use perfil persistente, *waits* adequados e trate *pop-ups*.

**Prós:** máxima compatibilidade com o Web Signer.
**Contras:** maior custo/licenciamento e overhead de máquina.

---

## C) Linux com **container GUI** (Docker + Xfce + VNC + Chrome + Web Signer)

Uma variação da opção A: empacotar tudo em **Docker** com um *desktop leve* (Xfce) e **VNC** embutidos, executar o Chrome “headed” dentro do contêiner e rodar seu crawler lá.

### Esqueleto de imagem (ideia)

* Base `ubuntu:22.04`.
* Instalar **Xfce**, **x11vnc**/**novnc**, **Chrome**, **ChromeDriver**.
* Adicionar **Web Signer .deb** e **manifesto** ao local do Chrome.
* Expor porta do VNC/noVNC para inspeção.
* **ENTRYPOINT** inicia o X, o window manager e o Chrome.
* Monte volume com o **perfil do Chrome** (certificado/estado persistentes).

**Referências técnicas**: usar extensão no modo “headless” exige X virtual; Xvfb + VNC é prática comum em testes com extensões. ([Stack Overflow][9])

---

## D) macOS em nuvem (ex.: MacStadium, AWS EC2 Mac)

Como você já validou no **macOS**, uma alternativa é **alugar um Mac em nuvem** e automatizar lá (Chrome + Web Signer para macOS).
**Prós:** reproduz exatamente seu ambiente funcional.
**Contras:** custo e disponibilidade (geralmente mais caro).

---

# Checklist de **diagnóstico** (quando “não comunica com host nativo”)

1. **Extensão ativa** e mesmo **ID** no `allowed_origins` do **manifesto**. ([Chrome for Developers][3])
2. **Caminho do manifesto** correto para o **Chrome** (user/system). ([Chrome for Developers][3])
3. **Permissões** do binário `websigner` (execução, *PATH*).
4. **Chrome NÃO headless**; rodando em sessão X/desktop. ([Google Groups][1])
5. **Política `AutoSelectCertificateForUrls`** aplicada e visível em `chrome://policy`. ([Google Cloud][10])
6. **User-agent & webdriver** “humanizados” (*undetected-chromedriver*, `--disable-blink-features=AutomationControlled`). ([ZenRows][5])
7. **Logs do Chrome** (`--enable-logging=stderr --v=1`) e **console da extensão** (via `chrome://extensions` → background/service worker) para ver erros de *native messaging*.
8. **Teste página Web Signer** (a página de ajuda/instalação detecta estado). ([WebSigner][6])
9. **Manual TJSP**: siga a sequência de “instalar → atualizar cadeias → reiniciar navegador”. ([TJSP][7])

---

# Orquestração & Operação

* **Agendamento**: systemd timers ou cron chamando seu runner (Docker/venv).
* **Observabilidade**: logs estruturados; *screenshots* em falha; HTML de erro salvo.
* **Higiene**: limite de taxa; janelas de execução fora de horário comercial para reduzir atritos.
* **Segurança**: proteja o **.pfx** (se for importado via Chrome GUI, remova cópias do disco); se usar NSS, proteja o *keystore*.

---

## Quando usar qual opção

* **Tente A (Ubuntu + desktop virtual)** primeiro. É barato, scriptável e mantém Linux.
* Se **A** falhar por limitação do Web Signer, vá de **C (Docker GUI)** para empacotar tudo.
* Se ainda travar a comunicação do host nativo, migre para **B (Windows)** — maior compatibilidade.
* **D (mac em nuvem)** é útil se você quiser replicar exatamente seu ambiente vencedor (macOS).

---

### Fontes citadas

* Site oficial do **Softplan Web Signer** (instalação/ajuda). ([WebSigner][2])
* **Manuais TJSP** relacionados a Web Signer/requisitos. ([TJSP][7])
* **Chrome Headless** e suporte a **extensões** (não suportadas no headless clássico; usar Xvfb/desktop). ([Google Groups][1])
* **Native Messaging**: locais de manifesto e regras. ([Chrome for Developers][3])
* Política **AutoSelectCertificateForUrls** (certificado automático por domínio). ([Chrome Enterprise][4])
* *Anti-bot hardening* em Selenium (**undetected-chromedriver** e flags). ([ZenRows][5])



[1]: https://groups.google.com/a/chromium.org/g/headless-dev/c/nEoeUkoNI0o/m/9KZ4Os46AQAJ?utm_source=chatgpt.com "Chrome Extensions"
[2]: https://websigner.softplan.com.br/?utm_source=chatgpt.com "Instalação Softplan Web Signer"
[3]: https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging?utm_source=chatgpt.com "Native messaging - Chrome for Developers"
[4]: https://chromeenterprise.google/policies/?utm_source=chatgpt.com "Chrome Enterprise Policy List & Management"
[5]: https://www.zenrows.com/blog/selenium-avoid-bot-detection?utm_source=chatgpt.com "How to Avoid Bot Detection With Selenium"
[6]: https://websigner.softplan.com.br/Help?utm_source=chatgpt.com "Instalação Softplan Web Signer"
[7]: https://www.tjsp.jus.br/Download/Portal/Coronavirus/ManuaisTI/Instala%C3%A7%C3%A3o%20web%20signer.pdf?utm_source=chatgpt.com "Instalação web signer"
[8]: https://esaj.tjsp.jus.br/esaj/portal.do?servico=820000&utm_source=chatgpt.com "Peticionamento Eletrônico"
[9]: https://stackoverflow.com/questions/45372066/is-it-possible-to-run-google-chrome-in-headless-mode-with-extensions?utm_source=chatgpt.com "Is it possible to run Google Chrome in headless mode with ..."
[10]: https://cloud.google.com/chrome-enterprise-premium/docs/enable-cba-enterprise-certificates?utm_source=chatgpt.com "Enable certificate-based access with your enterprise ..."


