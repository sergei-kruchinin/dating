"""
Модуль: schemas.errors

Схемы Pydantic для обработки HTTP ошибок в API

"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Базовая схема для сообщений об ошибке

    Attributes:
        detail (str): Описание ошибки.
    """
    detail: str = Field(..., description="Краткое описание ошибки.")


class InternalServerErrorResponse(ErrorResponse):
    """
    Сообщение об ошибке 500 Internal Server Error.

    Attributes:
        detail (str): Описание ошибки.
    """
    detail: str = Field(
        "An internal server error occurred. Please try again later.",
        description="Стандартное сообщение для внутренних ошибок сервера."
    )


class BadRequestResponse(ErrorResponse):
    """
    Сообщение об ошибке 400 Bad Request.

    Attributes:
        detail (str): Описание ошибки.
    """
    detail: str = Field(
        "The request was invalid or cannot be otherwise served.",
        description="Стандартное сообщение для ошибок неверного запроса."
    )


class NotFoundResponse(ErrorResponse):
    """
    Сообщение об ошибке 404 Not Found.

    Attributes:
        detail (str): Описание ошибки.
    """
    detail: str = Field(
        "The requested resource could not be found.",
        description="Стандартное сообщение для ошибок ненайденных ресурсов."
    )


class EmailAlreadyRegisteredResponse(ErrorResponse):
    """
    Сообщение об ошибке 409 Conflict из-за уже зарегистрированного email.

    Attributes:
        detail (str): Описание ошибки.
    """
    detail: str = Field(
        "Email уже зарегистрирован.",
        description="Стандартное сообщение для конфликтов из-за дублирования email."
    )
