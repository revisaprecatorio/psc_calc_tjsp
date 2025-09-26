# -*- coding: utf-8 -*-
"""
Crawler ESAJ TJSP - Consulta de Requisitórios
- Consulta por Documento da Parte OU por Número do Processo (CNJ)
- Abre Pasta Digital e baixa PDF (opcional)
- Modo TURBO (sem esperar a árvore) e fallback automático
- Seleção robusta na jstree (iframe, expand, clique real)
- Trata alerta "Selecione pelo menos um item da árvore"
- Métricas: started_at, finished_at, duration_seconds, duration_hms
- Fecha abas criadas pelo crawler e encerra o Chrome ao final

Requisitos:
  pip install selenium
  (opcional para fallback HTTP) pip install requests
"""

import argparse, json, re, sys, time, traceback, unicodedata, urllib.parse
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# ------------------------------------------------------------
# Constantes / utilitários
# ------------------------------------------------------------
BASE_URL = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do?gateway=true"
OUTPUT_DIR = Path("screenshots"); OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSO_REGEX = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")  # CNJ

def _slug(val) -> str:
    return re.sub(r"\W+", "_", str(val or "")).strip("_")

def _now_str(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def _ts_str():  return datetime.now().strftime("%Y%m%d_%H%M%S")

def _fmt_duration(sec: float) -> str:
    mins, secs = divmod(int(round(sec)), 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:d}h{mins:02d}m{secs:02d}s" if hrs else f"{mins:d}m{secs:02d}s"

def _safe_text(el):
    try:    return (el.text or "").strip()
    except: return ""

def debug(payload, msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    #line = f"[{ts}] {msg}"
    #print(line)
    #payload.setdefault("debug_steps", []).append(line)

# ============================================================
# Helpers para download de PDF (espera + fallback HTTP)
# ============================================================
def _wait_for_chromedownload(outdir, timeout=180):
    """Espera por .pdf finalizado em outdir, considerando .crdownload em progresso."""
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    end = time.time() + timeout
    while time.time() < end:
        for p in outdir.glob("*.pdf"):
            try:
                if p.exists() and p.stat().st_size > 0:
                    return str(p.resolve())
            except Exception:
                pass
        has_tmp = any(outdir.glob("*.crdownload"))
        time.sleep(1 if has_tmp else 0.5)
    return None

def _http_download_with_cookies(url, driver, outdir, filename=None, referer=None, timeout=180):
    """Baixa 'url' usando cookies do Chrome (driver) — fallback quando o Chrome não salva."""
    try:
        import requests
    except Exception:
        return None

    cookies = {}
    try:
        for c in driver.get_cookies():
            cookies[c.get("name")] = c.get("value")
    except Exception:
        pass

    headers = {"User-Agent": "Mozilla/5.0"}
    if referer:
        headers["Referer"] = referer

    if not filename:
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            docname = qs.get("doc", [None])[0]
        except Exception:
            docname = None
        if docname and str(docname).lower().endswith(".pdf"):
            filename = docname
        else:
            filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / filename

    try:
        with requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            with open(outfile, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        if outfile.exists() and outfile.stat().st_size > 0:
            return str(outfile.resolve())
    except Exception as e:
        print("[WARN] Fallback HTTP download falhou:", e)
    return None

# ------------------------------------------------------------
# Chrome
# ------------------------------------------------------------
def _build_chrome(attach, user_data_dir, cert_issuer_cn, cert_subject_cn,
                  debugger_address=None, headless=False, download_dir="downloads"):
    """
    Cria o Chrome com:
      - perfil (user_data_dir) ou ~/.pki (NSS com certificado A1)
      - prefs para FORÇAR DOWNLOAD de PDF (não abrir no viewer)
      - headless opcional
      - debuggerAddress (se fornecido)
    """
    from pathlib import Path
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException
    import json, os

    def make_options():
        opts = Options()

        # Perfil do Chrome → se não passar, usa ~/.pki (onde o entrypoint importou o cert A1)
        if user_data_dir:
            opts.add_argument(f"--user-data-dir={user_data_dir}")
            opts.add_argument("--profile-directory=Default")
        else:
            nss_profile = os.path.expanduser("~/.pki")
            opts.add_argument(f"--user-data-dir={nss_profile}")

        # Headless + flags úteis para VPS
        if headless:
            try:
                opts.add_argument("--headless=new")
            except Exception:
                opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-default-browser-check")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("--allow-running-insecure-content")

        # Força baixar PDF
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        prefs = {
            "download.default_directory": str(Path(download_dir).resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        opts.add_experimental_option("prefs", prefs)

        # Auto-seleção de certificado para o TJSP
        if cert_issuer_cn or cert_subject_cn:
            policy = {"pattern": "https://esaj.tjsp.jus.br", "filter": {}}
            if cert_issuer_cn:
                policy["filter"].setdefault("ISSUER", {})["CN"] = cert_issuer_cn
            if cert_subject_cn:
                policy["filter"].setdefault("SUBJECT", {})["CN"] = cert_subject_cn
            opts.add_argument("--auto-select-certificate-for-urls=" + json.dumps([policy]))

        # Usa o Chromium do container
        opts.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")

        return opts

    if not debugger_address:
        debugger_address = os.environ.get("DEBUGGER_ADDRESS")

    # Tenta anexar via debuggerAddress
    if debugger_address:
        try:
            opts = make_options()
            opts.add_experimental_option("debuggerAddress", debugger_address)
            d = webdriver.Chrome(options=opts)
            d.set_page_load_timeout(60)
            return d
        except WebDriverException as e:
            print(f"[WARN] Falha ao anexar em {debugger_address}: {e}. Abrindo Chrome novo…")

    # Chrome “novo”
    opts = make_options()
    if attach:
        opts.add_argument("--remote-allow-origins=*")
    d = webdriver.Chrome(options=opts)
    d.set_page_load_timeout(60)
    return d

# ------------------------------------------------------------
# CAS / Login
# ------------------------------------------------------------
def _switch_to_tab(wait, tab_sel):
    try:
        el = wait.until(EC.element_to_be_clickable(tab_sel)); el.click()
    except TimeoutException:
        pass

def _cas_login_with_password(wait, driver, usuario, senha):
    if "sajcas/login" not in (driver.current_url or ""):
        return True
    try:
        cpf = wait.until(EC.presence_of_element_located((By.ID, "username")))
        pwd = wait.until(EC.presence_of_element_located((By.ID, "password")))
    except TimeoutException:
        return False
    cpf.clear(); cpf.send_keys(usuario)
    pwd.clear(); pwd.send_keys(senha)
    for sel in [(By.ID, "submit"), (By.ID, "pbEntrar"), (By.CSS_SELECTOR, "button[type='submit']")]:
        try:
            btn = driver.find_element(*sel)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            btn.click(); break
        except Exception:
            continue
    try:
        WebDriverWait(driver, 15).until(EC.url_contains("/cpopg/"))
        return True
    except TimeoutException:
        return False

def _maybe_cas_login(wait, driver, cert_subject_cn, user=None, pwd=None, payload=None):
    if "sajcas/login" not in (driver.current_url or ""):
        debug(payload, "CAS: não precisou logar (já dentro).")
        return
    try:
        debug(payload, "CAS: tentando aba CERTIFICADO…")
        _switch_to_tab(wait, (By.ID, "linkAbaCertificado"))
        wait.until(EC.presence_of_element_located((By.ID, "certificados")))
        def options_ready(drv):
            try:
                els = drv.find_elements(By.CSS_SELECTOR, "#certificados option")
                if not els: return False
                first = (els[0].text or "").strip().lower()
                return not (len(els) == 1 and "carregando" in first)
            except: return False
        wait.until(options_ready)
        subj_hint = cert_subject_cn.split(":")[0].strip() if cert_subject_cn else None
        def pick():
            els = driver.find_elements(By.CSS_SELECTOR, "#certificados option"); ch = None
            if subj_hint:
                for o in els:
                    if subj_hint.lower() in ((o.text or "").lower()): ch = o; break
            if not ch:
                for o in els:
                    if (o.get_attribute("value") or '').strip(): ch = o; break
            return ch
        ch = pick()
        if not ch: raise RuntimeError("CAS: nenhum certificado disponível.")
        driver.execute_script("""
            const opt=arguments[0], sel=document.querySelector('#certificados');
            sel.value=opt.value; sel.dispatchEvent(new Event('change',{bubbles:true}));
        """, ch)
        debug(payload, f"CAS: certificado = {(ch.text or '').strip()}")
        clicked = False
        for by, sel in [(By.ID, "submitCertificado"),
                        (By.CSS_SELECTOR, "#submitCertificado,button#submitCertificado")]:
            els = driver.find_elements(by, sel)
            if els:
                try: els[0].click()
                except: driver.execute_script("arguments[0].click();", els[0])
                clicked = True; break
        if not clicked: raise RuntimeError("CAS: botão 'Entrar' (certificado) não encontrado.")
        wait.until(EC.url_contains("/cpopg/"))
        debug(payload, "CAS: certificado OK."); return
    except Exception:
        debug(payload, "CAS: falha no certificado. Tentando CPF/CNPJ…")
    if user and pwd and _cas_login_with_password(wait, driver, user, pwd):
        debug(payload, "CAS: login CPF/CNPJ OK."); return
    raise RuntimeError("CAS: autenticação necessária e não realizada.")

# ------------------------------------------------------------
# Consulta: Documento da Parte
# ------------------------------------------------------------
def _select_criterio_documento(wait, driver):
    sel_el = wait.until(EC.element_to_be_clickable((By.ID, "cbPesquisa")))
    sel = Select(sel_el)
    chosen = None
    for o in sel.options:
        if "documento da parte" in _safe_text(o).lower(): chosen = o; break
    if not chosen:
        for o in sel.options:
            v = (o.get_attribute("value") or "").lower()
            if "do" in v and "parte" in v: chosen = o; break
    if not chosen: raise RuntimeError("Não encontrei a opção 'Documento da Parte'.")
    sel.select_by_value(chosen.get_attribute("value"))
    wait.until(EC.visibility_of_element_located((By.ID, "campo_DOCPARTE")))

# ------------------------------------------------------------
# Consulta: Número do Processo (CNJ)
# ------------------------------------------------------------
def _parse_cnj_parts(texto_cnj: str):
    digits = re.sub(r"\D+", "", texto_cnj or "")
    if len(digits) < 17:
        raise ValueError("CNJ inválido — informe ao menos os 13 primeiros dígitos + foro.")
    primeiros13 = digits[:13]
    foro4 = digits[-4:]
    if len(foro4) != 4:
        raise ValueError("CNJ inválido — 4 dígitos do foro ausentes.")
    return primeiros13, foro4

def _select_criterio_processo(wait, driver, cnj_texto: str):
    sel_el = wait.until(EC.element_to_be_clickable((By.ID, "cbPesquisa")))
    sel = Select(sel_el)
    opt_proc = None
    for o in sel.options:
        if "número do processo" in _safe_text(o).lower() or "numero do processo" in _safe_text(o).lower():
            opt_proc = o; break
    if not opt_proc:
        for o in sel.options:
            v = (o.get_attribute("value") or "").upper()
            if "NUMPROC" in v: opt_proc = o; break
    if not opt_proc:
        raise RuntimeError("Não encontrei a opção 'Número do Processo' no seletor.")
    sel.select_by_value(opt_proc.get_attribute("value"))

    wait.until(EC.presence_of_element_located((By.ID, "NUMPROC")))
    wait.until(EC.presence_of_element_located((By.ID, "interna_NUMPROC")))

    primeiros13, foro4 = _parse_cnj_parts(cnj_texto)

    # rádio Unificado
    try:
        unif = driver.find_elements(By.CSS_SELECTOR, "input[name='dadosConsulta.valorConsultaUnificado'][value='UNIFICADO']")
        if not unif:
            unif = driver.find_elements(By.XPATH, "//input[@type='radio' and (@id='tipoNumero' or @name='tipoNumero' or contains(@name,'Unificado')) and (@value='UNIFICADO' or not(@value))]")
        if unif:
            try: unif[0].click()
            except Exception: driver.execute_script("arguments[0].click();", unif[0])
    except Exception:
        pass

    # campos
    def _find_first13():
        candidates = [
            (By.ID, "numeroDigitoAnoUnificado"),
            (By.NAME, "numeroDigitoAnoUnificado"),
            (By.NAME, "numeroDigitadoUnificado"),
            (By.CSS_SELECTOR, "input[aria-label*='treze primeiros dígitos' i]")
        ]
        for by, sel in candidates:
            els = driver.find_elements(by, sel)
            for el in els:
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception:
                    continue
        return None

    def _find_foro():
        candidates = [(By.ID, "foroNumeroUnificado"), (By.NAME, "foroNumeroUnificado")]
        for by, sel in candidates:
            els = driver.find_elements(by, sel)
            for el in els:
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception:
                    continue
        return None

    f13 = wait.until(lambda d: _find_first13())
    fforo = wait.until(lambda d: _find_foro())

    # set via JS (dispara eventos)
    def _js_set(el, value):
        driver.execute_script("""
            const el = arguments[0], v = arguments[1];
            if (!el) return;
            el.focus();
            el.value = '';
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.value = v;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            el.dispatchEvent(new Event('blur', {bubbles:true}));
        """, el, value)

    _js_set(f13, primeiros13)
    _js_set(fforo, foro4)

# ------------------------------------------------------------
# Disparo da consulta e espera do resultado
# ------------------------------------------------------------
def _submit_consulta(wait, driver, payload=None):
    # 1) botão
    try:
        btn = driver.find_element(By.ID, "botaoConsultarProcessos")
        try: driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        except Exception: pass
        try:
            btn.click()
            if payload: debug(payload, "Consultar: clique direto no #botaoConsultarProcessos.")
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", btn)
                if payload: debug(payload, "Consultar: clique via JS no #botaoConsultarProcessos.")
                return True
            except Exception:
                pass
    except Exception:
        pass

    # 2) submit no form
    js = """
      const f = document.getElementById('formConsulta') ||
                document.querySelector("form[name='consultarProcessoForm']") ||
                document.querySelector("form[action*='/cpopg/search.do']");
      if (f) {
        const btn = f.querySelector("button, input[type='submit']");
        if (btn) btn.removeAttribute('disabled');
        if (typeof f.requestSubmit === 'function') { f.requestSubmit(); return true; }
        if (typeof f.submit === 'function') { f.submit(); return true; }
      }
      return false;
    """
    try:
        if driver.execute_script(js):
            if payload: debug(payload, "Consultar: form.requestSubmit()/submit().")
            return True
    except Exception:
        pass

    # 3) ENTER no foro
    try:
        foro = None
        for sel in [(By.ID, "foroNumeroUnificado"), (By.NAME, "foroNumeroUnificado")]:
            els = driver.find_elements(*sel)
            if els and els[0].is_displayed() and els[0].is_enabled():
                foro = els[0]; break
        if foro:
            foro.send_keys(Keys.ENTER)
            if payload: debug(payload, "Consultar: ENTER no campo do foro.")
            return True
    except Exception:
        pass

    if payload: debug(payload, "Consultar: não consegui acionar.")
    return False

def _wait_result_page(driver, timeout=45, payload=None):
    end = time.time() + timeout
    last_url = None
    while time.time() < end:
        try:
            url = driver.current_url
            if url != last_url:
                last_url = url
                if payload: debug(payload, f"Após submit: URL -> {url}")
        except Exception:
            pass

        try:
            if driver.find_elements(By.ID, "numeroProcesso"):
                if payload: debug(payload, "Pós-submit: DETALHE.")
                return "detalhe"
        except Exception:
            pass

        try:
            if (driver.find_elements(By.CSS_SELECTOR, "a.linkProcesso, a[class*='numeroProcesso']") or
                driver.find_elements(By.CSS_SELECTOR, "div.classeProcesso")):
                if payload: debug(payload, "Pós-submit: LISTA.")
                return "lista"
        except Exception:
            pass
        time.sleep(0.5)
    if payload: debug(payload, "Pós-submit: timeout aguardando resultado.")
    return None

# ------------------------------------------------------------
# Detalhe
# ------------------------------------------------------------
def _extract_process_numbers_from_elements(elems):
    items, seen = [], set()
    for a in elems:
        txt = _safe_text(a) or (a.get_attribute("title") or "").strip()
        for m in PROCESSO_REGEX.findall(txt):
            if m not in seen:
                seen.add(m); items.append(m)
    return items

def _extract_details_from_detail_page(driver):
    data = {}
    def T(i):
        try: return driver.find_element(By.ID, i).text.strip()
        except: return None
    data["numero_processo"] = T("numeroProcesso")
    data["classe_processo"] = T("classeProcesso")
    data["assunto_processo"] = T("assuntoProcesso")
    data["foro_processo"] = T("foroProcesso")
    data["vara_processo"] = T("varaProcesso")
    data["juiz_processo"] = T("juizProcesso")
    data["is_precatorio"] = (data.get("classe_processo") or "").lower().find("precat") != -1
    try:
        data["link_pasta_digital"] = driver.find_element(By.ID, "linkPasta").get_attribute("href")
    except: data["link_pasta_digital"] = None
    return data["numero_processo"], data

# ------------------------------------------------------------
# Pasta Digital - helpers seleção/iframe/alerta
# ------------------------------------------------------------
def _open_pasta_digital(wait, driver, href, payload, timeout=20):
    old = driver.window_handles[:]
    debug(payload, f"PastaDigital: abrindo {href}")
    driver.get(href)
    def arrived(_):
        new = driver.window_handles
        if len(new) > len(old): driver.switch_to.window(new[-1])
        if "pastadigital" in (driver.current_url or ""): return True
        try: body = driver.find_element(By.TAG_NAME, "body").text.strip()
        except Exception: body = ""
        if body.startswith("http"): driver.get(body); return True
        return False
    try:
        WebDriverWait(driver, timeout).until(arrived)
        debug(payload, f"PastaDigital: URL atual {driver.current_url}")
    except TimeoutException:
        debug(payload, "PastaDigital: timeout ao abrir; tentando corpo com URL…")
        try:
            body = driver.find_element(By.TAG_NAME, "body").text.strip()
            if body.startswith("http"): driver.get(body)
        except Exception: pass

def _enable_downloads(driver, download_dir: Path, payload=None):
    download_dir.mkdir(parents=True, exist_ok=True)
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(download_dir)})
    if payload: debug(payload, f"Downloads habilitados em: {download_dir}")

def _has_pdf_500_banner(driver) -> bool:
    try:
        xp = ("//*[contains(@style,'background-color') or contains(@class,'error') or contains(@class,'textLayer')]"
              "[contains(normalize-space(.),'Resposta inesperada do servidor') or contains(normalize-space(.),'Unexpected server response (500)')]")
        return len(driver.find_elements(By.XPATH, xp)) > 0
    except: return False

def _close_pdf_banner_if_present(driver, payload):
    try:
        close = driver.find_elements(By.XPATH, "//*[normalize-space(text())='Fechar' or normalize-space(.)='Fechar']")
        if close:
            driver.execute_script("arguments[0].click();", close[0])
            debug(payload, "PDF viewer: banner 500 fechado.")
    except Exception: pass

def _switch_to_tree_iframe(driver, payload=None) -> bool:
    """Entra no iframe que contém #divArvore / #arvore_documentos (se houver)."""
    try:
        if driver.find_elements(By.CSS_SELECTOR, "#divArvore, #arvore_documentos"):
            return True
    except Exception:
        pass
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for idx, fr in enumerate(iframes):
        try:
            driver.switch_to.frame(fr)
            if driver.find_elements(By.CSS_SELECTOR, "#divArvore, #arvore_documentos"):
                if payload: debug(payload, f"Árvore encontrada no iframe #{idx}.")
                return True
        except Exception:
            pass
        finally:
            driver.switch_to.default_content()
    if payload: debug(payload, "Árvore não encontrada em iframes; permanecendo no contexto atual.")
    return False

def _ensure_some_selected(driver, payload=None, min_count=1, expand=True, max_clicks=200):
    """
    Garante seleção na jstree: tenta 'Todas', conta selecionados; se zero, expande e clica.
    Retorna o total selecionado.
    """
    _switch_to_tree_iframe(driver, payload)

    js_count = """
      (function(){
        const byChecked = document.querySelectorAll('#divArvore input[type=checkbox]:checked, #arvore_documentos input[type=checkbox]:checked').length;
        const byJstree  = document.querySelectorAll('#arvore_documentos .jstree-checked, #arvore_documentos a.jstree-clicked').length;
        return Math.max(byChecked, byJstree);
      })();
    """
    def count_selected():
        try: return int(driver.execute_script(js_count) or 0)
        except Exception: return 0

    # tenta "Todas"
    for _id in ("selecionarButton", "btnSelecionarTodos", "btSelecionarTodos"):
        btns = driver.find_elements(By.ID, _id)
        if btns:
            try: driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
            except Exception: pass
            try: btns[0].click()
            except Exception: driver.execute_script("arguments[0].click();", btns[0])
            if payload: debug(payload, f"Seleção: cliquei em 'Todas' (#{_id}).")
            time.sleep(0.3)
            break

    sel = count_selected()
    if sel >= min_count:
        if payload: debug(payload, f"Selecionados após 'Todas': {sel}.")
        return sel

    # turbo seletivo: expande e clica direto
    if expand:
        try:
            driver.execute_script("""
              try {
                var r = document.querySelector('#arvore_documentos');
                if (r && r.jstree) { r.jstree('open_all'); }
              } catch(e) {}
              var toggles = document.querySelectorAll('#arvore_documentos .jstree-closed > i.jstree-ocl');
              toggles.forEach(function(t){ try { t.click(); } catch(e){} });
            """)
        except Exception:
            pass

    try:
        clicked = driver.execute_script(f"""
          (function(maxClicks){{
            var clicks = 0;
            var nodes = document.querySelectorAll('#arvore_documentos .jstree-checkbox, #arvore_documentos a.jstree-anchor');
            for (var i=0; i<nodes.length && clicks<maxClicks; i++) {{
              var n = nodes[i];
              var li = n.closest('li');
              if (li && (li.classList.contains('jstree-checked') || li.querySelector('input[type=checkbox]:checked'))) continue;
              try {{ n.click(); clicks++; }} catch(e) {{}}
            }}
            return clicks;
          }})( 400 );
        """)
        if payload: debug(payload, f"Seleção: cliques diretos na árvore = {clicked}.")
    except Exception as e:
        if payload: debug(payload, f"Seleção: erro ao clicar jstree: {e}")

    sel = count_selected()
    if payload: debug(payload, f"Selecionados após jstree: {sel}.")
    return sel

def _dismiss_select_alert_and_retry(driver, payload=None) -> bool:
    """Fecha o alerta 'Selecione...' e tenta salvar novamente."""
    def _find_and_click_ok():
        ok = None
        for xp in (
            "//*[@id='btnMensagemOk']",
            "//input[@type='button' and translate(@value,'OK','ok')='ok']",
            "//button[normalize-space()='Ok' or normalize-space()='OK']",
        ):
            els = driver.find_elements(By.XPATH, xp)
            if els:
                ok = els[0]; break
        if ok:
            try: ok.click()
            except Exception: driver.execute_script("arguments[0].click();", ok)
            return True
        return False

    try:
        if not _find_and_click_ok():
            driver.switch_to.default_content()
            for fr in driver.find_elements(By.TAG_NAME, "iframe"):
                try:
                    driver.switch_to.frame(fr)
                    if _find_and_click_ok(): break
                except Exception:
                    pass
                finally:
                    driver.switch_to.default_content()
        if payload: debug(payload, "Alerta 'Selecione...' fechado (Ok).")
    except Exception:
        pass

    sel = _ensure_some_selected(driver, payload, min_count=1)
    if sel <= 0:
        if payload: debug(payload, "Alerta tratado, mas ainda zero itens selecionados.")
        return False

    try:
        how = driver.execute_script("""
          (function(){
            const candIds = ['salvarButton','btnSalvar','btSalvar'];
            for (const id of candIds){
              const btn = document.getElementById(id);
              if (btn){ btn.removeAttribute('disabled'); btn.click(); return 'btn:'+id; }
            }
            if (typeof salvarDocumento === 'function'){ try{ salvarDocumento(); return 'fn:salvarDocumento'; }catch(e){} }
            if (typeof salvar === 'function'){ try{ salvar(); return 'fn:salvar'; }catch(e){} }
            if (typeof versaoParaImpressao === 'function'){ try{ versaoParaImpressao(); return 'fn:versaoParaImpressao'; }catch(e){} }
            return null;
          })();
        """)
        if payload: debug(payload, f"Reenvio salvar após alerta via {how}.")
        return True
    except Exception:
        return False

def _wait_left_tree_loaded(wait, driver, payload, max_seconds=120):
    start = time.time()
    debug(payload, "Esperando árvore/botões da Pasta Digital… (até 120s)")
    try:
        wait.until(EC.any_of(
            EC.presence_of_element_located((By.ID, "divBotoes")),
            EC.presence_of_element_located((By.ID, "divBotoesInterna")),
            EC.presence_of_element_located((By.ID, "selecionarButton")),
            EC.presence_of_element_located((By.ID, "arvore_documentos")),
        ))
        debug(payload, "Estrutura base presente.")
    except TimeoutException:
        debug(payload, "ERRO: Estrutura básica não carregou a tempo.")
        raise
    try:
        interactive_wait = WebDriverWait(driver, max(1, max_seconds - (time.time() - start)))
        first_checkbox_selector = (By.CSS_SELECTOR, "#arvore_documentos .jstree-checkbox")
        interactive_wait.until(EC.element_to_be_clickable(first_checkbox_selector))
        debug(payload, "Árvore interativa (checkbox clicável).")
    except TimeoutException:
        total_docs = driver.execute_script("return document.querySelectorAll('#divArvore input[type=checkbox]').length;")
        if total_docs == 0:
            debug(payload, "AVISO: Árvore vazia (0 checkboxes). Prosseguindo.")
            return
        debug(payload, "ERRO: árvore/botões não ficaram interativos.")
        raise

def _click_footer_button(wait, driver, label_text: str, payload=None) -> bool:
    label = (label_text or "").strip()
    ids = {
        "todas": ["selecionarButton", "btnSelecionarTodos", "btSelecionarTodos"],
        "nenhuma": ["desmarcarButton", "btnDesmarcarTodos", "btDesmarcarTodos"],
        "baixar pdf": ["salvarButton", "btnSalvar", "btSalvar"],
        "versão para impressão": ["salvarButton", "btnSalvar", "btSalvar"],
    }.get(label.lower(), [])
    try: driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except Exception: pass
    for target_id in ids:
        try:
            btn = wait.until(EC.presence_of_element_located((By.ID, target_id)))
            try: wait.until(EC.element_to_be_clickable((By.ID, target_id)))
            except: pass
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try: btn.click()
            except: driver.execute_script("arguments[0].click();", btn)
            if payload: debug(payload, f"Clicou botão (id={target_id}) '{label}'.")
            return True
        except Exception: continue
    js = """
      const wanted=(arguments[0]||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
      const norm=s=>(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
      const areas=[document.querySelector('#divBotoes'),document.querySelector('#divBotoesInterna')].filter(Boolean);
      function pick(root){
        const nodes=Array.from(root.querySelectorAll('input[type=button],input[type=submit],button,a,[role=button]'));
        return nodes.find(el=>{ const v=norm(el.value), a=norm(el.getAttribute('aria-label')), t=norm(el.innerText||el.textContent), ttl=norm(el.title);
          return (v&&v.includes(wanted))||(a&&a.includes(wanted))||(t&&t.includes(wanted))||(ttl&&ttl.includes(wanted)); });
      }
      let el=null; for(const r of areas){ el=pick(r); if(el) break; }
      if(!el) el=pick(document); if(!el) return false; el.scrollIntoView({block:'center'}); el.click(); return true;
    """
    try:
        if driver.execute_script(js, label):
            if payload: debug(payload, f"Botão por texto '{label}' clicado.")
            return True
    except Exception: pass
    if payload: debug(payload, f"Botão '{label}' não encontrado/clicável.")
    return False

def _handle_print_modal_continue(wait, driver, payload, prefer="single", timeout=30):
    def _click_in_this_context() -> bool:
        try:
            present = (driver.find_elements(By.ID, "popupModalDiv") or
                       driver.find_elements(By.ID, "botaoContinuar") or
                       driver.find_elements(By.ID, "popupDividirDocumentos"))
            if not present: return False
        except Exception: return False
        try:
            if prefer == "single":
                for xp in ("//input[@id='opcao1']", "//label[contains(.,'Arquivo único')]"):
                    els = driver.find_elements(By.XPATH, xp)
                    if els:
                        try: els[0].click()
                        except Exception: driver.execute_script("arguments[0].click();", els[0]); break
            else:
                for xp in ("//input[@id='opcao2']", "//label[contains(.,'Um arquivo para cada documento')]"):
                    els = driver.find_elements(By.XPATH, xp)
                    if els:
                        try: els[0].click()
                        except Exception: driver.execute_script("arguments[0].click();", els[0]); break
        except Exception: pass
        try:
            btn = None
            try: btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "botaoContinuar")))
            except TimeoutException: pass
            if not btn:
                for xp in (
                    "//input[@id='botaoContinuar' or translate(@value,'ÁÀÂÃÉÊÍÓÔÕÚÜÇáàâãéêíóôõúüç','AAAAEEIOOOUUCaaaaeeiooouuc')='continuar']",
                    "//button[normalize-space()='Continuar']",
                    "//*[@role='button' and contains(translate(normalize-space(.),'ÁÀÂÃÉÊÍÓÔÕÚÜÇáàâãéêíóôõúüç','AAAAEEIOOOUUCaaaaeeiooouuc'),'continuar')]",
                ):
                    els = driver.find_elements(By.XPATH, xp)
                    if els: btn = els[0]; break
            if btn is not None:
                try: btn.click()
                except Exception: driver.execute_script("arguments[0].click();", btn)
                debug(payload, "Modal impressão: cliquei em 'Continuar'.")
                try: WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, "popupModalDiv")))
                except Exception: pass
                return True
        except Exception: pass
        return False
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: bool(d.find_elements(By.ID, "popupModalDiv") or d.find_elements(By.ID, "botaoContinuar") or d.find_elements(By.ID, "popupDividirDocumentos"))
        )
    except TimeoutException:
        return False
    if _click_in_this_context(): return True
    try:
        driver.switch_to.default_content()
        for f in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                driver.switch_to.frame(f)
                if _click_in_this_context(): return True
            except Exception: pass
            finally: driver.switch_to.default_content()
    except Exception: pass
    return False

