"""
Модуль: services.watermark_service

Этот модуль предоставляет сервис для наложения водяных знаков на изображения.
"""

from PIL import Image
import io


class WatermarkService:
    """
    Сервис для работы с водяными знаками.

    Attributes:
        watermark_image (Image): Изображение водяного знака,
                                           загружаемое из файла и используемое для наложения на другие изображения.

    """

    def __init__(self, watermark_path: str):
        """
        Инициализация сервиса водяного знака и загрузка изображения водяного знака в память.

        Args:
            watermark_path (str): Строка с путём до файла водяного знака.
        """
        self.watermark_image = Image.open(watermark_path)

    def add_watermark(self, image_data: bytes) -> bytes:
        """
        Добавляет водяной знак к изображению.

        Args:
            image_data (ImageData): Объект, содержащий данные об изображении.

        Returns:
            ImageData: Новый объект с данными изображения, содержащий водяной знак.
        """
        # Открытие изображения из входных данных
        image = Image.open(io.BytesIO(image_data))

        # Позиционирование водяного знака в правом нижнем углу
        position = (image.width - self.watermark_image.width, image.height - self.watermark_image.height)

        # Наложение водяного знака
        image.paste(self.watermark_image, position, self.watermark_image)

        # Сохранение обработанного изображения в памяти
        output_stream = io.BytesIO()
        image.save(output_stream, format='PNG')
        output_stream.seek(0)

        return output_stream.getvalue()
