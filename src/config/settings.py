"""
Модуль: config.settings

Модуль для управления конфигурацией приложения. Здесь загружаются переменные окружения
и задаются значения по умолчанию для ключевых параметров.

Обрабатываемые параметры:
- URL базы данных
- секретный ключ для генерации JWT-токенов
- каталог для хранения изображений аватаров
- префикс URL для аватаров
- путь к файлу вотермарка

Также создается каталог для хранения изображений аватаров, если не создан ранее

"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Загрузка переменных из .env файла и настройка логирования
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_base_dir() -> Path:
    """Возвращает базовый каталог проекта."""
    return Path(__file__).resolve().parent.parent.parent


BASE_DIR = get_base_dir()


def get_env_variable(name: str, default: str) -> str:
    """
    Возвращает значение переменной окружения или значение по умолчанию.

    Args:
        name (str): Имя переменной окружения,
        default (str): Значение по умолчанию, если переменная окружения не определена.

    Returns:
        str: Значение переменной окружения или значение по умолчанию.
    """
    value = os.getenv(name, default)
    if value == default:
        logger.warning(f"{name} не задан в переменных окружения. Используется значение по умолчанию.")
    logger.info(f"{name}: {value}")
    return value

def get_env_variable_only_from_env(name: str) -> str:
    """
    Возвращает значение переменной окружения или значение по умолчанию.

    Args:
        name (str): Имя переменной окружения,
        default (str): Значение по умолчанию, если переменная окружения не определена.

    Returns:
        str: Значение переменной окружения или значение по умолчанию.
    """
    value = os.getenv(name, '')
    if value == '':
        logger.error(f"{name} не задан в переменных окружения. ")
    logger.info(f"{name}: set {value}")
    return value


# Загрузка конфигурационных переменных
DATABASE_URL = get_env_variable('DATABASE_URL', f'sqlite+aiosqlite:///{BASE_DIR / "database.db"}')
AUTH_SECRET = get_env_variable('AUTH_SECRET', 'default_secret_key')
AUTH_EXPIRES_SECONDS = int(get_env_variable('AUTH_EXPIRES_SECONDS', '600'))  # 10 минут

AVATAR_DIR = get_env_variable('AVATAR_DIR', str(BASE_DIR / 'avatars'))
AVATAR_URL_PREFIX = get_env_variable('AVATAR_URL_PREFIX', 'avatars')
WATERMARK_PATH = get_env_variable('WATERMARK_FILE', str(BASE_DIR / 'watermark.png'))


# Без дефолтного значения для YANDEX_SMTP_SECRET
YANDEX_SMTP_SECRET = get_env_variable('YANDEX_SMTP_SECRET', default='')
YANDEX_EMAIL = get_env_variable('YANDEX_EMAIL', default='')

# Обеспечение существования директории для аватаров
avatar_path = Path(AVATAR_DIR)
try:
    avatar_path.mkdir(parents=True, exist_ok=True)
except OSError as e:
    error_msg = f"Не удалось создать каталог AVATAR_DIR: {AVATAR_DIR}. Приложение не может продолжать работу."
    logger.error(error_msg)
    raise RuntimeError(error_msg) from e
