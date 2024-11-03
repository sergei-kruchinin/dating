"""
Модуль: schemas.user

Этот модуль определяет Pydantic схемы для операций с пользователями, включая создание
нового пользователя и ответ с информацией о пользователе.
"""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для создания нового пользователя.

    Атрибуты:
        gender (Literal['male', 'female']): Пол пользователя; может быть 'male' или 'female'.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        email (EmailStr): Адрес электронной почты пользователя.
        password (str): Пароль для учетной записи пользователя.
    """
    gender: Literal['male', 'female'] = Field(...,
                                              description="Пол пользователя; может быть 'male' или 'female'.")
    first_name: str = Field(..., description="Имя пользователя.")
    last_name: str = Field(..., description="Фамилия пользователя.")
    email: EmailStr = Field(..., description="Адрес электронной почты пользователя.")
    password: str = Field(..., description="Пароль для учетной записи пользователя.")


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        email (EmailStr): Адрес электронной почты пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        gender (str): Пол пользователя.
        avatar_url (str | None): URL аватара пользователя, если есть.
    """
    id: int = Field(..., description="Уникальный идентификатор пользователя.")
    email: EmailStr = Field(..., description="Адрес электронной почты пользователя.")
    first_name: str = Field(..., description="Имя пользователя.")
    last_name: str = Field(..., description="Фамилия пользователя.")
    gender: str = Field(..., description="Пол пользователя.")
    avatar_url: str | None = Field(None, description="URL аватара пользователя.")

    class Config:
        from_attributes = True
        """Поддержка работы с ORM моделями, позволяет доступ к атрибутам."""
