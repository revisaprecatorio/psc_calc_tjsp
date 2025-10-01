# Dockerfile para rodar o WORKER (orchestrator_subprocess.py)
# SIMPLIFICADO: Não instala Chrome - usa Selenium Grid
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Sao_Paulo

# SIMPLIFICADO: Apenas dependências básicas
# Chrome roda no container Selenium Grid separado
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o código da aplicação
COPY . /app/

# Worker se conecta ao Selenium Grid via SELENIUM_REMOTE_URL
# Definido no docker-compose.yml
ENTRYPOINT ["python", "orchestrator_subprocess.py"]