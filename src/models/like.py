"""
Модуль: models.like

Модуль содержит класс LikeModel, представляющий таблицу `like` в базе данных.
Описывает структуру таблицы и хранит информацию о лайках пользователей друг другу.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class LikeModel(Base):
    """Модель для представления таблицы лайков.

    Эта модель используется для учета отношений "лайка" между пользователями, где один пользователь
    может лайкнуть другого пользователя.
    Время пока не храним, выглядит избыточной информацией

    Attributes:
        id (int): Уникальный идентификатор для каждой записи лайка,
        user_id (int): Идентификатор пользователя, поставившего лайк,
        liked_user_id (int): Идентификатор пользователя, которому поставили лайк,
        # created_at (datetime): Время создания записи лайка.
    """

    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
                     doc="Идентификатор ставящего лайк пользователя.")
    liked_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False,
                           doc="Идентификатор пользователя, получающего лайк.")
    # created_at = Column(DateTime(timezone=True), server_default=func.now(), doc="Время создания записи.")

    __table_args__ = (
        UniqueConstraint('user_id', 'liked_user_id', name='unique_user_like'),
    )

    # Определяем связи с другим пользователем, если требуется
    user = relationship("UserModel", foreign_keys=[user_id],
                        doc="Отношение к пользователю, который поставил лайк.")
    liked_user = relationship("UserModel", foreign_keys=[liked_user_id],
                              doc="Отношение к пользователю, получившему лайк.")