def _handle_print_modal_save(wait, driver, payload, timeout=240):
    def _visible(el) -> bool:
        try:
            s = (el.get_attribute("style") or "").lower()
            if "display: none" in s or "visibility: hidden" in s: return False
            if el.get_attribute("disabled"): return False
            return el.is_displayed()
        except Exception: return False
    def _pick_and_click_here() -> bool:
        XPS = [
            "//*[@id='btnDownloadDocumento' or starts-with(@id,'btnDownloadDocumento')][self::input or self::button]",
            "//*[@class and contains(concat(' ',normalize-space(@class),' '),' btBaixarDocumento ')][self::input or self::button]",
            "//button[normalize-space()='Salvar o documento']",
            "//input[(translate(@value,'ÁÀÂÃÉÊÍÓÔÕÚÜÇáàâãéêíóôõúüç','AAAAEEIOOOUUCaaaaeeiooouuc')='salvar o documento') and (@type='button' or @type='submit')]",
        ]
        for xp in XPS:
            els = driver.find_elements(By.XPATH, xp)
            for el in els:
                if _visible(el):
                    try: driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    except Exception: pass
                    try: el.click()
                    except Exception: driver.execute_script("arguments[0].click();", el)
                    debug(payload, "Modal impressão: cliquei em 'Salvar o documento'."); return True
        return False
    end = time.time() + timeout
    def modal_present(drv):
        anchors = [(By.ID, "msgGerandoDocumentoOpcos"), (By.ID, "popupModalDiv")]
        for by, sel in anchors:
            if drv.find_elements(by, sel): return True
        return False
    while time.time() < end:
        try:
            if modal_present(driver) and _pick_and_click_here(): return True
            driver.switch_to.default_content()
            if modal_present(driver) and _pick_and_click_here(): return True
            for fr in driver.find_elements(By.TAG_NAME, "iframe"):
                try:
                    driver.switch_to.frame(fr)
                    if modal_present(driver) and _pick_and_click_here():
                        driver.switch_to.default_content(); return True
                except Exception: pass
                finally: driver.switch_to.default_content()
        except Exception: pass
        time.sleep(1.0)
    return False

