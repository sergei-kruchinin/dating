"""
Модуль: routers.clients

Определяет API-маршруты для управления клиентами в приложении.
"""
import asyncio
import logging
from typing import Union
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import SessionLocal
from config.settings import WATERMARK_PATH, AVATAR_URL_PREFIX

from schemas.errors import (BadRequestResponse, InternalServerErrorResponse,
                            NotFoundResponse, EmailAlreadyRegisteredResponse)
from schemas.user import UserCreate, UserResponse
from services.image_service import LocalImageService
from services.password_hasher import PasswordHasher
from services.watermark_service import WatermarkService
from services.user_service import UserService
from services.image_validation_service import ImageValidationService
from models.user import UserModel
from exceptions.exceptions import (UserNotFound, EmailAlreadyRegistered,
                                   FileProcessingError, FileValidationError,
                                   DatabaseError)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncSession:
    """Создает и возвращает асинхронный сеанс работы с базой данных."""
    async with SessionLocal() as session:
        yield session


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Возвращает экземпляр UserService для управления пользователями."""
    password_hasher = PasswordHasher()
    return UserService(db, password_hasher)


def get_watermark_service() -> WatermarkService:
    """Возвращает экземпляр WatermarkService для наложения водяного знака"""
    return WatermarkService(WATERMARK_PATH)


def handle_exception(exception, status_code):
    logger.error(f"Пользователь не создан: {exception}")
    raise HTTPException(
        status_code=status_code,
        detail=str(exception),
    )


# вероятно, стоило бы делать отдельный роут для загрузки изображения, и отдельный для создания пользователя
# здесь слишком сложная логика, ее бы разделить даже на отдельные микросервисы
@router.post(
    "/create",
    response_model=UserResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="Создание клиента",
    description="Обрабатывает запрос на создание нового клиента, включая асинхронную загрузку аватара",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_409_CONFLICT: {"model": EmailAlreadyRegisteredResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerErrorResponse},
    },
)
async def create_client(
        user: UserCreate = Depends(UserCreate.as_form),
        avatar: UploadFile = File(...),
        user_service: UserService = Depends(get_user_service),
        watermark_service: WatermarkService = Depends(get_watermark_service),
) -> UserResponse:

    user_name = user.email
    logger.info(f"Создание нового пользователя {user_name} инициировано")
    unique_name = LocalImageService.generate_unique_filename('.png')
    avatar_url = f"{AVATAR_URL_PREFIX}/{unique_name}"

    async def process_image() -> Union[None, HTTPException]:
        try:
            file_data = await avatar.read()
            ImageValidationService.validate_image(file_data)
            image_with_watermark = watermark_service.add_watermark(file_data)
            await LocalImageService.upload_image(image_with_watermark, unique_name)
        except FileValidationError as e:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except FileProcessingError as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail=f"Image processing error: {str(e)}")

    async def save_user() -> Union['UserModel', HTTPException]:
        try:
            return await user_service.create_user(user, avatar_url)
        except EmailAlreadyRegistered as e:
            return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except DatabaseError as e:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail=f"User creation error: {str(e)}")

    try:
        # Запускаем обе задачи параллельно и дожидаемся обеих
        results = await asyncio.gather(
            process_image(),
            save_user(),
            return_exceptions=True
        )

        process_image_result, db_user_result = results

        # Логика определения ошибки
        if isinstance(process_image_result, HTTPException) and isinstance(db_user_result, HTTPException):
            if (process_image_result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    or db_user_result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR):
                handle_exception("Обе операции завершились с внутренней ошибкой сервера",
                                 status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                handle_exception("Пользователь уже существует. Дополнительно: ошибка в файле.",
                                 status.HTTP_400_BAD_REQUEST)

        # Обработка отдельных ошибок

        # Если загрузка файла окончилась неудачной, удаляем пользователя
        # Как альтернатива, можно было бы разрешить создание без картинки... но пусть будет так
        if isinstance(process_image_result, HTTPException):
            if isinstance(db_user_result, UserModel):  # Убеждаемся, что пользователь действительно создан
                try:
                    await user_service.delete_user_by_id(db_user_result.id)
                    logger.info(f"Операции сброшены, пользователь {db_user_result.email} удалён.")
                except Exception as deletion_error:
                    logger.error(f"Ошибка при удалении пользователя: {deletion_error}")

            handle_exception(process_image_result.detail, process_image_result.status_code)

        # Если пользователя не удалось создать, удаляем изображение
        if isinstance(db_user_result, HTTPException):
            try:
                await LocalImageService.delete_image(unique_name)
                logger.info(f"Операции сброшены, изображение {unique_name} удалено.")
            except Exception as deletion_error:
                logger.error(f"Ошибка при удалении изображения: {deletion_error}")

            handle_exception(db_user_result.detail, db_user_result.status_code)

        # Если успешно, db_user_result - это объект пользователя
        logger.info(f"Пользователь {db_user_result.email} успешно создан")
        return UserResponse.from_orm(db_user_result)

    except HTTPException as e:
        raise e  # Уже обработали и запротоколировали исключение

    except Exception as e:
        handle_exception(f"An internal server error occurred: {e}", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/create2",
    response_model=UserResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="Создание клиента (последовательное)",
    description="Обрабатывает запрос на создание нового клиента, включая загрузку аватара",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": BadRequestResponse},
        status.HTTP_409_CONFLICT: {"model": EmailAlreadyRegisteredResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerErrorResponse},

    },
)
async def create_client_simple(
        user: UserCreate = Depends(UserCreate.as_form),
        avatar: UploadFile = File(...),
        user_service: UserService = Depends(get_user_service),
        watermark_service: WatermarkService = Depends(get_watermark_service)
) -> UserResponse:

    logger.info("Создание нового пользователя инициировано")
    unique_name = LocalImageService.generate_unique_filename('.png')
    avatar_url = f"{AVATAR_URL_PREFIX}/{unique_name}"

    try:

        file_data = await avatar.read()

        # Проверим, что файл является изображением
        ImageValidationService.validate_image(file_data)
        # Наложение водяного знака
        image_with_watermark = watermark_service.add_watermark(file_data)
        await LocalImageService.upload_image(image_with_watermark, unique_name)

        db_user = await user_service.create_user(user, avatar_url)
        logger.info(f"Пользователь {db_user.email} успешно создан")
        return UserResponse.from_orm(db_user)
    except EmailAlreadyRegistered as e:
        handle_exception(e, status.HTTP_409_CONFLICT)
    except FileValidationError as e:
        handle_exception(e, status.HTTP_400_BAD_REQUEST)
    except (FileProcessingError, Exception) as e:
        handle_exception(e, status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    response_model_exclude_none=True,
    summary="Получение клиента по ID",
    description="Получение клиента по его ID, без авторизации",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NotFoundResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerErrorResponse},
    },
)
async def get_user_by_id(
        user_id: int,
        user_service: UserService = Depends(get_user_service),
) -> UserResponse:

    logger.info(f"Поиск пользователя по ID: {user_id}")
    try:
        db_user = await user_service.get_user_by_id(user_id)
        logger.info(f"Пользователь {db_user.email} найден")
        return UserResponse.from_orm(db_user)
    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred.",
        )
