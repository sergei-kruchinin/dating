"""
Модуль: config.settings

Модуль для управления конфигурацией приложения. Здесь загружаются переменные окружения
и задаются значения по умолчанию для ключевых параметров.

Обрабатываемые параметры:
- URL базы данных
- секретный ключ для генерации JWT-токенов
- каталог для хранения изображений аватаров
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_base_dir():
    """
    Возвращает базовый каталог проекта.

    Определяет путь до корневого каталога проекта,
    относительно местоположения текущего файла.

    Служит, если параметр не задан.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
    return base_dir


# DATABASE_URL
default_database_url = 'sqlite+aiosqlite:///' + os.path.join(get_base_dir(), 'database.db')
DATABASE_URL = os.getenv('DATABASE_URL', default_database_url)
if DATABASE_URL == default_database_url:
    logger.warning("DATABASE_URL не задан в переменных окружения. Используется значение по умолчанию.")

# SECRET_KEY
default_secret_key = 'default_secret_key'
SECRET_KEY = os.getenv('SECRET_KEY', default_secret_key)
if SECRET_KEY == default_secret_key:
    logger.warning("SECRET_KEY не задан в переменных окружения. Используется значение по умолчанию.")

# AVATAR_DIR
default_avatar_dir = os.path.join(get_base_dir(), 'avatars')
AVATAR_DIR = os.getenv('AVATAR_DIR', default_avatar_dir)
if AVATAR_DIR == default_avatar_dir:
    logger.warning("AVATAR_DIR не задан в переменных окружения. Используется значение по умолчанию.")

# Обеспечение существования директории для аватаров
try:
    os.makedirs(f"{AVATAR_DIR}", exist_ok=True)
except OSError as e:
    logger.error(f"Не удалось создать каталог AVATAR_DIR: {e}")
    raise RuntimeError((f"Не удалось создать каталог AVATAR_DIR: {AVATAR_DIR}."
                        "Приложение не может продолжать работу.")) from e

logger.info(f"DATABASE_URL: {DATABASE_URL}")
logger.info(f"SECRET_KEY: {SECRET_KEY}")
logger.info(f"AVATAR_DIR: {AVATAR_DIR}")
