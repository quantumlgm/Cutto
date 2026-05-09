from sqlalchemy import select, delete, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timezone, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from .database import async_session
from .models import Links, Users
from .config import settings
from .database import get_db

apscheldue_engine = create_engine(url=settings.DB_URL_psycopg)
jobstores = {"default": SQLAlchemyJobStore(engine=apscheldue_engine)}
scheduler = AsyncIOScheduler(jobstores=jobstores)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


async def task_expire(id: int):
    async with async_session() as session:
        query = await session.execute(select(Links).where(Links.id == id))
        result = query.scalar_one_or_none()
        if result:
            await session.delete(result)
            await session.commit()
            print(f"Link with ID {id} was successfully deleted after expiration")
        else:
            print(f"Link with ID {id} was not found")


async def link_cleaner():
    async with async_session() as session:
        query = await session.execute(
            delete(Links).where(Links.expire_at < datetime.now())
        )
        if query.rowcount > 0:
            await session.commit()
        else:
            print("No expired links were found")


async def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPERATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_admin(
    user_id: int = Depends(get_token), db: AsyncSession = Depends(get_db)
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    query = await db.execute(select(Users).where(Users.id == user_id))
    result = query.scalar_one_or_none()
    if not result or not result.is_admin:
        raise HTTPException(
            status_code=403, detail="Forbidden: You do not have admin permissions"
        )
    return result
