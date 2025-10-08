# psc_calc.py
# -*- coding: utf-8 -*-
import sys
import re
import time
import json
import argparse
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional
from contextlib import contextmanager
from time import perf_counter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://psc.precatoriosemcomplicacao.com.br/PSCWeb/Login"
CALC_URL  = "https://psc.precatoriosemcomplicacao.com.br/PSCWeb/AtualizacaoCalculos"

import unicodedata

# ===================== Utils de texto/moeda =====================
def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn")

def parse_currency_pt(text: str) -> float:
    """Extrai o primeiro número moeda pt-BR encontrado e converte para float."""
    m = re.compile(r"[-+]?\d{1,3}(?:\.\d{3})*,\d{2}").search(text or "")
    if not m:
        return 0.0
    s = m.group(0).replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0

def normalize_brl_input(s: Optional[str]) -> Optional[str]:
    """Converte '80.000,00' / '80000,00' / '80000' para '80000,00'."""
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return s
    s = s.replace(".", "").replace(" ", "")
    if "," not in s:
        if s.isdigit():
            s = s + ",00"
    else:
        parte_int, parte_dec = s.split(",", 1)
        parte_dec = (parte_dec + "00")[:2]
        s = parte_int + "," + parte_dec
    return s

# ===================== Logging & stages =====================
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )

@contextmanager
def stage(name: str):
    t0 = perf_counter()
    logging.info(f"[START] {name}")
    try:
        yield
        logging.info(f"[DONE ] {name} | {perf_counter()-t0:.3f}s")
    except Exception:
        logging.exception(f"[FAIL ] {name} | {perf_counter()-t0:.3f}s")
        raise

# ===================== Selenium helpers =====================
def wait_any_present(driver, candidates, timeout: int):
    last = None
    end = time.time() + timeout
    while time.time() < end:
        for by, sel in candidates:
            try:
                els = driver.find_elements(by, sel)
                if els:
                    return els[0]
            except Exception as e:
                last = e
        time.sleep(0.15)
    raise last or TimeoutException("Elemento não encontrado.")

def wait_any_clickable(driver, candidates, timeout: int):
    last = None
    end = time.time() + timeout
    while time.time() < end:
        for by, sel in candidates:
            try:
                els = driver.find_elements(by, sel)
                for el in els:
                    if el.is_displayed() and el.is_enabled():
                        return el
            except Exception as e:
                last = e
        time.sleep(0.15)
    raise last or TimeoutException("Elemento clicável não encontrado.")

def js_set_value(driver, el, value: str):
    driver.execute_script("""
        const el = arguments[0], val = arguments[1];
        const proto = Object.getPrototypeOf(el);
        const desc  = Object.getOwnPropertyDescriptor(proto, 'value')
                    || Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
        if (desc && desc.set) { desc.set.call(el, val); } else { el.value = val; }
        el.dispatchEvent(new Event('input',  { bubbles:true, cancelable:true }));
        el.dispatchEvent(new Event('change', { bubbles:true, cancelable:true }));
        el.dispatchEvent(new KeyboardEvent('keydown', { bubbles:true, key:'Tab' }));
        el.dispatchEvent(new KeyboardEvent('keyup',   { bubbles:true, key:'Tab' }));
        el.dispatchEvent(new Event('blur',   { bubbles:true }));
    """, el, value)

def safe_type(driver, el, value: str, blur: bool=True):
    try: driver.execute_script("try{arguments[0].focus();}catch(e){}", el)
    except Exception: pass
    try: el.clear()
    except Exception: pass

    js_set_value(driver, el, value)
    time.sleep(0.05)

    try: got = (el.get_attribute("value") or "").strip()
    except Exception: got = ""

    if not got:
        try: el.click()
        except Exception: pass
        try: el.send_keys(value)
        except Exception:
            driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", el, value)

    if blur:
        try: driver.execute_script("try{arguments[0].blur();}catch(e){}", el)
        except Exception:
            try: el.send_keys("\t")
            except Exception: pass
    time.sleep(0.1)

