# Dockerfile

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para pandas y BigQuery
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de la app
COPY . /app

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurar puerto por defecto para Flask
ENV PORT=8080

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "main.py"]