def _force_open_download_url(driver, payload=None) -> bool:
    try:
        url = driver.execute_script(
            "return (document.getElementById('urlAcessoArquivo') || document.querySelector(\"input[name='urlAcessoArquivo']\") || {}).value || null;"
        )
        if url:
            driver.execute_script("window.open(arguments[0], '_blank');", url)
            if payload: debug(payload, "URL de download aberta em nova aba (urlAcessoArquivo).")
            return True
    except Exception as e:
        if payload: debug(payload, f"URL direta não pôde ser aberta: {e}")
    return False

def _await_new_pdf(download_dir: Path, before_set: set, timeout: int, payload=None) -> str | None:
    end = time.time() + timeout
    while time.time() < end:
        pdfs = [p for p in download_dir.glob("*.pdf") if p.name not in before_set]
        final = [p for p in pdfs if not (download_dir / (p.name + ".crdownload")).exists()]
        if final:
            final.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            if payload: debug(payload, f"PDF detectado: {final[0].name}")
            return str(final[0])
        time.sleep(0.4)
    if payload: debug(payload, "PDF não apareceu dentro do timeout.")
    return None

# ------------------------------------------------------------
# Baixar PDF (com TURBO + fallback automático + anti-alerta)
# ------------------------------------------------------------
def _baixar_todos_pasta_digital(wait, driver, download_dir: Path, payload, timeout=240, turbo_download=False):
    try:
        iframe_id = "frameDocumento"
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, iframe_id)))
            debug(payload, f"Iframe {iframe_id} (ID).")
        except TimeoutException:
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, iframe_id)))
                debug(payload, f"Iframe {iframe_id} (NAME).")
            except TimeoutException:
                debug(payload, f"AVISO: Iframe '{iframe_id}' não encontrado. Prosseguindo na página principal.")

        _enable_downloads(driver, download_dir, payload)

        # normal x turbo (fallback para turbo se árvore demorar)
        use_turbo = bool(turbo_download)
        if not use_turbo:
            try:
                debug(payload, "Esperando árvore/botões (máx. 12s)…")
                start = time.time()
                wait_short = WebDriverWait(driver, 12)
                wait_short.until(EC.any_of(
                    EC.presence_of_element_located((By.ID, "divBotoes")),
                    EC.presence_of_element_located((By.ID, "divBotoesInterna")),
                    EC.presence_of_element_located((By.ID, "arvore_documentos")),
                ))
                remain = max(1, 12 - int(time.time() - start))
                WebDriverWait(driver, remain).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#arvore_documentos"))
                )
                debug(payload, "Estrutura presente (tentará seleção normal).")
            except TimeoutException:
                debug(payload, "Árvore lenta. Caindo para TURBO…")
                use_turbo = True

        # seleção robusta
        if not use_turbo:
            selected = _ensure_some_selected(driver, payload, min_count=1, expand=False)
            if selected == 0:
                debug(payload, "Nada selecionado no fluxo normal; tentando jstree (expande + clicks)…")
                selected = _ensure_some_selected(driver, payload, min_count=1, expand=True)
        else:
            debug(payload, "TURBO: tentativa direta (jstree + JS)…")
            selected = _ensure_some_selected(driver, payload, min_count=1, expand=True, max_clicks=400)

        if selected == 0:
            debug(payload, "ERRO: não consegui selecionar nenhum item na árvore. Prosseguindo para tentar salvar (anti-alerta cuidará).")

        handles_before = driver.window_handles[:]
        antes = {p.name for p in download_dir.glob("*.pdf")}
        last_pdf_url = None

        # acionar Baixar PDF
        clicked = False
        js_click_save = r"""
          (function(){
            const candIds = ['salvarButton','btnSalvar','btSalvar'];
            for (const id of candIds){
              const btn = document.getElementById(id);
              if (btn){ btn.removeAttribute('disabled'); btn.click(); return 'btn:'+id; }
            }
            if (typeof salvarDocumento === 'function'){ try{ salvarDocumento(); return 'fn:salvarDocumento'; }catch(e){} }
            if (typeof salvar === 'function'){ try{ salvar(); return 'fn:salvar'; }catch(e){} }
            if (typeof versaoParaImpressao === 'function'){ try{ versaoParaImpressao(); return 'fn:versaoParaImpressao'; }catch(e){} }
            return null;
          })();
        """
        try:
            how = driver.execute_script(js_click_save)
            if how: clicked = True; debug(payload, f"Disparou salvar via {how}.")
        except Exception as e:
            debug(payload, f"Erro ao disparar salvar via JS: {e}")

        if not clicked:
            _click_footer_button(wait, driver, "baixar pdf", payload) or _click_footer_button(wait, driver, "versão para impressão", payload)

        # alerta "Selecione..."
        time.sleep(0.4)
        try:
            body_txt = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
        except Exception:
            body_txt = ""
        if "selecione pelo menos um item da árvore" in body_txt:
            _dismiss_select_alert_and_retry(driver, payload)

        # modais
        try: _handle_print_modal_continue(wait, driver, payload, prefer="single", timeout=12 if use_turbo else 20)
        except Exception: pass
        try:
            _handle_print_modal_save(wait, driver, payload, timeout=120 if use_turbo else 240)
            _force_open_download_url(driver, payload)
        except Exception: pass

        # nova aba / download
        try:
            WebDriverWait(driver, 30 if use_turbo else 60).until(
                lambda d: len(d.window_handles) > len(handles_before) or any(download_dir.glob("*.pdf"))
            )
            if len(driver.window_handles) > len(handles_before):
                driver.switch_to.window(driver.window_handles[-1])
                debug(payload, f"Aba nova: {driver.current_url}")
                last_pdf_url = driver.current_url
                _enable_downloads(driver, download_dir, payload)
        except Exception:
            try: _handle_print_modal_save(wait, driver, payload, timeout=90)
            except Exception: pass
            try: _force_open_download_url(driver, payload)
            except Exception: pass
            try:
                last_pdf_url = driver.current_url
            except Exception:
                last_pdf_url = None

        pdf = _await_new_pdf(download_dir, antes, 120 if use_turbo else timeout, payload)
        if pdf and not _has_pdf_500_banner(driver):
            debug(payload, "Download OK."); return [pdf]

        _close_pdf_banner_if_present(driver, payload)

        # Fallback HTTP
        if not pdf:
            referer = None
            try: referer = driver.current_url
            except Exception: pass
            fallback_url = last_pdf_url or referer
            if fallback_url and ("getPDFImpressao.do" in fallback_url or fallback_url.lower().endswith(".pdf")):
                debug(payload, "Tentando fallback HTTP (cookies) para baixar o PDF…")
                alt = _http_download_with_cookies(fallback_url, driver, download_dir, referer=referer, timeout=180)
                if alt:
                    debug(payload, f"Fallback OK: {alt}")
                    return [alt]

        raise TimeoutException("Falha no download direto.")
    finally:
        driver.switch_to.default_content()
        debug(payload, "Contexto: default content.")

