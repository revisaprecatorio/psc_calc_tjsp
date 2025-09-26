#!/bin/bash
set -e

# diretório do banco NSS (Chrome/Chromium usa aqui os certificados)
NSSDB_DIR="$HOME/.pki/nssdb"
CERT_FILE="/app/certs/cert.pfx"

mkdir -p "$NSSDB_DIR"

# cria o banco NSS se não existir
if [ ! -f "$NSSDB_DIR/cert9.db" ]; then
  certutil -N --empty-password -d sql:$NSSDB_DIR
fi

# importa certificado A1 (.pfx) se existir
if [ -f "$CERT_FILE" ]; then
  echo "[INFO] Importando certificado $CERT_FILE no NSS..."
  pk12util -i "$CERT_FILE" -d sql:$NSSDB_DIR -W "$CERT_PASS"
else
  echo "[WARN] Nenhum certificado encontrado em $CERT_FILE"
fi

echo "[INFO] Iniciando uvicorn..."
exec uvicorn app:app --host 0.0.0.0 --port 8000
