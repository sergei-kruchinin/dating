# services.email_service
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTP

from src.config.settings import YANDEX_SMTP_SECRET, YANDEX_EMAIL


logger = logging.getLogger(__name__)


class EmailService:
    SMTP_SERVER = "smtp.yandex.com"
    SMTP_PORT = 465

    async def send_email(self, to_email: str, subject: str, body: str):
        """
        Асинхронно отправляет электронное письмо используя Яндекс почту SMTP.

        Args:
            to_email (str): Адрес электронной почты получателя.
            subject (str): Тема письма.
            body (str): Текст письма.

        Raises:
            Exception: Если отправка не удалась.
        """
        # Настраиваем сообщение
        msg = MIMEMultipart()
        msg['From'] = YANDEX_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            logger.info("Connecting to Yandex SMTP server...")
            # Устанавливаем асинхронное соединение с SMTP сервером
            async with SMTP(hostname=self.SMTP_SERVER, port=self.SMTP_PORT, use_tls=True) as smtp:
                await smtp.login(YANDEX_EMAIL, YANDEX_SMTP_SECRET)
                await smtp.send_message(msg)
            logger.info("Email sent successfully!")

        except Exception as e:
            logger.error("Failed to send email", exc_info=True)
            raise
