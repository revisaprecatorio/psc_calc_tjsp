# Dockerfile para rodar o WORKER (orchestrator_subprocess.py)
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Sao_Paulo \
    CHROME_BIN=/usr/bin/chromium

# Instala dependências do sistema + chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg2 unzip fonts-liberation \
    libnss3-tools openssl chromium \
    libnss3 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libgbm1 libx11-xcb1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o código da aplicação
COPY . /app/

# --- MUDANÇAS AQUI ---
# 1. A linha EXPOSE 8000 foi removida, pois não é um servidor web.
# 2. O ENTRYPOINT agora chama o script python diretamente.
#    As linhas que copiavam e davam permissão ao entrypoint.sh foram removidas.

ENTRYPOINT ["python", "orchestrator_subprocess.py"]