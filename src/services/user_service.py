"""
Модуль: services.user_service

Предоставляет сервис для управления пользователями, включая создание пользователей
и получение пользователей по электронной почте и ID.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from exceptions.exceptions import UserNotFound, EmailAlreadyRegistered, DatabaseError
from interfaces.protocols import PasswordHasherProtocol
from models.user import UserModel
from schemas.user import UserCreate

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для работы с пользователями.

    Attributes:
        db (AsyncSession): Асинхронная сессия базы данных,
        password_hasher (PasswordHasherProtocol): Сервис для хеширования паролей,
    """

    def __init__(self, db: AsyncSession, password_hasher: PasswordHasherProtocol):
        self.db = db
        self.password_hasher = password_hasher

    async def email_exists(self, email: str) -> bool:
        """
        Проверяет, существует ли пользователь с данным email в базе данных.

        Args:
            email (str): Электронная почта пользователя.

        Returns:
            bool: True, если пользователь с данным email существует, иначе False.
        """
        query = select(UserModel).filter(UserModel.email == email)
        result = await self.db.execute(query)
        existing_user = result.scalars().first()
        return existing_user is not None

    async def create_user(self, user: UserCreate, avatar_url: str) -> UserModel:
        """
        Создает нового пользователя.

        Args:
            user (UserCreate): Данные нового пользователя,
            avatar_url (str): URL аватара пользователя.

        Returns:
            UserModel: Созданный пользователь.

        Raises:
            Exception: В случае уже существования пользователя или ошибки загрузки изображения
        """
        logger.info("Попытка создать пользователя с email: %s", user.email)

        # Проверка наличия пользователя с таким же email
        if await self.email_exists(user.email):
            logger.info("Регистрация пользователя с email \"%s\" отклонена: email уже используется.",
                        user.email)
            raise EmailAlreadyRegistered("Email уже зарегистрирован")

        try:
            # Обработка аватара и хеширование пароля
            hashed_password = self.password_hasher.hash_password(user.password)

            # Создание новой записи пользователя
            db_user = UserModel(
                avatar_url=avatar_url,
                gender=user.gender,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                hashed_password=hashed_password,
                is_active=True  # Устанавливаем is_active по умолчанию на True
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            logger.info("Пользователь с email \"%s\" успешно создан.", db_user.email)
            return db_user

        except SQLAlchemyError as e:
            logger.error(f"Ошибка транзакции при создании пользователя: {e}")
            # Откатываем транзакцию в случае ошибки
            await self.db.rollback()
            raise DatabaseError("Ошибка при работе с базой данных") from e

    async def get_user_by_id(self, user_id: int) -> UserModel:
        """
        Получает пользователя по его ID.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            UserModel: Найденный пользователь.

        Raises:
            UserNotFound: Если пользователь не найден или неактивен.
        """
        logger.info("Запрос пользователя с ID: %d", user_id)

        query = select(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True)
        result = await self.db.execute(query)
        user = result.scalars().first()
        if user is None:
            logger.info("Пользователь с ID \"%d\" не найден или неактивен.", user_id)
            raise UserNotFound("Пользователь не найден")

        logger.info("Пользователь с ID \"%d\" найден: %s", user_id, user.email)
        return user

    async def delete_user_by_id(self, user_id: int) -> None:
        """
        Удаляет пользователя по его ID (hard delete)

        Args:
            user_id (int): Идентификатор пользователя.

        Raises:
            UserNotFound: Если пользователь не найден или неактивен.
            DatabaseError: В случае ошибки базы данных.
        """
        logger.info("Попытка удалить пользователя с ID: %d", user_id)

        try:
            # Используем get_user_by_id для проверки
            user = await self.get_user_by_id(user_id)

            await self.db.delete(user)
            await self.db.commit()
            logger.info(f"Пользователь с ID \"{user_id}\" успешно удален.")

        except UserNotFound:
            logger.info("Пользователь с ID \"%d\" не найден или неактивен.", user_id)
            raise  # Повторно выбрасываем исключение UserNotFound для верхних уровней

        except SQLAlchemyError as e:
            logger.error(f"Ошибка транзакции при удалении пользователя: {e}")
            await self.db.rollback()
            raise DatabaseError("Ошибка при работе с базой данных") from e