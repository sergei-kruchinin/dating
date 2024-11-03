"""
Модуль: config.database

Модуль конфигурации базы данных и создание движка для работы с
асинхронными сессиями SQLAlchemy + функция для инициализации
базы данных.

Основные компоненты:
- engine: Асинхронный движок базы данных.
- SessionLocal: Фабрика сессий для взаимодействия с базой данных.
- init_db: Функция для создания таблиц при начальной настройке.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .settings import DATABASE_URL
from models.user import UserModel  # type: ignore

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """
    Инициализация базы данных.

    Создает все таблицы в базе данных в соответствие с метаданными моделей.
    """

    from models import Base  # Импорт Base внутри функции для избежания циклического импорта.

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

