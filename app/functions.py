from sqlalchemy import select, delete, create_engine 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime

from .database import async_session, engine
from .models import Links
from .config import settings

apscheldue_engine = create_engine(url=settings.DB_URL_psycopg)
jobstores = {
    'default': SQLAlchemyJobStore(engine=apscheldue_engine)
}
scheduler = AsyncIOScheduler(jobstores=jobstores)

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
            print(f"No expired links were found")      