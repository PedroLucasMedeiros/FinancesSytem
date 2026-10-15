FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala os requisitos da raiz
COPY ambient/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o container
COPY . /app