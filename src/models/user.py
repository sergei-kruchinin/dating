"""
Модуль: models.user

Модуль содержит класс UserModel, представляющий таблицу `users` в базе данных.
Описывает структуру таблицы и хранит информацию о пользователях приложения.
"""

from sqlalchemy import Column, Integer, String, Boolean

from . import Base


class UserModel(Base):
    """Класс модели для пользователя.

    Представляет таблицу `users` в базе данных, содержащую информацию о пользователе.

    Attributes:
        id (int): Первичный ключ пользователя.
        avatar_url (str, optional): URL аватара пользователя.
        gender (str): Пол пользователя; может быть 'male' или 'female'.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        email (str): Уникальный адрес электронной почты пользователя.
        hashed_password (str): Хэшированный пароль для аутентификации.
        is_active (bool): Флаг, отображающий активен ли пользователь; для soft delete.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="Первичный ключ пользователя.")
    avatar_url = Column(String, index=True, nullable=True, comment="URL аватара пользователя.")
    gender = Column(String, index=True, nullable=False, comment="Пол пользователя; может быть 'male' или 'female'.")
    first_name = Column(String, index=True, comment="Имя пользователя.")
    last_name = Column(String, index=True, comment="Фамилия пользователя.")
    email = Column(String, unique=True, index=True, comment="Уникальный адрес электронной почты пользователя.")
    hashed_password = Column(String, comment="Хэшированный пароль для аутентификации.")
    is_active = Column(Boolean, default=True,
                       comment="Флаг активности пользователя; используется для мягкого удаления.")

    def __repr__(self) -> str:
        """Возвращает строковое представление экземпляра UserModel.

        Returns:
            str: Строковое представление экземпляра модели пользователя.
        """
        return (
            f"UserModel(id={self.id}, email={self.email}, first_name={self.first_name}, "
            f"last_name={self.last_name}, is_active={self.is_active})"
        )