# ------------------------------------------------------------
# Lista + paginação
# ------------------------------------------------------------
def _norm_txt(s: str) -> str:
    s = (s or "").replace("\xa0", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(s.lower().split())

def _click_next_page(wait, driver, payload) -> bool:
    js = """
      const norm=s=>(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toLowerCase();
      const labels = ['>', '>>', 'proxima', 'próxima', 'next'];
      const roots = [document.querySelector('.pagination'), document.querySelector('#paginacao'),
                     document.querySelector('#paginacaoSuperior'), document.body].filter(Boolean);
      function findIn(root){
        const els = Array.from(root.querySelectorAll('a,button,[role=button]'));
        for(const el of els){
          const t=norm(el.innerText||el.textContent), a=norm(el.getAttribute('aria-label')), ttl=norm(el.title);
          if (labels.some(w=> t===w || t.includes(w) || a===w || a.includes(w) || ttl===w || ttl.includes(w))) return el;
        }
        return null;
      }
      for(const r of roots){ const el=findIn(r); if(el){ el.scrollIntoView({block:'center'}); el.click(); return true; } }
      const icon = document.querySelector("a[aria-label*='Próxima'], a[aria-label*='proxima'], a[aria-label*='Next']");
      if (icon){ icon.scrollIntoView({block:'center'}); icon.click(); return true; }
      return false;
    """
    try:
        if not driver.execute_script(js):
            return False
        wait.until(EC.any_of(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.linkProcesso")),
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class*='numeroProcesso']")),
        ))
        debug(payload, "Paginação: próxima página.")
        return True
    except Exception:
        return False

