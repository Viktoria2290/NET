FROM python:3.12-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    libpng-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8081
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "--log-file", "/NET/logs/gunicorn.log", "--workers", "3", "docmagic_core.wsgi:application"]
