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
- Execucao direta python crawler_full.py --doc 03730461893 --attach --debugger-address "127.0.0.1:9222" --abrir-autos --baixar-pdf --download-dir "C:\Temp\RevisaDownloads"
Requisitos:
  pip install selenium
  (opcional para fallback HTTP) pip install requests
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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
#BASE_URL = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do?gateway=true"
BASE_URLS = [
    "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do",
    "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do?gateway=true",
]

BASE_URL = BASE_URLS[0]  # compatibilidade: código antigo pode usar BASE_URL


# BASE_URL "sempre existe" (compatibilidade com trechos antigos)
BASE_URL = next(
    (u for u in (BASE_URLS or []) if isinstance(u, str) and u.strip()),
    "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
)

def _ensure_cert_logged_in(wait, driver, payload, base_url="https://esaj.tjsp.jus.br/"):
    """
    Garante que a sessão esteja autenticada com certificado.
    A policy do Chrome cuida da seleção do certificado; aqui só disparamos o fluxo do site.
    """
    driver.get(base_url)
    time.sleep(0.5)

    # Se existir botão/link Identificar-se, clica para disparar autenticação
    ident = driver.find_elements(By.XPATH, "//a[contains(.,'Identificar-se') or contains(.,'Identificar')]")
    if ident:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ident[0])
            try:
                ident[0].click()
            except Exception:
                driver.execute_script("arguments[0].click();", ident[0])

            debug(payload, "Auth: clique em 'Identificar-se' disparado (certificado).")
        except Exception as e:
            payload.setdefault("auth_errors", []).append(str(e))
            return False

    # Espera algum indicativo de login concluído:
    # 1) sumir "Identificar-se" OU 2) aparecer "Sair" OU 3) URL mudar para área autenticada
    try:
        wait.until(EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[contains(.,'Sair') or contains(.,'Logout')]")),
            EC.invisibility_of_element_located((By.XPATH, "//a[contains(.,'Identificar-se') or contains(.,'Identificar')]")),
        ))
        debug(payload, "Auth: sessão parece autenticada.")
        return True
    except TimeoutException:
        debug(payload, "Auth: não consegui confirmar login (site pode exigir interação/tempo).")
        payload.setdefault("auth_required", True)
        return False

