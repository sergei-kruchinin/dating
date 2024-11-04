"""
Модуль: services.password_hasher

Этот модуль предоставляет утилиту для хеширования и проверки паролей
с использованием Passlib и алгоритма bcrypt.
"""

from passlib.context import CryptContext


class PasswordHasher:
    """
    Класс для хеширования и проверки паролей.

    Attributes:
        pwd_context (CryptContext): Контекст, используемый для хеширования
                                    и проверки паролей с использованием схемы bcrypt.
    """

    def __init__(self):
        """Инициализация PasswordHasher с использованием схемы bcrypt."""

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Хэширует пароль.

        Args:
            password (str): Пароль в открытом виде для хеширования.

        Returns:
            str: Хэшированный пароль.
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли предоставленный пароль указанному хешу пароля?

        Args:
            plain_password (str): Пароль в открытом виде для проверки.
            hashed_password (str): Хэшированный пароль для сравнения.

        Returns:
            bool: True, если пароли совпадают, иначе False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)
