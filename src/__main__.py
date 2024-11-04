"""
Модуль: __main__

Точка входа для запуска приложения FastAPI.
Настраиваем логирование и
подключаем маршрутизаторы, используемые в приложении.
"""

from fastapi import FastAPI
from routers.clients import router as users_router
from config.logging import setup_logging
from exceptions.error_handlers import register_error_handlers

setup_logging()

app = FastAPI()

app.include_router(users_router, prefix="/api/clients")
# app.include_router(matches_router, prefix="/api/clients")
# app.include_router(listings_router, prefix="/api")

register_error_handlers(app)