def _get_base_urls():
    """Retorna URLs base válidas (strings) e sem duplicar."""
    urls = []

    u = globals().get("BASE_URL", None)
    if isinstance(u, str) and u.strip():
        urls.append(u.strip())

    ul = globals().get("BASE_URLS", None)
    if isinstance(ul, (list, tuple)):
        urls.extend([x.strip() for x in ul if isinstance(x, str) and x.strip()])

    # dedupe mantendo ordem
    seen = set()
    out = []
    for x in urls:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

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
    line = f"[{ts}] {msg}"
    print(line, flush=True)  # O flush=True garante que apareça na hora no terminal
    payload.setdefault("debug_steps", []).append(line)

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
    - Se debugger_address for informado: anexa ao Chrome já aberto (remote debugging).
      Se falhar, NÃO abre um Chrome novo (porque isso perde a sessão/certificado).
    - Se NÃO houver debugger_address: abre Chrome novo (com user-data-dir, prefs, etc).
    """
    import os as _os
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import WebDriverException
    from pathlib import Path
    import json

    # ----------------------------
    # 1) MODO ATTACH (Chrome já aberto)
    # ----------------------------
    if debugger_address:
        opts_dbg = Options()
        # Importantíssimo: não usar user-data-dir aqui
        # (o Chrome já está rodando com o profile certo)
        opts_dbg.add_experimental_option("debuggerAddress", debugger_address)

        # Alguns ambientes precisam disso (não atrapalha o attach)
        opts_dbg.add_argument("--remote-allow-origins=*")

        print(f"[INFO] Tentando anexar ao Chrome existente em {debugger_address}...", flush=True)
        import time
        for i in range(3): # Tenta 3 vezes
            try:
                print(f"[INFO] Tentativa de conexão {i+1}/3 em {debugger_address}...", flush=True)
                d = webdriver.Chrome(service=Service(), options=opts_dbg)
                d.set_page_load_timeout(60)
                return d
            except WebDriverException:
                time.sleep(2) # Espera 2s antes de tentar de novo
        
        # Se falhar nas 3, aí sim dá erro
        raise RuntimeError(
            "Falha ao conectar no Chrome (Porta 9222). "
            "Verifique se o Chrome foi aberto com --remote-debugging-port=9222"
        )
        

    # ----------------------------
    # 2) MODO NORMAL (abrir Chrome novo)
    # ----------------------------
    def make_options():
        opts = Options()

        if headless:
            try:
                opts.add_argument("--headless=new")
            except Exception:
                opts.add_argument("--headless")

        # Flags padrão
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--remote-allow-origins=*")

        if user_data_dir:
            print(f"[DEBUG] user-data-dir: {user_data_dir}", flush=True)
            opts.add_argument(f"--user-data-dir={user_data_dir}")

        # Preferências de download
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        prefs = {
            "download.default_directory": str(Path(download_dir).resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        opts.add_experimental_option("prefs", prefs)

        # Auto-seleção de certificado via flag (opcional)
        if cert_issuer_cn or cert_subject_cn:
            policy = {"pattern": "https://esaj.tjsp.jus.br", "filter": {}}
            if cert_issuer_cn:
                policy["filter"].setdefault("ISSUER", {})["CN"] = cert_issuer_cn
            if cert_subject_cn:
                policy["filter"].setdefault("SUBJECT", {})["CN"] = cert_subject_cn
            opts.add_argument("--auto-select-certificate-for-urls=" + json.dumps([policy]))

        return opts

    print("[INFO] Usando Chrome novo (modo normal).", flush=True)
    opts = make_options()
    d = webdriver.Chrome(service=Service(), options=opts)
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
    """
    Autentica quando necessário.
    Versão Otimizada:
    - Detecta "Identifique-se" e clica se necessário.
    - Força seleção do certificado (índice 1) via JavaScript para evitar erros de UI.
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    # --- Funções auxiliares internas ---
    def _norm(s: str) -> str:
        import unicodedata
        s = (s or "").replace("\xa0", " ")
        s = unicodedata.normalize("NFKD", s)
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
        return " ".join(s.lower().split())

    def _is_cas_login_url() -> bool:
        try:
            return "sajcas/login" in (driver.current_url or "").lower()
        except Exception:
            return False

    def _page_has_identifique_se() -> bool:
        try:
            elems = driver.find_elements(By.XPATH, "//*[self::a or self::button or @role='button']")
            for el in elems:
                try:
                    t = _norm(el.text or el.get_attribute("textContent") or "")
                    if "identifique" in t:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def _click_identifique_se() -> bool:
        try:
            elems = driver.find_elements(By.XPATH, "//*[self::a or self::button or @role='button']")
            for el in elems:
                try:
                    t = _norm(el.text or el.get_attribute("textContent") or "")
                    if "identifique" in t:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                        try:
                            el.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", el)
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def _already_inside_app() -> bool:
        try:
            if driver.find_elements(By.ID, "cbPesquisa"): return True
            if driver.find_elements(By.ID, "campo_DOCPARTE") or driver.find_elements(By.ID, "NUMPROC"): return True
            if driver.find_elements(By.ID, "numeroProcesso"): return True
        except Exception:
            pass
        return False

    # --- Lógica de Fluxo ---

    # 1. Se não está em URL de login, mas tem "Identifique-se", clica.
    if (not _is_cas_login_url()) and _page_has_identifique_se() and (not _already_inside_app()):
        debug(payload, "CAS: achei 'Identifique-se' na página; clicando...")
        _click_identifique_se()
        try:
            WebDriverWait(driver, 10).until(lambda d: _is_cas_login_url() or _already_inside_app())
        except TimeoutException:
            pass

    # 2. Se depois disso não está em login e já parece dentro, retorna
    if not _is_cas_login_url():
        debug(payload, "CAS: não precisou logar (já dentro/url diferente).")
        return

    # =========================
    # PRIORIDADE 1: Certificado (Versão Otimizada / Agressiva)
    # =========================
    try:
        debug(payload, "CAS: Tentando login via Certificado...")

        # A. Clica na aba certificado (garantia)
        try:
            tab = driver.find_element(By.ID, "linkAbaCertificado")
            driver.execute_script("arguments[0].click();", tab)
            time.sleep(1)
        except Exception:
            pass 

        # B. Seleciona o certificado via JS (Pega o índice 1, ignorando placeholder)
        # Isso resolve problemas onde o Selenium não consegue interagir com o <select>
        driver.execute_script("""
            var sel = document.getElementById('certificados');
            if (sel && sel.options.length > 1) {
                sel.selectedIndex = 1; 
                sel.dispatchEvent(new Event('change'));
                sel.dispatchEvent(new Event('input'));
            }
        """)
        time.sleep(0.5)

        # C. Clica no botão Entrar
        try:
            btn_entrar = driver.find_element(By.ID, "submitCertificado")
            driver.execute_script("arguments[0].click();", btn_entrar)
        except Exception:
            # Fallback se o ID mudar
            driver.execute_script("document.querySelector('#submitCertificado, button[type=submit]').click();")
        
        # D. Espera sair da URL de login
        WebDriverWait(driver, 30).until(lambda d: "sajcas" not in (d.current_url or ""))
        debug(payload, "CAS: Login via certificado enviado (sucesso).")
        return

    except Exception as e:
        debug(payload, f"CAS: Tentativa de certificado falhou: {e}")

    # =========================
    # FALLBACK: CPF/Senha
    # =========================
    if user and pwd:
        debug(payload, "CAS: tentando login com CPF/CNPJ (fallback)…")
        # _cas_login_with_password deve estar definida no escopo global do arquivo
        if _cas_login_with_password(wait, driver, user, pwd):
            debug(payload, "CAS: login CPF/CNPJ OK.")
            return
        debug(payload, "CAS: falha no login CPF/CNPJ.")

    raise RuntimeError("CAS: autenticação necessária e não realizada.")

def _ensure_esaj_authenticated(wait, driver, payload=None,
                               cert_subject_cn=None, cas_usuario=None, cas_senha=None,
                               base_url=None, timeout=20): # Timeout reduzido para ser mais ágil
    
    # Verifica se já existe o botão de sair (Logado)
    if driver.find_elements(By.XPATH, "//*[contains(text(), 'Sair') or contains(text(), 'Logoff')]"):
        return True

    # Verifica se existe o botão Identificar-se
    try:
        # Procura link que contenha "Identificar"
        btns = driver.find_elements(By.XPATH, "//a[contains(.,'Identificar')]")
        if btns:
            ident_btn = btns[0]
            if ident_btn.is_displayed():
                debug(payload, "Login: Botão 'Identificar-se' encontrado. Clicando...")
                driver.execute_script("arguments[0].click();", ident_btn)
                time.sleep(2)
                
                # Agora deve estar na tela do CAS ou Popup. Chama a função de login.
                _maybe_cas_login(wait, driver, cert_subject_cn, user=cas_usuario, pwd=cas_senha, payload=payload)
                return True
    except Exception as e:
        debug(payload, f"Erro ao tentar clicar em Identificar-se: {e}")

    # Se chegou aqui, ou já está logado ou falhou.
    # Verifica URL do CAS
    if "sajcas/login" in driver.current_url:
         _maybe_cas_login(wait, driver, cert_subject_cn, user=cas_usuario, pwd=cas_senha, payload=payload)
         return True

    return True

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
    """
    Versão Otimizada: Foca nos IDs confirmados pelo seu HTML.
    """
    import time
    
    # 1. Tenta o clique normal no botão identificado
    try:
        btn = driver.find_element(By.ID, "botaoConsultarProcessos")
        if btn.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5) # Dá um respiro pro site
            driver.execute_script("arguments[0].click();", btn)
            if payload: debug(payload, "Consultar: Clique JS no #botaoConsultarProcessos.")
            return True
    except Exception:
        pass

    # 2. Se o botão falhar, dispara o formulário direto pelo ID confirmado
    try:
        # Seu HTML confirmou que o id é 'formConsulta'
        driver.execute_script("document.getElementById('formConsulta').submit();")
        if payload: debug(payload, "Consultar: Forcei envio via formConsulta.submit().")
        return True
    except Exception:
        pass

    if payload: debug(payload, "Consultar: Falha crítica (botão e form falharam).")
    return False


