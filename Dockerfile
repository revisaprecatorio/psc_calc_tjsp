# Dockerfile para rodar o WORKER (orchestrator_subprocess.py)
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Sao_Paulo

# CORRIGIDO: Instala Google Chrome (não Chromium) para evitar bug de user-data-dir
# Chromium do Debian tem problema conhecido com Docker
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg2 unzip fonts-liberation \
    libnss3-tools openssl \
    libnss3 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libgbm1 libx11-xcb1 \
  && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
  && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
  && apt-get update \
  && apt-get install -y google-chrome-stable \
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