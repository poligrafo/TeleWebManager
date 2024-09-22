from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.crud_user import user_crud
from backend.app.db.session import get_db
from backend.app.models.user_models import User
from backend.app.schemas.user_schemas import UserUpdate, UserCreate


router = APIRouter()


@router.get("/users/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    users = await user_crud.get_multi(db=db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_crud.create(db=db, obj_in=user)


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.update(db=db, db_obj=db_user, obj_in=user)


@router.delete("/users/{user_id}", response_model=User)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.remove(db=db, id=user_id)
