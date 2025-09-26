# Dockerfile (Chrome oficial + Selenium Manager)
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Sao_Paulo \
    CHROME_BIN=/usr/bin/chromium

# instalar dependências do sistema + chromium + ferramentas de certificados
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg2 unzip fonts-liberation \
    libnss3-tools openssl chromium \
    libnss3 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libgbm1 libx11-xcb1 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# instalar dependências python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copiar código e entrypoint
COPY . /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]