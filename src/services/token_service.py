# services/token_service.py
import logging
from datetime import datetime, timezone, timedelta

import jwt

from config.settings import AUTH_SECRET, AUTH_EXPIRES_SECONDS
from exceptions.exceptions import TokenExpired, TokenInvalid
from schemas.token import TokenPayload, TokenData, TokenVerification

# Настройка логгера
logger = logging.getLogger(__name__)


class TokenGenerator:
    """Класс для генерации JWT-токенов"""

    @staticmethod
    def generate_token(payload: TokenPayload) -> TokenData:
        """
        Формирование JWT токена и установка времени его истечения.
        Args:
            payload (TokenPayload): Данные для токена.
        Returns:
            TokenData: Сгенерированный токен и время его истечения.
        """
        if not isinstance(AUTH_SECRET, str):
            raise TypeError("AUTH_SECRET must be a string")
        exp = datetime.now(timezone.utc) + timedelta(seconds=AUTH_EXPIRES_SECONDS)
        jwt_payload = payload.dict().copy()
        jwt_payload.update({"exp": exp.timestamp()})

        encoded_jwt = jwt.encode(jwt_payload, AUTH_SECRET, algorithm='HS256')
        logger.info(f"Generated new access token")
        return TokenData(access_token=encoded_jwt, expires_in=AUTH_EXPIRES_SECONDS)


class TokenVerifier:
    """ Класс для проверки токенов"""
    @staticmethod
    def verify_token(token: str) -> TokenVerification:
        """
        Проверка JWT токена
        Args:
            token (str): Сам JWT токен
        Returns:
            TokenVerification: Информация о проверенном токене
        """
        logger.info(f"Verifying token: {token}")
        try:
            decoded = jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
            token_payload = TokenPayload(**decoded)
            logger.info("Token successfully verified")
            return token_payload.to_response()
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise TokenExpired("Token expired. Get new one")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise TokenInvalid("Invalid token")