def _wait_result_page(driver, timeout=90, payload=None):
    """
    Versão ajustada para detectar 'listagemDeProcessos' (ID confirmado no HTML).
    """
    import time
    from selenium.webdriver.common.by import By

    def _body_text_lower():
        try: return (driver.find_element(By.TAG_NAME, "body").text or "").strip().lower()
        except: return ""

    end = time.time() + timeout
    last_url = None

    while time.time() < end:
        try: url = driver.current_url or ""
        except: url = ""

        if url != last_url:
            last_url = url
            if payload: debug(payload, f"Pós-submit: URL -> {url}")

        # 1) DETECTA CAS / LOGIN / IDENTIFIQUE-SE
        body_l = _body_text_lower()
        if ("sajcas/login" in url.lower()) or ("identifique-se" in body_l) or ("certificado digital" in body_l):
            if payload: debug(payload, "Pós-submit: Login detectado. Tentando contornar...")
            # (Aqui você pode manter sua lógica de login automático se tiver)
            time.sleep(1)
            continue

        # 2) DETALHE (Se cair direto no processo)
        try:
            if driver.find_elements(By.ID, "numeroProcesso"):
                if payload: debug(payload, "Pós-submit: DETALHE encontrado.")
                return "detalhe"
        except: pass

        # 3) LISTA (AQUI ESTÁ A CORREÇÃO CRUCIAL)
        try:
            # Verifica o container principal da lista OU links de processo
            if (driver.find_elements(By.ID, "listagemDeProcessos") or 
                driver.find_elements(By.CSS_SELECTOR, "a.linkProcesso")):
                if payload: debug(payload, "Pós-submit: LISTA encontrada.")
                return "lista"
        except: pass

        # 4) Verificação de 'Não Encontrado' para abortar rápido
        if "não existem dados" in body_l or "nenhum registro encontrado" in body_l:
             # Opcional: retornar um status específico ou deixar dar timeout se preferir
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
        a = driver.find_element(By.ID, "linkPasta")
        href = (a.get_attribute("href") or "").strip()
        # se for hash (#liberarAutoPorSenha), mantém mesmo assim (open_pasta_digital agora sabe tratar)
        data["link_pasta_digital"] = href if href else None
    except:
        data["link_pasta_digital"] = None

    return data["numero_processo"], data


# ------------------------------------------------------------
# Pasta Digital - helpers seleção/iframe/alerta
# ------------------------------------------------------------
def _open_pasta_digital(wait, driver, href, payload, timeout=30):
    """
    Abre a Pasta Digital do ESAJ priorizando o clique em "Visualizar autos"
    (que costuma carregar sessão/token corretamente). Usa href apenas como fallback.
    """
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    old_handles = list(driver.window_handles)

    debug(payload, "PastaDigital: tentando clicar em 'Visualizar autos'…")

    js_click_visualizar = r"""
      const norm = s => (s||'')
        .normalize('NFD').replace(/[\u0300-\u036f]/g,'')
        .replace(/\s+/g,' ').trim().toLowerCase();

      function isVisible(el){
        if(!el) return false;
        const st = window.getComputedStyle(el);
        if(st && (st.visibility==='hidden' || st.display==='none')) return false;
        const r = el.getBoundingClientRect();
        return (r.width > 2 && r.height > 2);
      }

      // candidatos comuns
      const candidates = [];

      // id clássico do link da pasta
      const byId = document.getElementById('linkPasta');
      if (byId) candidates.push(byId);

      // tudo que pode ser "botão"
      candidates.push(...Array.from(document.querySelectorAll(
        "a,button,input[type='button'],input[type='submit'],[role='button']"
      )));

      const wantedA = norm('visualizar autos');
      const wantedB = norm('pasta digital');

      function score(el){
        const t = norm(el.innerText || el.textContent || '');
        const v = norm(el.value || '');
        const a = norm(el.getAttribute('aria-label') || '');
        const ttl = norm(el.title || '');
        const h = norm(el.getAttribute('href') || '');

        let s = 0;
        if (t.includes(wantedA) || v.includes(wantedA) || a.includes(wantedA) || ttl.includes(wantedA)) s += 10;
        if (t.includes(wantedB) || v.includes(wantedB) || a.includes(wantedB) || ttl.includes(wantedB)) s += 6;
        if (h.includes('pastadigital')) s += 5;
        if ((el.id||'') === 'linkPasta') s += 8;
        return s;
      }

      let best = null, bestScore = 0;
      for(const el of candidates){
        if(!isVisible(el)) continue;
        const s = score(el);
        if(s > bestScore){
          bestScore = s;
          best = el;
        }
      }

      if(!best || bestScore < 6) return false;

      try{
        best.scrollIntoView({block:'center', inline:'center'});
      }catch(e){}

      try{
        best.click();
        return true;
      }catch(e){
        try{
          best.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
          return true;
        }catch(e2){}
      }
      return false;
    """

    clicked = False
    try:
        clicked = bool(driver.execute_script(js_click_visualizar))
    except Exception:
        clicked = False

    if not clicked and href:
        debug(payload, "PastaDigital: não achei/clickou 'Visualizar autos'. Usando href como fallback…")
        # tenta abrir como popup/aba (mais parecido com clique)
        try:
            driver.execute_script("window.open(arguments[0], '_blank');", href)
            clicked = True
        except Exception:
            driver.get(href)
            clicked = True

    if not clicked:
        raise TimeoutException("PastaDigital: não consegui abrir (sem clique e sem href).")

    # aguarda: nova aba OU URL/página de pasta digital
    def arrived(_drv):
        try:
            handles = _drv.window_handles
            if len(handles) > len(old_handles):
                _drv.switch_to.window(handles[-1])

            url = (_drv.current_url or "").lower()
            if "pastadigital" in url:
                return True

            # em alguns casos o body vem só com uma URL (redirecionamento “texto”)
            try:
                body = (_drv.find_element(By.TAG_NAME, "body").text or "").strip()
            except Exception:
                body = ""

            if body.startswith("http"):
                _drv.get(body)
                return True

            # ou a pasta digital já está carregando (elementos típicos)
            if _drv.find_elements(By.CSS_SELECTOR, "#divArvore, #arvore_documentos, #divBotoes, #divBotoesInterna"):
                return True

        except Exception:
            return False
        return False

    try:
        wait.until(arrived)
        debug(payload, f"PastaDigital: URL atual {driver.current_url}")
        return True
    except TimeoutException:
        debug(payload, f"PastaDigital: timeout (URL atual: {getattr(driver, 'current_url', None)})")
        return False


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
    """
    Aguarda um novo arquivo PDF aparecer no diretório de download.
    O arquivo não deve ser um .crdownload temporário e deve ter um tamanho > 0.
    """
    end = time.time() + timeout
    while time.time() < end:
        # Encontra todos os arquivos .pdf no diretório
        all_pdfs = list(download_dir.glob("*.pdf"))

        # Filtra por arquivos novos, criados durante esta execução
        new_pdfs = [p for p in all_pdfs if p.name not in before_set]

        if not new_pdfs:
            time.sleep(0.5)
            continue

        # Verifica os arquivos novos para ver se estão completos e com conteúdo
        completed_files = []
        for p in new_pdfs:
            try:
                # Um arquivo é considerado completo se:
                # 1. Existe
                # 2. Tem tamanho maior que 0 bytes
                # 3. Seu arquivo .crdownload correspondente não existe mais
                if p.exists() and p.stat().st_size > 0 and not (download_dir / (p.name + ".crdownload")).exists():
                    completed_files.append(p)
            except (FileNotFoundError, Exception):
                # Ignora erros de arquivos que podem desaparecer durante a verificação
                pass

        if completed_files:
            # Se múltiplos arquivos terminaram, retorna o mais recente
            completed_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            newest_file = completed_files[0]
            if payload:
                debug(payload, f"Download concluído: {newest_file.name} ({newest_file.stat().st_size} bytes)")
            
            # Espera um breve momento para garantir que o navegador liberou o arquivo
            time.sleep(1) 
            return str(newest_file.resolve())

        # Se nenhum arquivo completo foi encontrado ainda, espera e tenta novamente
        time.sleep(0.5)

    if payload:
        debug(payload, f"Timeout: Nenhum PDF novo e completo foi encontrado em {timeout} segundos.")
    return None

