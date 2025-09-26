# -*- coding: utf-8 -*-
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Body, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# importa seu crawler ORIGINAL
from crawler_full import go_and_extract, PROCESSO_REGEX  # mantém seu código original

app = FastAPI(title="TJSP Requisitórios API", version="1.1.0", docs_url="/docs", redoc_url="/redoc")

# CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    doc: str = Field(..., description="CPF/CNPJ (só dígitos) ou número CNJ completo")
    attach: bool = False
    user_data_dir: Optional[str] = None
    cert_issuer_cn: Optional[str] = None
    cert_subject_cn: Optional[str] = None
    debugger_address: Optional[str] = None
    cas_usuario: Optional[str] = None
    cas_senha: Optional[str] = None
    abrir_autos: bool = False
    baixar_pdf: bool = False
    turbo_download: bool = False
    download_dir: str = "downloads"
    headless: bool = False  # <— NOVO

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/crawl")
def crawl(body: CrawlRequest = Body(...)):
    raw = body.doc or ""
    is_cnj = bool(PROCESSO_REGEX.search(raw)) or (sum(ch.isdigit() for ch in raw) >= 17)

    Path(body.download_dir).mkdir(parents=True, exist_ok=True)

    if is_cnj:
        res = go_and_extract(
            doc_number=None,
            process_number=raw,
            attach=body.attach,
            user_data_dir=body.user_data_dir,
            cert_issuer_cn=body.cert_issuer_cn,
            cert_subject_cn=body.cert_subject_cn,
            debugger_address=body.debugger_address,
            cas_usuario=body.cas_usuario,
            cas_senha=body.cas_senha,
            abrir_autos=body.abrir_autos,
            baixar_pdf=body.baixar_pdf,
            download_dir=body.download_dir,
            turbo_download=body.turbo_download,
            headless=body.headless,  # <— NOVO
        )
    else:
        only_digits = "".join(ch for ch in raw if ch.isdigit())
        if not only_digits:
            return {"documento": raw, "ok": False, "error": "Documento inválido"}
        res = go_and_extract(
            doc_number=only_digits,
            process_number=None,
            attach=body.attach,
            user_data_dir=body.user_data_dir,
            cert_issuer_cn=body.cert_issuer_cn,
            cert_subject_cn=body.cert_subject_cn,
            debugger_address=body.debugger_address,
            cas_usuario=body.cas_usuario,
            cas_senha=body.cas_senha,
            abrir_autos=body.abrir_autos,
            baixar_pdf=body.baixar_pdf,
            download_dir=body.download_dir,
            turbo_download=body.turbo_download,
            headless=body.headless,  # <— NOVO
        )
    return res

@app.get("/crawl")
def crawl_get(
    doc: str = Query(..., description="CPF/CNPJ ou CNJ completo"),
    attach: bool = False,
    user_data_dir: Optional[str] = None,
    cert_issuer_cn: Optional[str] = None,
    cert_subject_cn: Optional[str] = None,
    debugger_address: Optional[str] = None,
    cas_usuario: Optional[str] = None,
    cas_senha: Optional[str] = None,
    abrir_autos: bool = False,
    baixar_pdf: bool = False,
    turbo_download: bool = False,
    download_dir: str = "downloads",
    headless: bool = False,  # <— NOVO
):
    body = CrawlRequest(
        doc=doc,
        attach=attach,
        user_data_dir=user_data_dir,
        cert_issuer_cn=cert_issuer_cn,
        cert_subject_cn=cert_subject_cn,
        debugger_address=debugger_address,
        cas_usuario=cas_usuario,
        cas_senha=cas_senha,
        abrir_autos=abrir_autos,
        baixar_pdf=baixar_pdf,
        turbo_download=turbo_download,
        download_dir=download_dir,
        headless=headless,  # <— NOVO
    )
    return crawl(body)
