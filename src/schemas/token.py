"""
Модуль: schemas.token

Определяет схемы данных для управления JWT-токенами в приложении.
Используются для представления полезной нагрузки токенов,
данных токена и результатов проверки токена.

Состав:
- TokenPayload: Представляет данные полезной нагрузки, которые будут помещаться в JWT.
- TokenData: Представляет сам токен и время его истечения.
- TokenVerification: Представляет данные успешной проверки токена.
"""

from datetime import datetime
import logging

from pydantic import BaseModel, EmailStr, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenPayload(BaseModel):
    """Схема полезной нагрузки для токена JWT."""
    id: int = Field(..., description="User ID in the database")
    username: str = Field(..., description="Username of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    exp: datetime | None = Field(default=None, description="Expiration time, set during token generation")

    def to_response(self) -> 'TokenVerification':
        logger.info(f"to_response called: {self.dict()}")
        res = TokenVerification(
            id=self.id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            exp=self.exp.isoformat(),
            success=True
        )
        logger.info(f"ro_response done: {res}")
        return res


class TokenData(BaseModel):
    """Схема для данных токена."""
    access_token: str = Field(..., description="The encoded JWT token")
    expires_in: int = Field(..., description="Time in seconds until the token expires")


class TokenVerification(TokenPayload):
    """Схема для проверки токена."""
    exp: str = Field(..., description="Expiration time of the token")
    success: bool = Field(default=True, description="Indicates successful verification")
