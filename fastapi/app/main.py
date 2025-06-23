from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.database import Base, engine
import logging
import os

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Настройка логгирования
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/fastapi.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Document Processing API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(routes.router, prefix="/api/v1")
