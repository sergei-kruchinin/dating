# routers/auth.py
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from fastapi.responses import JSONResponse


from exceptions.exceptions import UserNotFound, TokenInvalid, TokenExpired
from schemas.errors import (BadRequestResponse, InternalServerErrorResponse,
                            UnauthorizedResponse)
from schemas.token import TokenData, TokenPayload, TokenVerification

from services.authentication_service import AuthenticationService
from services.token_service import TokenGenerator
from .dependencies import get_db, get_user_service, get_password_hasher, token_required

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

router = APIRouter()


def create_auth_response(token_data: TokenData) -> Response:
    """
    Create JSON response with the access token and set the refresh token in HTTP-only cookie.

    Args:
        authentication (AuthTokens): The authentication response containing tokens.

    Returns:
        Response: FastAPI response object with access token in JSON and refresh token in cookie.
    """
    logger.info(f"Создаем ответ для {token_data.access_token}")

    response_data = token_data.dict()
    response = JSONResponse(content=response_data, status_code=200)
    # Set the refresh token in HTTP-only cookie
    logger.info("Auth response created")

    return response

async def get_authentication_service(
        db=Depends(get_db),
        user_service=Depends(get_user_service),
        password_hasher=Depends(get_password_hasher)
) -> AuthenticationService:
    return AuthenticationService(db, user_service, password_hasher)


@router.post(
    "/token",
    response_model=TokenData,
    summary="Получение токена",
    description="Генерирует и возвращает JWT токен для аутентифицированного пользователя",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerErrorResponse},
    },
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthenticationService = Depends(get_authentication_service),
) -> Response:
    try:
        # Пытаемся найти пользователя по email и проверить пароль
        user = await auth_service.authenticate_user(form_data.username, form_data.password)

        # Создаем JWT токен
        payload = TokenPayload(
            id=user.id,
            username=user.first_name,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            exp=None  # Установим exp при генерации токена
        )
        token_data = TokenGenerator.generate_token(payload)

        logger.info("User %s successfully logged in", user.first_name)
        return create_auth_response(token_data)

    except UserNotFound as e:
        logger.warning("Failed login attempt for user: %s", form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@router.post("/verify", response_model=TokenVerification,
             summary="Проверка токена",
             responses={
                        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
                        status.HTTP_401_UNAUTHORIZED: {"model": UnauthorizedResponse},
                        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerErrorResponse},
                        })
async def verify(
            verification: TokenVerification = Depends(token_required)
    ) -> Response:
        """
        Route for verifying an authentication token.

        """
        logger.info(f"Verify route called: {verification}")
        response_data = verification.dict()
        logger.info(f"Converting to dict: {response_data}")

        response = JSONResponse(response_data, status_code=200)

        logger.info("Verify response created")

        return response