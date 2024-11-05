# routers.dependencies
from typing import AsyncGenerator
import logging
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from config.database import SessionLocal
from services.authentication_service import AuthenticationService
from services.password_hasher import PasswordHasher
from services.user_service import UserService
from services.like_service import LikeService
from services.token_service import TokenVerifier
from schemas.headers import AuthorizationHeaders
from exceptions.exceptions import TokenExpired, TokenInvalid
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


async def get_token_verifier() -> TokenVerifier:
    return TokenVerifier()


async def get_user_service(db: AsyncSession = Depends(get_db),
                           hasher: PasswordHasher = Depends(get_password_hasher)) -> UserService:
    return UserService(db, hasher)


async def get_like_service(db: AsyncSession = Depends(get_db)) -> LikeService:
    return LikeService(db)


async def get_authentication_service(
        db: AsyncSession = Depends(get_db),
        user_service: UserService = Depends(get_user_service),
        password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> AuthenticationService:
    return AuthenticationService(db, user_service, password_hasher)


async def token_required(authorization: Annotated[AuthorizationHeaders, Header()],
                         token: str = Depends(oauth2_scheme),
                         token_verifier: TokenVerifier = Depends(get_token_verifier)):
    """Dependency to verify the presence and validity of a Bearer token in the request headers."""
    logger.info(f"TOKEN_REQUIRED called for {token}, header: {authorization.authorization}")

    # token = authorization.token() # I like this method more than use OAuth2PasswordBearer but now...

    try:
        verification = token_verifier.verify_token(token)
        return verification
    except TokenExpired as e:
        logger.warning(f"Token expired. Get new one: {str(e)}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token expired. Get new one") from e
    except TokenInvalid as e:
        logger.error(f"Invalid token: {str(e)}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


