"""
Модуль: services.image_validation_service

Предоставляет сервис для проверки валидности изображений.
Он включает функциональность для определения, является ли загруженный файл
корректным изображением.
"""


from PIL import Image, UnidentifiedImageError
import io
from exceptions.exceptions import FileValidationError


class ImageValidationService:
    """Сервис для проверки валидности изображений."""

    @staticmethod
    def validate_image(image_data: bytes) -> None:
        """Проверяет, что данные представляют собой корректное изображение.

        Args:
            image_data (bytes): Данные изображения.

        Raises:
            FileValidationError: Если файл не является корректным изображением.

        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # Проверка, что изображение корректное
        except (IOError, SyntaxError, UnidentifiedImageError) as e:
            raise FileValidationError("Загруженный файл не является корректным изображением.") from e