def scroll_into_view(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

def build_driver(headless=False) -> webdriver.Chrome:
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    if headless:
        opts.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

# ===================== Select helpers & checks =====================
from selenium.webdriver.support.ui import Select

def select_by_text_or_value(sel_element, target_text: str, value_map: dict) -> bool:
    sel = Select(sel_element)
    if target_text in value_map:
        try:
            sel.select_by_value(value_map[target_text]); return True
        except Exception:
            pass
    try:
        sel.select_by_visible_text(target_text); return True
    except Exception:
        norm = target_text.strip().lower()
        for opt in sel.options:
            if opt.text.strip().lower() == norm:
                sel.select_by_visible_text(opt.text); return True
    return False

def assert_selected_text(sel_element, expected_text: str):
    sel = Select(sel_element)
    try:
        txt = sel.first_selected_option.text.strip()
    except Exception:
        raise RuntimeError("Não consegui ler a opção selecionada")
    if txt.lower() != expected_text.strip().lower():
        raise RuntimeError(f"Select não confirmou valor. Esperado='{expected_text}' | Atual='{txt}'")

def wait_calculate_enabled(driver, btn, timeout_sec: int = 10):
    end = time.time() + timeout_sec
    while time.time() < end:
        try:
            disabled_attr = btn.get_attribute("disabled")
            aria_disabled = btn.get_attribute("aria-disabled")
            if (not disabled_attr) and (not aria_disabled or aria_disabled == "false"):
                return True
        except Exception:
            pass
        time.sleep(0.2)
    raise TimeoutException("Botão CALCULAR não habilitou dentro do timeout.")

# ===================== Locators =====================
@dataclass
class LoginLocators:
    email = [(By.CSS_SELECTOR,"input[type='email']"),
             (By.CSS_SELECTOR,"input[name='email']"),
             (By.CSS_SELECTOR,"input[placeholder*='E-mail']"),
             (By.CSS_SELECTOR,"input[placeholder*='CPF']"),
             (By.XPATH,"//label[contains(.,'E-mail') or contains(.,'CPF')]/following::input[1]"),
             (By.CSS_SELECTOR,"input[type='text']")]
    password = [(By.CSS_SELECTOR,"input[type='password']"),
                (By.CSS_SELECTOR,"input[name='password']"),
                (By.XPATH,"//label[contains(.,'Senha')]/following::input[@type='password'][1]")]
    submit = [(By.CSS_SELECTOR,"button[type='submit']"),
              (By.XPATH,"//button[contains(.,'ENTRAR') or contains(.,'Entrar')]"),
              (By.XPATH,"//form//button")]

@dataclass
class CalcLocators:
    numero_precatorio = [
        (By.CSS_SELECTOR,"input[id$='Input_NumeroPrecatorio']"),
        (By.XPATH,"//label[contains(.,'Nº Precatório')]/following::input[1]"),
    ]
    tipo_select = [
        (By.CSS_SELECTOR,"select[id$='DropdownTipo']"),
        (By.XPATH,"//label[contains(.,'Tipo')]/following::select[1]"),
    ]
    ano_venc = [
        (By.CSS_SELECTOR,"input[id$='AnodeVencimento']"),
        (By.XPATH,"//label[contains(.,'Ano de Vencimento')]/following::input[1]"),
    ]
    data_ult_liquid = [
        (By.CSS_SELECTOR,"input[id$='Input_DataUltimaLiquidacao']"),
        (By.XPATH,"//label[contains(.,'Data Última Liquidação')]/following::input[1]"),
    ]
    valor_precatorio = [
        (By.CSS_SELECTOR,"input[id$='ValorPrecatorio']"),
        (By.XPATH,"//label[contains(.,'Valor do Precatório')]/following::input[1]"),
    ]
    principal = [
        (By.CSS_SELECTOR,"input[id$='Principal']"),
        (By.XPATH,"//label[contains(.,'Principal')]/following::input[1]"),
    ]
    juros_mora = [
        (By.CSS_SELECTOR,"input[id$='JurosMora']"),
        (By.XPATH,"//label[contains(.,'Juros de Mora')]/following::input[1]"),
    ]
    indice_sentenca_select = [
        (By.CSS_SELECTOR,"select[id$='DropdownIndiceUsadoSentenca']"),
        (By.XPATH,"//label[contains(.,'Índice usado na Sentença')]/following::select[1]"),
    ]
    incide_ir_select = [
        (By.CSS_SELECTOR,"select[id$='DropdownIncideIR']"),
        (By.XPATH,"//label[contains(.,'Incide IR')]/following::select[1]"),
    ]
    calcular_btn = [
        (By.XPATH,"//button[.//span[contains(.,'Calcular')]]"),
        (By.XPATH,"//span[contains(.,'Calcular')]/ancestor::button[1]"),
    ]
    resultado_block_candidates = [
        (By.CSS_SELECTOR,"fieldset[id$='CalculosFinal']"),
        (By.XPATH,"//*[contains(@id,'CalculosFinal')]"),
    ]

# ===================== Maps =====================
TIPO_MAP = {"Alimentar":"0", "Comum":"1"}
INDICE_MAP = {"TR":"0", "IPCA-E":"1", "SELIC":"2", "INPC":"3", "Poupança":"4"}
INCIDE_IR_MAP = {"Não":"0", "RRA":"1", "Tabela Progressiva":"2", "Justiça Federal":"3"}

def to_iso_date(s: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s): return s
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        d, mth, y = m.group(1), m.group(2), m.group(3)
        return f"{y}-{mth}-{d}"
    return s

# ===================== Busca de valores por label =====================
def find_currency_after_label(driver, label_text: str) -> float:
    """
    Encontra o label (case/acento-insensitive) e pega o PRIMEIRO número-moeda no elemento
    seguinte útil (td/span/div/strong). Funciona bem com o HTML da calculadora PSC.
    """
    label_norm = strip_accents(label_text).lower()
    xpath = (
        "//*[contains(translate(normalize-space(.),"
        " 'ÁÂÃÀÉÊÍÓÔÕÚÇáâãàéêíóôõúç', 'AAAAEEIOOOUCaaaaeeiooouc'),"
        f" '{label_norm}')]"
        "/following::*[self::td or self::span or self::div or self::strong][1]"
    )
    try:
        el = driver.find_element(By.XPATH, xpath)
        v = parse_currency_pt((el.text or "").strip())
        # aceita zero também
        if v or v == 0.0:
            return v
    except Exception:
        pass

    # Fallback: procurar no HTML bruto numa janela após o label
    try:
        html = driver.page_source
        idx = strip_accents(html).lower().find(label_norm)
        trecho = html[idx: idx+400] if idx != -1 else ""
        v = parse_currency_pt(trecho)
        if v or v == 0.0:
            return v
    except Exception:
        pass
    return 0.0

def find_first_by_labels(driver, labels: List[str]) -> float:
    """Tenta várias variações de rótulo."""
    for i, lab in enumerate(labels):
        v = find_currency_after_label(driver, lab)
        if v or v == 0.0 or i == len(labels) - 1:
            return v
    return 0.0

# ===================== Snap & helpers (screenshots desativados) =====================
def _ts(): return time.strftime("%Y%m%d_%H%M%S")
def take_snap(driver, out_dir: Path, name: str): return  # no-op
def _first_present(driver, candidates: List[Tuple[By, str]]):
    for by, sel in candidates:
        els = driver.find_elements(by, sel)
        if els: return els[0]
    return None

# ===================== Fluxo =====================
def do_login(driver, email, senha, timeout, debug_dir: Path, debug_screens: bool):
    with stage("Login / abrir"):
        driver.get(LOGIN_URL)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
    with stage("Login / preencher"):
        e = wait_any_present(driver, LoginLocators.email, timeout)
        p = wait_any_present(driver, LoginLocators.password, timeout)
        safe_type(driver, e, email, blur=False)
        safe_type(driver, p, senha, blur=False)
    with stage("Login / submeter"):
        btn = wait_any_clickable(driver, LoginLocators.submit, timeout)
        btn.click()
        WebDriverWait(driver, timeout).until(lambda d: "/Login" not in d.current_url)

def fill_calc(driver,
              numero_precatorio: Optional[str],
              tipo: Optional[str],
              ano_venc: Optional[str],
              data_ult_liquid: Optional[str],
              valor_precatorio: Optional[str],
              principal: Optional[str],
              juros_mora: Optional[str],
              indice: Optional[str],
              incide_ir: Optional[str],
              timeout: int,
              debug_dir: Path,
              debug_screens: bool):
    with stage("Calculadora / abrir"):
        driver.get(CALC_URL)
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        time.sleep(0.4)

    def fill_if(value, locs, label, transform=lambda x:x):
        if value is None:
            logging.info(f"[skip] {label}")
            return
        el = wait_any_present(driver, locs, timeout)
        scroll_into_view(driver, el)
        safe_type(driver, el, transform(value))
        logging.info(f"[fill] {label}: {value}")

    fill_if(numero_precatorio, CalcLocators.numero_precatorio, "Nº Precatório")

    if tipo:
        with stage("Calculadora / selecionar Tipo"):
            sel_el = wait_any_present(driver, CalcLocors.tipo_select, timeout) if False else wait_any_present(driver, CalcLocators.tipo_select, timeout)
            scroll_into_view(driver, sel_el)
            ok = select_by_text_or_value(sel_el, tipo, TIPO_MAP)
            if not ok: raise RuntimeError(f"Falha ao selecionar Tipo='{tipo}'")
            assert_selected_text(sel_el, tipo)

    fill_if(ano_venc, CalcLocators.ano_venc, "Ano de Vencimento")
    fill_if(data_ult_liquid, CalcLocators.data_ult_liquid, "Data Última Liquidação", transform=to_iso_date)
    fill_if(normalize_brl_input(valor_precatorio), CalcLocators.valor_precatorio, "Valor do Precatório")
    fill_if(normalize_brl_input(principal),        CalcLocators.principal,        "Principal")
    fill_if(normalize_brl_input(juros_mora),       CalcLocators.juros_mora,       "Juros de Mora")

    if indice:
        with stage("Calculadora / selecionar Índice na Sentença"):
            sel_el = wait_any_present(driver, CalcLocators.indice_sentenca_select, timeout)
            scroll_into_view(driver, sel_el)
            ok = select_by_text_or_value(sel_el, indice, INDICE_MAP)
            if not ok: raise RuntimeError(f"Falha ao selecionar Índice usado na Sentença='{indice}'")
            assert_selected_text(sel_el, indice)

    if incide_ir:
        with stage("Calculadora / selecionar Incide IR"):
            sel_el = wait_any_present(driver, CalcLocators.incide_ir_select, timeout)
            scroll_into_view(driver, sel_el)
            ok = select_by_text_or_value(sel_el, incide_ir, INCIDE_IR_MAP)
            if not ok: raise RuntimeError(f"Falha ao selecionar Incide IR='{incide_ir}'")
            assert_selected_text(sel_el, incide_ir)

    with stage("Calculadora / clicar Calcular"):
        btn = wait_any_clickable(driver, CalcLocators.calcular_btn, timeout)
        scroll_into_view(driver, btn)
        wait_calculate_enabled(driver, btn, timeout_sec=10)
        time.sleep(0.2)
        btn.click()

def wait_and_capture_result(driver, timeout_calc: int, out_dir: Path, debug_screens: bool, valor_precatorio_cli: Optional[str]):
    texto = ""
    with stage("Calculadora / aguardar resultado"):
        block = WebDriverWait(driver, timeout_calc).until(
            lambda d: _first_present(d, CalcLocators.resultado_block_candidates)
        )
        scroll_into_view(driver, block)
        time.sleep(0.3)
        try: texto = (block.text or "").strip()
        except Exception: texto = ""
        logging.info(f"[info] len(texto_resultado)={len(texto)}")

    # ===== Captura dos campos solicitados =====
    # As variações de rótulo cobrem exatamente o que aparece no HTML das suas capturas.
    valor_bruto_precatorio = find_first_by_labels(driver, ["Valor Bruto", "Valor Bruto Precatório", "Valor Bruto Precatorio"])
    base_calculo_liquida    = find_first_by_labels(driver, ["Base de Cálculo Líquida", "Base de Calculo Liquida"])
    ir_calculado            = find_first_by_labels(driver, ["IR Calculado", "IR calculado"])
    prev_fgts_assist        = find_first_by_labels(driver, ["FGTS + Assistência", "FGTS + Assist.", "Prev. FGTS+Assist.", "FGTS + Assistencia"])
    valor_liquido_cedivel   = find_first_by_labels(driver, ["Valor Líquido Cedível", "Valor Liquido Cedivel"])

    # Fallback direto no texto visível (inclusive para zeros)
    def fallback(lbl: str, current: float) -> float:
        if current or current == 0.0:
            return current
        idx = strip_accents(texto).lower().find(strip_accents(lbl).lower())
        trecho = texto[idx: idx+160] if idx != -1 else ""
        v = parse_currency_pt(trecho)
        return v if (v or v == 0.0) else current

    valor_bruto_precatorio = fallback("Valor Bruto", valor_bruto_precatorio)
    valor_bruto_precatorio = fallback("Valor Bruto Precatório", valor_bruto_precatorio)
    base_calculo_liquida   = fallback("Base de Cálculo Líquida", base_calculo_liquida)
    ir_calculado           = fallback("IR Calculado", ir_calculado)
    prev_fgts_assist       = fallback("FGTS + Assistência", prev_fgts_assist)
    valor_liquido_cedivel  = fallback("Valor Líquido Cedível", valor_liquido_cedivel)

    # Sanity simples: VLC não pode explodir 20x o valor informado
    try:
        vp_cli_norm = normalize_brl_input(valor_precatorio_cli) if valor_precatorio_cli else None
        vp_float = parse_currency_pt(vp_cli_norm) if vp_cli_norm else 0.0
        if vp_float > 0 and valor_liquido_cedivel > vp_float * 20:
            raise RuntimeError(
                f"Sanity check falhou: VLC ({valor_liquido_cedivel:,.2f}) >> Valor do Precatório ({vp_float:,.2f})."
            )
    except Exception as sc_err:
        logging.error(str(sc_err))
        raise

    # ===== Persistência (SOMENTE JSON) =====
    payload = {
        "when": _ts(),
        "url": driver.current_url,
        "texto_len": len(texto),
        "preview": (texto[:800] + "..." if len(texto) > 800 else texto),

        # --- Campos solicitados ---
        "valor_bruto_precatorio": valor_bruto_precatorio,
        "base_calculo_liquida": base_calculo_liquida,
        "ir_calculado": ir_calculado,
        "prev_fgts_assist": prev_fgts_assist,
        "valor_liquido_cedivel": valor_liquido_cedivel,

        # útil para auditoria
        "valor_precatorio_cli": valor_precatorio_cli,
    }
    json_path = out_dir / f"resultado_calc_{_ts()}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logging.info(f"[SAVE] {json_path}")

# ===================== CLI =====================
def get_parser():
    p = argparse.ArgumentParser(description="PSC - login, calculadora e coleta de resultado (JSON-only).")
    p.add_argument("--email", required=True)
    p.add_argument("--senha", required=True)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--timeout-calc", type=int, default=60)
    p.add_argument("--debug-screens", action="store_true")
    p.add_argument("--out-dir", default="out")

    # Campos obrigatórios
    p.add_argument("--numero-precatorio", required=True)
    p.add_argument("--tipo", choices=["Alimentar","Comum"], required=True)
    p.add_argument("--ano-venc", required=True)
    p.add_argument("--data-ult-liquid", required=True)
    p.add_argument("--valor-precatorio", required=True)
    p.add_argument("--principal", required=True)
    p.add_argument("--juros-mora", required=True)
    p.add_argument("--indice", choices=["TR","IPCA-E","SELIC","INPC","Poupança"], required=True)
    p.add_argument("--incide-ir", choices=["Não","RRA","Tabela Progressiva","Justiça Federal"], required=True)
    return p

def main():
    setup_logging()
    args = get_parser().parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    valor_precatorio_cli = args.valor_precatorio
    args.debug_screens = False  # garante zero screenshots

    driver = build_driver(headless=args.headless)
    try:
        do_login(driver, args.email, args.senha, args.timeout, out_dir, args.debug_screens)
        fill_calc(driver,
                  numero_precatorio=args.numero_precatorio,
                  tipo=args.tipo,
                  ano_venc=args.ano_venc,
                  data_ult_liquid=args.data_ult_liquid,
                  valor_precatorio=args.valor_precatorio,
                  principal=args.principal,
                  juros_mora=args.juros_mora,
                  indice=args.indice,
                  incide_ir=args.incide_ir,
                  timeout=args.timeout,
                  debug_dir=out_dir,
                  debug_screens=args.debug_screens)
        wait_and_capture_result(driver, args.timeout_calc, out_dir, args.debug_screens, valor_precatorio_cli)
        logging.info("[OK] Fluxo concluído.")
    except Exception as e:
        logging.exception("[FATAL] Erro no fluxo.")
        try:
            err_json = {
                "when": _ts(),
                "stage": "fatal",
                "error": str(e),
                "current_url": None
            }
            try:
                err_json["current_url"] = driver.current_url
            except Exception:
                pass
            err_path = out_dir / f"zz_error_{_ts()}.json"
            with open(err_path, "w", encoding="utf-8") as f:
                json.dump(err_json, f, ensure_ascii=False, indent=2)
            logging.info(f"[SAVE] {err_path}")
        except Exception:
            pass
        sys.exit(1)
    finally:
        if args.headless:
            driver.quit()

if __name__ == "__main__":
    main()
