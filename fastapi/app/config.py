from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, AmqpDsn
from typing import Optional
import os

class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: PostgresDsn = Field(
        default=os.getenv("DATABASE_URL"),
        env="DATABASE_URL",
        example="postgresql://user:password@localhost:5432/db"
    )
    
    # Настройки Celery/RabbitMQ
    CELERY_BROKER_URL: AmqpDsn = Field(
        default=os.getenv("CELERY_BROKER_URL"),
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
        env="CELERY_RESULT_BACKEND"
    )
    
    # Настройки файловой системы
    UPLOAD_DIR: str = Field(
        default=os.getenv("UPLOAD_DIR", "/uploads"),
        env="UPLOAD_DIR"
    )
    
    # Настройки RabbitMQ
    RABBITMQ_HOST: str = Field(
        default=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        env="RABBITMQ_HOST"
    )
    RABBITMQ_PORT: int = Field(
        default=int(os.getenv("RABBITMQ_PORT", 5673)),
        env="RABBITMQ_PORT"
    )
    RABBITMQ_USER: str = Field(
        default=os.getenv("RABBITMQ_USER", "rabbitmq_user"),
        env="RABBITMQ_USER"
    )
    RABBITMQ_PASSWORD: str = Field(
        default=os.getenv("RABBITMQ_PASSWORD", "doc_rabbit_pass_2025"),
        env="RABBITMQ_PASSWORD"
    )
    RABBITMQ_VHOST: str = Field(
        default=os.getenv("RABBITMQ_VHOST", "/"),
        env="RABBITMQ_VHOST"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
