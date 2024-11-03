"""
Модуль: services.user_service

Предоставляет сервис для управления пользователями, включая создание пользователей
и получение пользователей по электронной почте и ID.
"""

import logging


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import UserModel


logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для работы с пользователями.

    Параметры:
        db (AsyncSession): Асинхронная сессия базы данных,
        password_hasher (PasswordHasherProtocol): Сервис для хеширования паролей,
        image_service (ImageServiceProtocol): Сервис для работы с изображениями.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def email_exists(self, email: str) -> bool:
        """
        Проверяет, существует ли пользователь с данным email в базе данных.

        Параметры:
            email (str): Электронная почта пользователя.

        Возвращает:
            bool: True, если пользователь с данным email существует, иначе False.
        """
        query = select(UserModel).filter(UserModel.email == email)
        result = await self.db.execute(query)
        existing_user = result.scalars().first()
        return existing_user is not None
