from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.db.base_crud import CRUDBase
from backend.app.models.user_models import User
from backend.app.schemas.user_schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_nickname(self, db: AsyncSession, nickname: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.nickname == nickname)
        result = await db.execute(stmt)
        return result.scalars().first()


user_crud = CRUDUser(User)
