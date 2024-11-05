# services.like_service

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.like import LikeModel
from models.user import UserModel

logger = logging.getLogger(__name__)


class LikeService:
    """
    Сервис для работы с лайками пользователей.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def user_exists(self, user_id: int) -> bool:
        """
        Проверяет, существует ли пользователь в базе данных.

        Args:
            user_id (int): ID пользователя.

        Returns:
            bool: True, если пользователь существует, иначе False.
        """
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        return user is not None

    async def create_like(self, user_id: int, liked_user_id: int) -> None:
        """
        Создает лайк от одного пользователя к другому.

        Args:
            user_id (int): ID пользователя, который ставит лайк.
            liked_user_id (int): ID пользователя, которому ставят лайк.

        Raises:
            ValueError: Если user_id и liked_user_id совпадают или если один из пользователей не существует.
            SQLAlchemyError: В случае ошибки во время работы с базой данных.
        """
        if user_id == liked_user_id:
            raise ValueError("Пользователь не может лайкать сам себя")

        # Проверка существования пользователей
        if not await self.user_exists(user_id):
            raise ValueError(f"Пользователь с ID {user_id} не существует.")
        if not await self.user_exists(liked_user_id):
            raise ValueError(f"Пользователь с ID {liked_user_id} не существует.")

        try:
            # Проверяем, существует ли уже лайк
            query = select(LikeModel).filter(
                LikeModel.user_id == user_id,
                LikeModel.liked_user_id == liked_user_id
            )
            result = await self.db.execute(query)
            existing_like = result.scalars().first()

            if existing_like:
                logger.info(f"Лайк уже существует от пользователя {user_id} к пользователю {liked_user_id}")
                return

            # Создаем новый лайк
            new_like = LikeModel(user_id=user_id, liked_user_id=liked_user_id)
            self.db.add(new_like)
            await self.db.commit()
            logger.info(f"Лайк создан от пользователя {user_id} к пользователю {liked_user_id}")

        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Ошибка работы с базой данных при создании лайка: {e}")
            raise

