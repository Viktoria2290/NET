FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8082
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--log-file", "/NET/logs/gunicorn_djangorest.log", "--workers", "3", "proxy.wsgi:application"]
