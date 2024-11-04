"""
Модуль: interfaces.protocols

Определяет протоколы для сервисов, используемых в приложении.
Протоколы описывают интерфейсы, которые должны реализовывать конкретные классы.

"""

from typing import Protocol


class PasswordHasherProtocol(Protocol):
    """Протокол для хеширования и проверки паролей."""

    def hash_password(self, password: str) -> str:
        """
        Хэширует пароль.

        Args:
            password (str): Пароль, который необходимо хэшировать.

        Returns:
            str: Хэшированный пароль.
        """
        ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли предоставленный пароль указанному хешу пароля?

        Args:
            plain_password (str): Пароль в открытом виде.
            hashed_password (str): Хэшированный пароль.

        Returns:
            bool: True, если пароли совпадают, иначе False.
        """
        ...


