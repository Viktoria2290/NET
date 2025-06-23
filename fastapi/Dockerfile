FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    sqlalchemy==2.0.31 \
    psycopg2-binary==2.9.9 \
    alembic==1.13.2

# Копируем исходный код
COPY . .

# Создаем рабочие директории
RUN mkdir -p /uploads && chmod 777 /uploads && \
    mkdir -p /var/log/fastapi

# Инициализация Alembic (если нужно)
RUN if [ "$INIT_ALEMBIC" = "true" ]; then \
      alembic upgrade head; \
    fi

EXPOSE 8080

# Запуск приложения
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8080"]
