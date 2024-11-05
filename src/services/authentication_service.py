# services/authentication_service.py

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exceptions import UserNotFound, DatabaseError
from interfaces.protocols import PasswordHasherProtocol
from models.user import UserModel
from services.user_service import UserService
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Сервис аутентификации пользователей.

    Attributes:
        db (AsyncSession): Асинхронная сессия базы данных.
        user_service (UserService): Сервис для работы с пользователями.
        password_hasher (PasswordHasherProtocol): Сервис для хеширования и проверки паролей.
    """

    def __init__(self, db: AsyncSession, user_service: UserService, password_hasher: PasswordHasherProtocol):
        self.db = db
        self.user_service = user_service
        self.password_hasher = password_hasher

    async def authenticate_user(self, email: str, password: str) -> UserModel:
        """
        Аутентифицирует пользователя по email и паролю.

        Args:
            email (str): Электронная почта пользователя.
            password (str): Пароль пользователя.

        Returns:
            UserModel: Найденный пользователь.

        Raises:
            UserNotFound: Если пользователь не найден или пароль неверный.
            DatabaseError: В случае ошибки базы данных.
            ValueError: Если email или пароль пусты.
        """
        logger.info("Аутентификация пользователя с email: %s", email)

        if not email or not password:
            logger.warning("Пустой email или пароль для аутентификации")
            raise ValueError("Email и пароль не могут быть пустыми")

        try:
            # Находим пользователя по email
            query = select(UserModel).filter(UserModel.email == email)
            result = await self.db.execute(query)
            user = result.scalars().first()

            if user is None:
                logger.warning("Пользователь с email \"%s\" не найден", email)
                raise UserNotFound("Пользователь не найден")

            # Проверяем пароль
            if not self.password_hasher.verify_password(password, user.hashed_password):
                logger.warning("Неверный пароль для пользователя с email \"%s\"", email)
                raise UserNotFound("Пароль неверный")

            logger.info("Пользователь с email \"%s\" успешно аутентифицирован", email)
            return user

        except SQLAlchemyError as e:
            logger.error(f"Ошибка в базе данных при аутентификации пользователя: {e}")
            raise DatabaseError("Ошибка при работе с базой данных") from e