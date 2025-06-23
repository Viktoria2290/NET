FROM python:3.12-slim

# Установка Tesseract и зависимостей
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запуск Flask-сервера
CMD ["python", "server.py"]