def _iterar_precatorios_da_lista(wait, driver, baixar_pdf, download_dir, payload, turbo_download=False):
    xp_link_no_item = ".//a[contains(@class,'linkProcesso') or contains(@class,'numeroProcesso') or self::a]"
    def _espera_lista():
        wait.until(EC.any_of(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.linkProcesso, a[class*='numeroProcesso']")),
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.classeProcesso")),
        ))
    def _coleta_precatorios():
        divs = driver.find_elements(By.CSS_SELECTOR, "div.classeProcesso")
        hits = []
        for d in divs:
            try:
                raw = d.get_attribute("textContent")
                if "precatorio" in _norm_txt(raw):
                    li = d.find_element(By.XPATH, "ancestor::li[1]")
                    hits.append(li)
            except Exception:
                continue
        return hits
    total = 0
    while True:
        _espera_lista(); time.sleep(0.2)
        itens = _coleta_precatorios()
        debug(payload, f"Lista: {len(itens)} item(ns) 'Precatório' nesta página.")
        idx = 0
        while idx < len(itens):
            _espera_lista(); itens = _coleta_precatorios()
            if idx >= len(itens): break
            li = itens[idx]
            try:
                link = li.find_element(By.XPATH, xp_link_no_item)
            except Exception:
                idx += 1; continue
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
            try: link.click()
            except Exception: driver.execute_script("arguments[0].click();", link)
            wait.until(EC.presence_of_element_located((By.ID, "numeroProcesso")))
            _, data = _extract_details_from_detail_page(driver)
            payload["results"].append(data)
            if data.get("is_precatorio"): payload["has_precatorio"] = True
            debug(payload, f"Detalhe: {data.get('numero_processo')} | classe='{data.get('classe_processo')}'")
            if baixar_pdf and data.get("link_pasta_digital"):
                try:
                    _open_pasta_digital(wait, driver, data["link_pasta_digital"], payload)
                    files = _baixar_todos_pasta_digital(wait, driver, Path(download_dir), payload, turbo_download=turbo_download)
                    payload.setdefault("downloaded_files", []).extend(files)
                except Exception as e:
                    payload.setdefault("download_errors", []).append(str(e))
            driver.back()
            try: _espera_lista()
            except TimeoutException:
                driver.back(); _espera_lista()
            total += 1; idx += 1
            debug(payload, f"Voltou p/ lista. Total processados: {total}.")
        if not _click_next_page(wait, driver, payload): break
    debug(payload, f"Concluído: {total} 'Precatório'(s) processado(s).")
    return total