# ------------------------------------------------------------
# Baixar PDF (com TURBO + fallback automático + anti-alerta)
# ------------------------------------------------------------
def _baixar_todos_pasta_digital(wait, driver, download_dir, payload, timeout=300, turbo_download=False):
    """
    Versão v12 (Busca Universal):
    - Não depende do nome 'frameDocumento'.
    - Varre a janela principal e TODOS os iframes procurando checkboxes.
    - Se o botão 'Selecionar Todas' falhar, marca os checkboxes manualmente um por um via JS.
    - Usa o 'Link Oculto' para baixar sem travamentos.
    """
    import time, os, shutil
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    
    # Configura caminhos
    target_dir = os.path.abspath(download_dir)
    fallback_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Força CDP
    try:
        driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
            "behavior": "allow", "downloadPath": target_dir, "eventsEnabled": True
        })
    except: pass

    # Identifica Janela Atual
    try: popup_handle = driver.current_window_handle
    except: return []

    def _focar_popup():
        try:
            if driver.current_window_handle != popup_handle:
                driver.switch_to.window(popup_handle)
            return True
        except: return False

    # --- Função Inteligente de Seleção ---
    def _tentar_selecionar_em_qualquer_lugar():
        # 1. Tenta na Janela Principal (Default Content)
        driver.switch_to.default_content()
        
        # Tenta clicar no botão "Selecionar Todas"
        clicou_botao = driver.execute_script("""
            var b = document.getElementById('selecionarButton') || 
                    document.getElementById('btSelecionar') || 
                    document.querySelector('input[title*="Selecionar todas"]');
            if(b) { b.click(); return true; }
            return false;
        """)
        
        # Conta itens
        qtd = driver.execute_script("""
            return document.querySelectorAll('.jstree-checked').length || 
                   document.querySelectorAll('input[type=checkbox]:checked').length;
        """)
        
        if qtd > 0: return qtd

        # 2. Se não achou/selecionou, VARRE TODOS OS IFRAMES
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for i, frame in enumerate(iframes):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                
                # Tenta botão dentro do frame
                if not clicou_botao:
                    driver.execute_script("""
                        var b = document.getElementById('selecionarButton');
                        if(b) b.click();
                    """)
                
                # Tenta marcar checkboxes na força bruta (se o botão falhou)
                driver.execute_script("""
                    var inputs = document.querySelectorAll('input[type=checkbox]');
                    for(var i=0; i<inputs.length; i++) {
                        if(!inputs[i].checked && (inputs[i].id.indexOf('chkDocumento') !== -1 || inputs[i].name.indexOf('chk') !== -1)) {
                            inputs[i].click();
                        }
                    }
                """)
                
                # Conta
                qtd = driver.execute_script("""
                    return document.querySelectorAll('.jstree-checked').length || 
                           document.querySelectorAll('input[type=checkbox]:checked').length;
                """)
                
                if qtd > 0:
                    debug(payload, f"Itens encontrados no Iframe {i}!")
                    return qtd
            except: pass
            
        return 0

    # -----------------------------------------------------------
    debug(payload, "PastaDigital: Iniciando protocolo v12 (Busca Universal)...")
    sucesso_inicio_download = False
    
    for tentativa in range(1, 4):
        if not _focar_popup(): break
        debug(payload, f"PastaDigital: Ciclo {tentativa}/3...")
        
        # A. Seleção (Varredura)
        qtd = 0
        for _ in range(3):
            qtd = _tentar_selecionar_em_qualquer_lugar()
            if qtd > 0: break
            time.sleep(1.5)
            
        debug(payload, f"Itens selecionados: {qtd}")
        
        if qtd == 0: 
            if tentativa < 3: 
                time.sleep(2); continue
            else: 
                # Última tentativa: tenta salvar mesmo sem contagem (vai que é bug visual)
                pass

        # B. Botão Salvar Inicial
        _focar_popup()
        driver.switch_to.default_content()
        driver.execute_script("var b=document.getElementById('btSalvar')||document.getElementById('salvarButton'); if(b) b.click();")
        time.sleep(2)

        # C. Confirmação e Captura do Link
        try:
            # Opção Arquivo Único
            driver.execute_script("var r=document.getElementById('opcao1'); if(r){r.click(); r.checked=true;}")
            
            # Clica em Confirmar/Continuar para gerar o PDF
            driver.execute_script("""
                var btn = document.getElementById('btConfirmar') || document.getElementById('botaoContinuar');
                if(btn && btn.offsetParent) btn.click();
            """)
            
            debug(payload, "Aguardando geração do PDF (Link oculto)...")
            
            # --- Ler o input hidden ---
            url_pdf = None
            for i in range(60): # Espera até 60s
                _focar_popup()
                url_pdf = driver.execute_script("""
                    var input = document.getElementById('urlAcessoArquivo');
                    return (input && input.value && input.value.indexOf('http') !== -1) ? input.value : null;
                """)
                
                if url_pdf:
                    debug(payload, "Link oculto capturado com sucesso!")
                    break
                
                # Fallback: Tenta clicar no botão se ele aparecer
                if i > 5:
                    clicou = driver.execute_script("""
                        var b=document.getElementById('btBaixarDocumento')||document.getElementById('btnDownloadDocumento'); 
                        if(b && !b.disabled && b.offsetParent) { b.click(); return true; }
                        return false;
                    """)
                    if clicou: 
                        debug(payload, "Cliquei no botão visual (fallback).")
                        sucesso_inicio_download = True
                        break
                
                time.sleep(1)
            
            if url_pdf:
                debug(payload, "Baixando via URL direta...")
                driver.get(url_pdf)
                sucesso_inicio_download = True
                break 
                
        except Exception as e:
            debug(payload, f"Erro modal: {e}")

        # Fecha alerta se houver
        try: 
            _focar_popup()
            alert = driver.switch_to.alert
            if "selecione" in alert.text.lower(): 
                debug(payload, "Alerta de seleção vazia. Retentando...")
                alert.accept()
        except: pass

    if not sucesso_inicio_download:
        debug(payload, "PastaDigital: Falha. Não consegui baixar.")
        try: driver.close()
        except: pass
        return []

    # Monitoramento Final
    debug(payload, f"Aguardando arquivo no disco...")
    end = time.time() + timeout
    arquivo_final = None
    
    while time.time() < end:
        pastas = [target_dir, fallback_dir]
        for p in pastas:
            if not os.path.exists(p): continue
            try:
                files = sorted([os.path.join(p, x) for x in os.listdir(p)], key=os.path.getmtime, reverse=True)
                if not files: continue
                cand = files[0]
                
                if (time.time() - os.path.getmtime(cand) < 60):
                    if cand.endswith(".crdownload") or cand.endswith(".tmp"):
                        time.sleep(1); break 
                    
                    if cand.lower().endswith(".pdf") and os.path.getsize(cand) > 100:
                        # Estabilidade
                        s1 = os.path.getsize(cand); time.sleep(1); s2 = os.path.getsize(cand)
                        if s1 == s2:
                            if p == fallback_dir:
                                dest = os.path.join(target_dir, os.path.basename(cand))
                                try: shutil.move(cand, dest); arquivo_final = dest
                                except: arquivo_final = cand
                            else:
                                arquivo_final = cand
                            break
            except: pass
        
        if arquivo_final: break
        time.sleep(1)

    try:
        handles = driver.window_handles
        for h in handles:
            if h != driver.window_handles[0]: 
                driver.switch_to.window(h)
                driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except: pass

    if arquivo_final:
        debug(payload, f"Download Sucesso: {os.path.basename(arquivo_final)}")
        return [str(arquivo_final)]
    
    return []
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
    """
    Versão Linear Estrita:
    1. Coleta todas as URLs da lista primeiro.
    2. Processa uma por uma sequencialmente.
    3. Garante limpeza total de janelas entre um processo e outro.
    """
    import time
    from selenium.webdriver.common.by import By
    
    # 1. Coleta URLs (sem navegar ainda)
    urls_para_processar = []
    try:
        wait.until(EC.presence_of_element_located((By.ID, "listagemDeProcessos")))
        # Pega todos os links visíveis
        links = driver.find_elements(By.CSS_SELECTOR, "#listagemDeProcessos a.linkProcesso")
        for lnk in links:
            url = lnk.get_attribute("href")
            txt = lnk.text.strip()
            # Filtra simples para garantir que é processo
            if url and ("processo.codigo" in url):
                urls_para_processar.append((txt, url))
    except Exception as e:
        debug(payload, f"Erro ao ler lista de processos: {e}")
        return 0

    total = len(urls_para_processar)
    debug(payload, f"Lista: Encontrei {total} processos. Iniciando processamento sequencial...")
    
    sucesso_count = 0
    janela_principal = driver.current_window_handle

    # 2. Loop Sequencial (Um por vez, do início ao fim)
    for i, (proc_nome, proc_url) in enumerate(urls_para_processar):
        debug(payload, f"--- Processando {i+1}/{total}: {proc_nome} ---")
        
        try:
            # A. Navega para o processo (Resetando o estado)
            driver.get(proc_url)
            
            # B. Extrai dados e Valida se é Precatório
            try:
                wait.until(EC.presence_of_element_located((By.ID, "numeroProcesso")))
                nr, data = _extract_details_from_detail_page(driver)
                
                # Se não for precatório, pula (opcional, ajustável conforme sua regra)
                if not data.get("is_precatorio"):
                    debug(payload, f"Ignorando {proc_nome}: Não parece precatório.")
                    continue
                
                payload["results"].append(data)
                payload["has_precatorio"] = True
                if nr and nr not in payload["found_process_numbers"]:
                    payload["found_process_numbers"].append(nr)

            except Exception as e:
                debug(payload, f"Erro ao ler detalhes de {proc_nome}: {e}")
                continue

            # C. Inicia Operação de Download (Pasta Digital)
            if baixar_pdf:
                # 1. Abre a Pasta Digital
                if data.get("link_pasta_digital"):
                    _open_pasta_digital(wait, driver, data["link_pasta_digital"], payload)
                else:
                    _click_visualizar_autos(wait, driver, payload)
                
                # 2. Executa o Download na Janela da Pasta
                # A função _baixar_todos... já cuida de focar na janela certa
                files = _baixar_todos_pasta_digital(
                    wait, driver, Path(download_dir), payload, 
                    timeout=300, turbo_download=turbo_download
                )
                
                if files:
                    payload.setdefault("downloaded_files", []).extend(files)
                    debug(payload, f"Sucesso no download de {proc_nome}")
                else:
                    debug(payload, f"Falha no download de {proc_nome}")

        except Exception as e:
            debug(payload, f"Erro crítico processando {proc_nome}: {e}")

        finally:
            # D. LIMPEZA TOTAL (O Segredo)
            # Fecha todas as janelas exceto a principal para o próximo ciclo começar limpo
            try:
                atuais = driver.window_handles
                for h in atuais:
                    if h != janela_principal:
                        driver.switch_to.window(h)
                        driver.close()
                # Volta o foco para a principal
                driver.switch_to.window(janela_principal)
            except Exception as e:
                debug(payload, f"Erro na limpeza de janelas: {e}")
                # Se perder a principal, tenta recuperar a última
                if driver.window_handles:
                    driver.switch_to.window(driver.window_handles[0])
                    janela_principal = driver.window_handles[0]

        sucesso_count += 1
        # Pequena pausa para o servidor respirar
        time.sleep(2)

    return sucesso_count
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

