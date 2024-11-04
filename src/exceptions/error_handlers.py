"""
Модуль: exceptions.error_handlers

Модуль обработки пользовательских исключений в приложении FastAPI.
Регистрируем обработчики ошибок, чтобы преобразовать исключения в
ответы JSON с соответствующими статус-кодами и сообщениями.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError

import logging

from .exceptions import FileValidationError, FileProcessingError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Регистрация обработчиков ошибок для приложения FastAPI.

    Добавляет обработчики для исключений FileValidationError и FileProcessingError,
    генерируя JSON-ответы с соответствующими статус-кодами и деталями ошибки.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI, к которому будут привязаны обработчики ошибок.
    """

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.error(f"Validation error: {exc.errors()}. Path: {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Произошла ошибка валидации",
                "errors": exc.errors()
            },
        )

    @app.exception_handler(FileValidationError)
    async def file_validation_error_handler(_request: Request, exc: FileValidationError) -> JSONResponse:
        """Обработчик для исключений FileValidationError."""
        return JSONResponse(
            status_code=400,
            content={"message": "File validation error", "details": str(exc)}
        )

    @app.exception_handler(FileProcessingError)
    async def file_processing_error_handler(_request: Request, exc: FileProcessingError) -> JSONResponse:
        """Обработчик для исключений FileProcessingError."""
        return JSONResponse(
            status_code=500,
            content={"message": "File processing error", "details": str(exc)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}. Path: {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Произошла ошибка валидации",
                "errors": exc.errors(),
                "body": str(exc.body)
            },
        )

