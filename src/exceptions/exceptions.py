"""
Модуль: exceptions.exceptions

Пользовательские исключения для обработки ошибок
"""


# Ошибки, связанные с обработкой файлов (пока только изображений)

class FileValidationError(ValueError):
    """При неверной валидации файла."""
    pass


class FileProcessingError(IOError):
    """При обработке файла."""
    pass


# Ошибки, связанные с обработкой пользователя

class EmailAlreadyRegistered(Exception):
    """Если email уже зарегистрирован"""
    pass


class UserNotFound(Exception):
    """Если пользователь не найден"""
    pass


class DatabaseError(Exception):
    """Ошибка БД"""
    pass


# Ошибки связанные с jwt-токеном
class TokenExpired(Exception):
    pass


class TokenInvalid(Exception):
    pass