# ------------------------------------------------------------
# Fechamento de abas e sessão
# ------------------------------------------------------------
def _close_extra_tabs(driver, baseline_handles, payload=None):
    """Fecha todas as abas que não existiam quando o driver foi criado."""
    try:
        current = driver.window_handles
    except Exception:
        return
    for h in list(current):
        if h not in baseline_handles:
            try:
                driver.switch_to.window(h)
                driver.close()
                if payload: debug(payload, "Fechando aba criada pelo crawler.")
            except Exception:
                pass
    try:
        remain = driver.window_handles
        if remain:
            driver.switch_to.window(remain[0])
    except Exception:
        pass

# ------------------------------------------------------------
# Fluxo principal
# ------------------------------------------------------------
def go_and_extract(doc_number=None, attach=False, user_data_dir=None,
                   cert_issuer_cn=None, cert_subject_cn=None,
                   debugger_address=None, cas_usuario=None, cas_senha=None,
                   abrir_autos=False, baixar_pdf=False, download_dir="downloads",
                   process_number=None, turbo_download=False,
                   headless=False):
    label_input = process_number if process_number else doc_number
    payload = {"documento": doc_number, "processo": process_number, "ok": False, "has_precatorio": False,
               "found_process_numbers": [], "results": [], "error": None,
               "started_at": _now_str(), "finished_at": None}
    t0 = time.perf_counter()
    driver = None
    baseline_handles = set()
    try:
        # cria Chrome com prefs de download + headless se pedido
        driver = _build_chrome(
            attach, user_data_dir, cert_issuer_cn, cert_subject_cn,
            debugger_address=debugger_address, headless=headless, download_dir=download_dir
        )
        wait = WebDriverWait(driver, 30); driver.set_script_timeout(120)

        # abas existentes no início
        try:
            baseline_handles = set(driver.window_handles)
        except Exception:
            baseline_handles = set()

        debug(payload, "Abrindo tela de consulta…")
        driver.get(BASE_URL); wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        _maybe_cas_login(wait, driver, cert_subject_cn, user=cas_usuario, pwd=cas_senha, payload=payload)

        if process_number:
            _select_criterio_processo(wait, driver, process_number)
        else:
            _select_criterio_documento(wait, driver)
            inp = wait.until(EC.visibility_of_element_located((By.ID, "campo_DOCPARTE")))
            inp.clear(); inp.send_keys(doc_number)

        if not _submit_consulta(wait, driver, payload):
            raise TimeoutException("Não consegui acionar o 'Consultar'.")
        debug(payload, "Consulta enviada.")

        kind = _wait_result_page(driver, timeout=45, payload=payload)
        if kind == "lista":
            processos = driver.find_elements(By.CSS_SELECTOR, "a.linkProcesso, a[class*='numeroProcesso']")
            found = _extract_process_numbers_from_elements(processos)
            debug(payload, f"Resultados (lista): {len(found)} processo(s).")
            payload["found_process_numbers"] = found
            if abrir_autos:
                _iterar_precatorios_da_lista(wait, driver, baixar_pdf, download_dir, payload, turbo_download=turbo_download)
        elif kind == "detalhe":
            numero, data = _extract_details_from_detail_page(driver)
            if numero:
                payload["results"].append(data)
                payload["found_process_numbers"] = [numero]
                if data.get("is_precatorio"): payload["has_precatorio"] = True
                if abrir_autos and baixar_pdf and data.get("link_pasta_digital"):
                    _open_pasta_digital(wait, driver, data["link_pasta_digital"], payload)
                    try:
                        files = _baixar_todos_pasta_digital(wait, driver, Path(download_dir), payload, turbo_download=turbo_download)
                        #payload.setdefault("downloaded_files1", []).extend(files)
                    except Exception as e:
                        payload.setdefault("download_errors", []).append(str(e))
        else:
            raise TimeoutException("Depois do submit não encontrei lista nem detalhe.")

        ts = _ts_str()
        safe = _slug(label_input)
        scr = OUTPUT_DIR / f"screenshot_{safe}_{ts}.png"
        ##driver.save_screenshot(str(scr))
        #payload.update({"ok": True, "screenshot_path": str(scr), "last_url": driver.current_url})
        if payload.get("has_precatorio") or "consultaDeRequisitorios" in driver.current_url:
            payload["has_precatorio"] = True
        payload["finished_at"] = _now_str()
        elapsed = time.perf_counter() - t0
        payload["duration_seconds"] = round(elapsed, 3)
        #payload["duration_hms"] = _fmt_duration(elapsed)
        return payload

    except Exception as e:
        payload["error"] = f"{e.__class__.__name__}: {e}\n{traceback.format_exc()}"
        try: payload["last_url"] = driver.current_url if driver else None
        except: payload["last_url"] = None
        try:
            ts = _ts_str()
            safe = _slug(label_input)
            if driver:
                p_html = OUTPUT_DIR / f"erro_{safe}_{ts}.html"
                with open(p_html, "w", encoding="utf-8") as f: f.write(driver.page_source)
                payload["error_html_path"] = str(p_html)
                p_png = OUTPUT_DIR / f"erro_{safe}_{ts}.png"
                ##driver.save_screenshot(str(p_png))
                payload["error_screenshot_path"] = str(p_png)
        except Exception: pass
        payload["finished_at"] = _now_str()
        elapsed = time.perf_counter() - t0
        payload["duration_seconds"] = round(elapsed, 3)
        payload["duration_hms"] = _fmt_duration(elapsed)
        return payload
    finally:
        # Fecha abas criadas pelo crawler
        try:
            if driver:
                _close_extra_tabs(driver, baseline_handles, payload)
        except Exception:
            pass

        # Encerra o Chrome: se não estamos anexados a um Chrome externo, podemos fechar tudo
        try:
            if driver:
                if not debugger_address:
                    driver.quit()  # encerra o processo inteiro iniciado pelo Selenium
                else:
                    # Chrome externo (debugger): não encerramos o browser do usuário
                    try:
                        driver.close()
                    except Exception:
                        pass
        except Exception:
            pass

