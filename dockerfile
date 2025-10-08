## 🐳 **Dockerfile**


# ================================================================
# Dockerfile - PSC Calculadora Automática
# ================================================================
FROM python:3.12-slim-bookworm

# Evita prompts interativos e ativa logs não bufferizados
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instala dependências do sistema e do Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg unzip fonts-liberation \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 \
    libc6 libcairo2 libcups2 libdbus-1-3 libdrm2 libgbm1 \
    libgtk-3-0 libnspr4 libnss3 libx11-6 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
    libxshmfence1 libu2f-udev xdg-utils \
 && rm -rf /var/lib/apt/lists/*

# Instala Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script principal
COPY psc_calc.py .

# Cria diretório de saída
RUN mkdir -p /app/out

# Comando padrão
CMD ["python", "psc_calc.py", "--help"]
