FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias necesarias para pandas y BigQuery
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libc6-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