def _click_visualizar_autos(wait, driver, payload=None, timeout=20):
    import time
    
    debug(payload, "Visualizar Autos: Preparando clique...")
    
    # 1. Memoriza as janelas abertas antes do clique
    janelas_antes = set(driver.window_handles)

    # 2. Tenta encontrar o link/botão
    try:
        # Tenta pelo ID, removendo bloqueios de acessibilidade
        driver.execute_script("""
            var btn = document.getElementById('linkPasta');
            if(btn) {
                btn.removeAttribute('aria-hidden'); 
                btn.style.display = 'block';
                btn.click();
            } else {
                // Fallback para classe se o ID mudar
                var l = document.querySelector('a.linkPasta');
                if(l) l.click();
            }
        """)
        debug(payload, "Visualizar Autos: Clique enviado via JS.")
    except Exception as e:
        debug(payload, f"Erro no clique: {e}")
        return False

    # 3. Monitora o resultado (Nova Janela ou Modal)
    end = time.time() + timeout
    while time.time() < end:
        # A. Verifica se abriu NOVA JANELA (Pop-up)
        janelas_agora = set(driver.window_handles)
        novas = janelas_agora - janelas_antes
        if novas:
            nova_aba = list(novas)[-1]
            driver.switch_to.window(nova_aba)
            debug(payload, f"Visualizar Autos: Sucesso! Nova aba detectada: {driver.current_url}")
            return True

        # B. Verifica se abriu o MODAL de Senha (para quem não está 100% logado)
        try:
            modal_btn = driver.execute_script("""
                var b = document.querySelector('#botaoEnviarSenha, #botaoConfirmar, #popupSenha button');
                if(b && b.offsetParent !== null) { b.click(); return 'clicado'; }
                return null;
            """)
            if modal_btn:
                debug(payload, "Visualizar Autos: Modal de senha detectado e confirmado.")
                time.sleep(2) # Espera o modal processar e abrir a janela
        except: pass

        # C. Verifica se carregou na MESMA aba (redirecionamento)
        if "pastadigital" in (driver.current_url or "").lower():
            debug(payload, "Visualizar Autos: Sucesso! Carregou na mesma aba.")
            return True
            
        time.sleep(0.5)

    debug(payload, "Visualizar Autos: Falha. O pop-up não abriu a tempo (verifique bloqueador de pop-up).")
    return False

