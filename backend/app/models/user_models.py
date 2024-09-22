from sqlalchemy import String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from backend.app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False,
                                          comment="User's nickname")
    telegram_uid: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False,
                                              comment="Telegram User ID")
    coins: Mapped[int] = mapped_column(default=0, comment="Number of coins")
    rating: Mapped[int] = mapped_column(default=0, comment="User's rating")
    last_login: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 comment="Last login time")
    last_logout: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                  comment="Last logout time")

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, nickname={self.nickname!r}, "
            f"telegram_uid={self.telegram_uid!r}, coins={self.coins!r}, "
            f"rating={self.rating!r}, last_login={self.last_login!r}, "
            f"last_logout={self.last_logout!r})"
        )
