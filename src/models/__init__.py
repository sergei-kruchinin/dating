"""
Модуль: __init__ пакета models

Создание базовой декларативной модели, от которой будут наследоваться все ORM-модели.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