def _login_proativo(wait, driver, payload):
    """
    Login 'Pessimista': Assume que precisa logar.
    Aguarda elementos carregarem antes de decidir e monitora a URL.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    import time

    # URL que força o redirecionamento para o login
    URL_LOGIN = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fcpopg%2FabrirConsultaDeRequisitorios.do"
    
    debug(payload, "Login: Acessando tela de autenticação...")
    driver.get(URL_LOGIN)
    
    # 1. Análise do Estado Atual (com espera)
    precisa_logar = False
    try:
        # Espera até 5 segundos para ver se o botão "Identificar-se" aparece
        # Se aparecer, é porque NÃO estamos logados.
        wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Identificar-se")))
        debug(payload, "Login: Botão 'Identificar-se' detectado. Necessário autenticar.")
        precisa_logar = True
    except:
        # Se deu timeout, verificamos se já estamos na URL interna
        # Se a URL ainda tiver 'sajcas', é porque o carregamento está lento, então FORÇAMOS o login
        if "sajcas" in driver.current_url:
            debug(payload, "Login: Ainda na URL de login. Forçando tentativa.")
            precisa_logar = True
        else:
            debug(payload, "Login: Parece que já estamos logados (URL interna).")
            return True

    if not precisa_logar:
        return True

    # 2. Execução do Login (Passo a Passo Lento)
    try:
        # A. Seleciona a aba CERTIFICADO DIGITAL
        debug(payload, "Login: Selecionando aba Certificado...")
        try:
            # Tenta clicar na aba pelo ID ou Link
            aba = wait.until(EC.element_to_be_clickable((By.ID, "aba-certificado")))
            aba.click()
        except:
            # Fallback via JS
            driver.execute_script("var a=document.getElementById('aba-certificado'); if(a) a.click();")
        
        time.sleep(2) # Espera a aba mudar e o componente carregar

        # B. Clica no Botão ENTRAR (submitCertificado)
        debug(payload, "Login: Clicando em 'Entrar'...")
        
        # Garante que o botão está visível
        btn_entrar = wait.until(EC.visibility_of_element_located((By.ID, "submitCertificado")))
        
        # Tenta clicar
        driver.execute_script("arguments[0].click();", btn_entrar)
        
        # 3. Espera a Mágica Acontecer (Certificado do Windows + Redirecionamento)
        # Dá até 30 segundos para o navegador processar o certificado e mudar de página
        debug(payload, "Login: Aguardando redirecionamento do sistema...")
        
        start_wait = time.time()
        sucesso = False
        while time.time() - start_wait < 30:
            # Se a URL não tem mais "sajcas", deu certo!
            if "sajcas" not in driver.current_url:
                debug(payload, "Login: Sucesso! URL mudou (saímos do login).")
                sucesso = True
                break
            
            # Se ainda estiver na página, tenta clicar de novo a cada 5 segundos (caso o clique tenha falhado)
            if int(time.time()) % 5 == 0:
                try:
                    driver.execute_script("var b=document.getElementById('submitCertificado'); if(b) b.click();")
                except: pass
            
            time.sleep(1)

        if sucesso:
            time.sleep(3) # Tempo extra para o cookie firmar
            return True
        else:
            debug(payload, "Login: Alerta - Tempo esgotado e ainda estamos na URL de login.")
            return False

    except Exception as e:
        debug(payload, f"Login: Erro durante o processo: {e}")
        # Tenta seguir mesmo com erro
        return False
# ------------------------------------------------------------
# Fluxo principal
# ------------------------------------------------------------
# Em crawler_full.py

# ... (todo o código anterior permanece o mesmo) ...

# ------------------------------------------------------------
# Fluxo principal
# ------------------------------------------------------------
def go_and_extract(doc_number=None, attach_debugger=False, user_data_dir=None,
                   cert_issuer_cn=None, cert_subject_cn=None,
                   debugger_address=None, cas_usuario=None, cas_senha=None,
                   abrir_autos=False, baixar_pdf=False, download_dir="downloads",
                   process_number=None, turbo_download=False,
                   headless=False):
    
    # Define o rótulo (Processo ou Documento)
    label_input = process_number if process_number else doc_number
    
    # Payload Inicial
    payload = {
        "documento": doc_number, 
        "processo": process_number, 
        "ok": False, 
        "has_precatorio": False,
        "found_process_numbers": [], 
        "results": [], 
        "error": None, 
        "downloaded_files": [],
        "started_at": _now_str(), 
        "finished_at": None
    }
    
    t0 = time.perf_counter()
    driver = None
    baseline_handles = set()

    try:
        # 1. Conecta/Abre o Chrome
        #driver = _build_chrome(attach=attach_debugger, debugger_address=debugger_address, download_dir=download_dir)

        # 1. Conecta/Abre o Chrome
        driver = _build_chrome(
            user_data_dir=user_data_dir,
            cert_issuer_cn=cert_issuer_cn,
            cert_subject_cn=cert_subject_cn,
            attach=attach_debugger,
            debugger_address=debugger_address,
            download_dir=download_dir
        )

        wait = WebDriverWait(driver, 20)

        # Captura abas iniciais para não fechar o que não deve depois
        try: baseline_handles = set(driver.window_handles)
        except: baseline_handles = set()

        # ------------------------------------------------------------------
        # [CRÍTICO] 1. Login Proativo Obrigatório
        # ------------------------------------------------------------------
        # Tenta autenticar antes de qualquer navegação de busca
        if not _login_proativo(wait, driver, payload):
             # Se falhar no login, não adianta prosseguir
             raise Exception("Falha crítica na autenticação inicial (Login/Certificado).")
        
        # Pausa tática para garantir propagação da sessão
        time.sleep(1)

        # ------------------------------------------------------------------
        # 2. Navegação para a Busca
        # ------------------------------------------------------------------
        # Se tiver número de processo, busca direto. Se for documento, usa a URL de DOC.
        base_requisitorios = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
        
        # 2. Navegação para a Busca (SEMPRE REQUISITÓRIOS)
        # Forçamos a URL correta para garantir acesso à Pasta Digital de Precatórios
        base_requisitorios = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"

        if process_number:
             # Se for processo, vamos para a tela de requisitórios limpa
             url_busca = base_requisitorios
        else:
             # Se for documento, já montamos a query string
             url_busca = f"https://esaj.tjsp.jus.br/cpopg/search.do?conversationId=&cbPesquisa=DOCPARTE&dadosConsulta.valorConsulta={doc_number}&consultaDeRequisitorios=true"
        
        driver.get(url_busca)
        # Espera carregamento básico
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        except:
            # Tenta recuperar se caiu em tela de erro
            pass

        # ------------------------------------------------------------------
        # 3. Preenchimento e Força Bruta de Critérios
        # ------------------------------------------------------------------
        if process_number:
            _select_criterio_processo(wait, driver, process_number)
        else:
            # === CORREÇÃO CRÍTICA (DOCPARTE) ===
            try:
                # 1. Espera campo
                inp = wait.until(EC.presence_of_element_located((By.ID, "campo_DOCPARTE")))
                
                # 2. Script para forçar a mudança visual e lógica do combo
                driver.execute_script("""
                    var sel = document.getElementById('cbPesquisa');
                    if(sel) { sel.value = 'DOCPARTE'; sel.dispatchEvent(new Event('change')); }
                    
                    var radio = document.querySelector("input[type='radio'][value='DOCPARTE']");
                    if(radio) radio.click();

                    var divDoc = document.getElementById('DOCPARTE');
                    if(divDoc) { divDoc.style.display = 'block'; divDoc.style.visibility = 'visible'; }
                    
                    var divProc = document.getElementById('NUMPROC');
                    if(divProc) divProc.style.display = 'none';
                """)
                time.sleep(0.5)

                # 3. Preenche valor
                driver.execute_script("arguments[0].value = arguments[1];", inp, doc_number)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", inp)
                
                debug(payload, f"Preenchi DOC e forcei critério DOCPARTE via JS: {doc_number}")
            except Exception as e:
                debug(payload, f"Erro ao preencher campos de busca: {e}")
                # Não dá raise aqui, tenta clicar em consultar mesmo assim (vai que já estava preenchido)

        # ------------------------------------------------------------------
        # 4. Envio do Formulário (Consultar)
        # ------------------------------------------------------------------
        if not _submit_consulta(wait, driver, payload):
            raise TimeoutException("Não consegui clicar no botão 'Consultar'.")
        
        debug(payload, "Consulta enviada.")

        # ------------------------------------------------------------------
        # 5. Análise do Resultado
        # ------------------------------------------------------------------
        kind = _wait_result_page(driver, timeout=60, payload=payload)
        
        # A. Vazio
        if kind == "vazio":
            debug(payload, "Nenhum processo encontrado.")
            payload["ok"] = True
            payload["found_process_numbers"] = []

        # B. Lista de Processos
        elif kind == "lista":
            # Coleta números visuais (Regex)
            import re
            links_texto = []
            try:
                elementos = driver.find_elements(By.TAG_NAME, "a")
                for el in elementos:
                    if el.is_displayed(): links_texto.append(el.text)
            except: pass
            
            regex_cnj = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
            encontrados = set()
            for t in links_texto:
                m = regex_cnj.search(t)
                if m: encontrados.add(m.group(0))
            
            found = list(encontrados)
            debug(payload, f"Resultados (lista): {len(found)} processo(s) identificados visualmente.")
            payload["found_process_numbers"] = found
            
            # === ITERAÇÃO SEQUENCIAL ===
            if abrir_autos:
                # O payload é passado por referência e preenchido dentro da função
                count = _iterar_precatorios_da_lista(wait, driver, baixar_pdf, download_dir, payload, turbo_download=turbo_download)
                debug(payload, f"Fim da iteração. Total de Precatórios processados: {count}")

        # C. Detalhe (Caiu direto num processo único)
        elif kind == "detalhe":
            numero, data = _extract_details_from_detail_page(driver)
            
            if numero:
                payload["results"].append(data)
                payload["found_process_numbers"] = [numero]
                
                if data.get("is_precatorio"):
                    payload["has_precatorio"] = True
                
                if abrir_autos:
                    debug(payload, "Processo único: Tentando abrir autos...")
                    # 1. Tenta abrir Pasta Digital
                    sucesso_abertura = False
                    if data.get("link_pasta_digital"):
                        sucesso_abertura = _open_pasta_digital(wait, driver, data["link_pasta_digital"], payload)
                    
                    if not sucesso_abertura:
                        sucesso_abertura = _click_visualizar_autos(wait, driver, payload, timeout=25)

                    # 2. Se abriu, Baixa
                    if sucesso_abertura and baixar_pdf:
                        try:
                            # Chama a versão v12 (Busca Universal)
                            files = _baixar_todos_pasta_digital(
                                wait, driver, Path(download_dir), payload,
                                timeout=300, turbo_download=turbo_download
                            )
                            if files:
                                payload.setdefault("downloaded_files", []).extend(files)
                        except Exception as e:
                            debug(payload, f"Erro no download único: {e}")
                            payload.setdefault("download_errors", []).append(str(e))
            else:
                raise TimeoutException("Página de detalhe identificada, mas falha ao extrair número.")

        else:
            raise TimeoutException("Estado desconhecido após consulta (nem lista, nem detalhe, nem vazio).")

        # ------------------------------------------------------------------
        # Finalização de Sucesso
        # ------------------------------------------------------------------
        # Screenshot final de controle
        try:
            ts = _ts_str()
            safe = _slug(label_input)
            scr = OUTPUT_DIR / f"screenshot_{safe}_{ts}.png"
            driver.save_screenshot(str(scr))
            payload["screenshot_path"] = str(scr)
        except: pass

        payload["last_url"] = driver.current_url
        payload["ok"] = True
        
        # Cálculo de tempo
        payload["finished_at"] = _now_str()
        elapsed = time.perf_counter() - t0
        payload["duration_seconds"] = round(elapsed, 3)
        payload["duration_hms"] = _fmt_duration(elapsed)
        
        return payload

    except Exception as e:
        # Tratamento de Erro Global
        payload["error"] = f"{e.__class__.__name__}: {e}\n{traceback.format_exc()}"
        try: payload["last_url"] = driver.current_url if driver else None
        except: pass
        
        # Screenshot do Erro
        try:
            ts = _ts_str()
            safe = _slug(label_input)
            if driver:
                p_png = OUTPUT_DIR / f"erro_{safe}_{ts}.png"
                driver.save_screenshot(str(p_png))
                payload["error_screenshot_path"] = str(p_png)
        except: pass
        
        payload["finished_at"] = _now_str()
        elapsed = time.perf_counter() - t0
        payload["duration_seconds"] = round(elapsed, 3)
        payload["duration_hms"] = _fmt_duration(elapsed)
        return payload

    finally:
        # Limpeza Final
        try:
            if driver:
                # Fecha abas extras criadas durante a execução
                _close_extra_tabs(driver, baseline_handles, payload)
                
                # Se não for debug, fecha o navegador
                if not attach_debugger and not debugger_address:
                    driver.quit()
        except: pass


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
            attach_debugger=args.attach,
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
            attach_debugger=args.attach,
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
