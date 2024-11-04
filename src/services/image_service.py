"""
Модуль: services.image_service

Предоставляет сервис для работы с изображениями на локальном диске,
их загрузку и сохранение, а также генерацию уникальных имен.
"""

import logging
import os
import uuid

import aiofiles

from config.settings import AVATAR_DIR
from exceptions.exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class LocalImageService:
    """Сервис для работы с локальными изображениями."""

    @staticmethod
    def generate_unique_filename(extension: str) -> str:
        """Генерирует уникальное имя файла на основе UUID.

        Args:
            extension (str): Расширение файла.

        Returns:
            str: Уникальное имя файла.
        """
        unique_filename = f"{uuid.uuid4()}{extension}"
        return unique_filename

    @staticmethod
    async def upload_image(file_data: bytes, unique_filename: str) -> None:
        """Загружает изображение на локальный диск.

        Args:
            file_data (bytes): Данные изображения в виде байтов,
            unique_filename (str): Расширение файла (например, ".jpg").


        Raises:
            FileProcessingError: Если произошла ошибка при сохранении файла.
        """
        logger.info("Начата загрузка изображения.")

        # Генерация полного имени файла
        file_path = os.path.join(AVATAR_DIR, unique_filename)

        try:
            # Асинхронное сохранение изображения на диск
            async with aiofiles.open(file_path, "wb") as buffer:
                await buffer.write(file_data)

            logger.info(f"Изображение успешно сохранено: {file_path}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {str(e)}")
            raise FileProcessingError("Ошибка при сохранении файла") from e

    @staticmethod
    async def delete_image(filename: str) -> None:
        """Удаляет изображение с локального диска.

        Args:
            filename (str): Имя файла для удаления.

        Raises:
            FileProcessingError: Если произошла ошибка при удалении файла.
        """
        file_path = os.path.join(AVATAR_DIR, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Изображение успешно удалено: {file_path}")
            else:
                logger.warning(f"Файл не найден и не может быть удален: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла: {str(e)}")
            raise FileProcessingError("Ошибка при удалении файла") from e