def main():
    p = argparse.ArgumentParser(description="Crawler ESAJ TJSP (Pasta Digital) — Documento da Parte OU Número do Processo (CNJ)")
    p.add_argument("--doc", required=True, help="Documento da parte (CPF/CNPJ) OU o CNJ completo (ex: 0158003-37.2025.8.26.0500)")
    p.add_argument("--attach", action="store_true")
    p.add_argument("--user-data-dir", dest="user_data_dir", default=None)
    p.add_argument("--cert-issuer-cn", dest="cert_issuer_cn", default=None)
    p.add_argument("--cert-subject-cn", dest="cert_subject_cn", default=None)
    p.add_argument("--debugger-address", dest="debugger_address", default=None)
    p.add_argument("--cas-usuario", dest="cas_usuario", default=None)
    p.add_argument("--cas-senha", dest="cas_senha", default=None)
    p.add_argument("--abrir-autos", action="store_true")
    p.add_argument("--baixar-pdf", action="store_true")
    p.add_argument("--turbo-download", action="store_true", help="Seleciona todos e dispara o download via JS; cai automaticamente se a árvore demorar.")
    p.add_argument("--download-dir", dest="download_dir", default="downloads")
    p.add_argument("--headless", action="store_true", help="Roda sem janelas (recomendado em VPS).")
    args = p.parse_args()

    raw = args.doc or ""
    is_cnj = bool(PROCESSO_REGEX.search(raw)) or (len(re.sub(r"\D+", "", raw)) >= 17)

    if is_cnj:
        res = go_and_extract(
            doc_number=None,
            process_number=raw,
            attach=args.attach,
            user_data_dir=args.user_data_dir,
            cert_issuer_cn=args.cert_issuer_cn,
            cert_subject_cn=args.cert_subject_cn,
            debugger_address=args.debugger_address,
            cas_usuario=args.cas_usuario,
            cas_senha=args.cas_senha,
            abrir_autos=args.abrir_autos,
            baixar_pdf=args.baixar_pdf,
            download_dir=args.download_dir,
            turbo_download=args.turbo_download,
            headless=args.headless,
        )
    else:
        doc = re.sub(r"\D+", "", raw)
        if not doc:
            #print(json.dumps({"documento": raw, "ok": False, "error": "Documento inválido",
            #                  "started_at": _now_str(), "finished_at": _now_str()}, ensure_ascii=False, indent=2))
            sys.exit(2)
        res = go_and_extract(
            doc_number=doc,
            process_number=None,
            attach=args.attach,
            user_data_dir=args.user_data_dir,
            cert_issuer_cn=args.cert_issuer_cn,
            cert_subject_cn=args.cert_subject_cn,
            debugger_address=args.debugger_address,
            cas_usuario=args.cas_usuario,
            cas_senha=args.cas_senha,
            abrir_autos=args.abrir_autos,
            baixar_pdf=args.baixar_pdf,
            download_dir=args.download_dir,
            turbo_download=args.turbo_download,
            headless=args.headless,
        )

    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
