from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets
import logging

from ..schemas import Update, CheckAll
from ..database import get_db, redis
from ..models import Links, Users
from ..functions import scheduler, task_expire, get_token, get_admin

router_link = APIRouter()
logger = logging.getLogger(__name__)


@router_link.get(
    "/get/all",
    tags=["Statistics"],
    summary="Get all links",
)
async def all(
    limit: int = 10,
    offset: int = 0,
    admin: Users = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info(
            f"Admin {admin.id} requested all links (limit={limit}, offset={offset})"
        )
        query = await db.execute(
            select(Links).limit(limit).offset(offset).order_by(Links.created_at.desc())
        )
        item = query.scalars().all()
        if not item:
            logger.warning("No links found")
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in 'all' endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get(
    "/get/my",
    tags=["Statistics"],
    summary="Get user links",
)
async def my(
    limit: int = 10,
    offset: int = 0,
    user_id: int = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    if not user_id:
        logger.warning("An unregistered user attempted to retrieve their links")
        raise HTTPException(status_code=401, detail="Log in to see your links")
    logger.info(f"The user with user_id: {user_id} has requested their links")
    try:
        query = await db.execute(
            select(Links)
            .limit(limit)
            .offset(offset)
            .where(Links.owner_id == user_id)
            .order_by(Links.created_at.desc())
        )
        item = query.scalars().all()
        if not item:
            logger.warning(f"The user with user_id: {user_id} has no links")
            return {"links": [], "detail": "You dont have links. Please create it"}
        logger.info(f"The user with user_id: {user_id} has been sent their links")
        return {"links": item}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get(
    "/get/{id}",
    tags=["Statistics"],
    summary="Get links for a specific user",
)
async def get_one_link(
    id: int, admin: Users = Depends(get_admin), db: AsyncSession = Depends(get_db)
):
    try:
        logger.info(f"Admin {admin.id} is searching for link ID: {id}")
        query = await db.execute(select(Links).where(Links.id == id))
        item = query.scalar_one_or_none()
        if not item:
            logger.warning(f"Link ID {id} not found")
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error while fetching link ID {id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get("/leaderboard", tags=["Statistics"], summary="Get most popular links")
async def leaderboard(
    admin: Users = Depends(get_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info(f"Admin {admin.id} requested leaderboard")
        query = await db.execute(select(Links).order_by(Links.clicks.desc()))
        item = query.scalars().all()
        if not item:
            logger.warning("Leaderboard requested but no links exist")
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get(
    "/{link}",
    tags=["Links"],
    summary="Redirect from short link",
    description="Usage: Enter http://your_domain/{short_link} in your browser",
)
async def get_link(link: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"Attempting redirect for short link: {link}")
        cache_key = f"link:{link}"
        clicks_key = f"clicks:{link}"
        original_url = await redis.get(cache_key)

        if not original_url:
            logger.info(f"Cache miss for '{link}', searching in database")
            query = await db.execute(select(Links).where(Links.shortened == link))
            item = query.scalar_one_or_none()
            if not item:
                logger.warning(f"Failed redirect: short link '{link}' does not exist")
                raise HTTPException(status_code=404, detail="No links found")
            original_url = item.original
            async with redis.pipeline(transaction=True) as pipe:
                pipe.set(cache_key, original_url, ex=3600)
                pipe.setnx(clicks_key, item.clicks)
                pipe.incr(clicks_key)
                await pipe.execute()
        else:
            logger.debug(f"Cache hit for '{link}'")
            await redis.incr(clicks_key)
        return RedirectResponse(url=original_url)
    except Exception as e:
        print(f"Server error: {e}")
        logger.error(f"Critical error during redirect for '{link}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.post("/create", tags=["Links"], summary="Universal short link creator")
async def create(
    data: CheckAll,
    user_id: int = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    logger.debug(f"User {user_id} is creating a new link for URL: {data.url}")
    final_short_link = None
    expire_date = None

    if data.text:
        query = await db.execute(select(Links).where(Links.shortened == data.text))
        if query.scalar_one_or_none():
            logger.warning(
                f"Link creation failed: custom name '{data.text}' already taken"
            )
            raise HTTPException(status_code=409, detail="Short name already taken")
        final_short_link = data.text

    if data.time:
        expire_date = datetime.now() + timedelta(hours=data.time)

    if not final_short_link:
        while True:
            temp_code = secrets.token_urlsafe(4)[:5]
            check_code = await db.execute(
                select(Links).where(Links.shortened == temp_code)
            )
            if not check_code.scalar_one_or_none():
                final_short_link = temp_code
                break
    try:
        new_link = Links(
            original=str(data.url),
            shortened=final_short_link,
            expire_at=expire_date,
            owner_id=user_id,
        )
        cache_key = f"link:{final_short_link}"
        clicks_key = f"clicks:{final_short_link}"
        await redis.set(cache_key, str(data.url), ex=3600)
        await redis.setnx(clicks_key, 0)
        db.add(new_link)
        await db.commit()
        await db.refresh(new_link)

        if expire_date:
            logger.info(
                f"Link {new_link.id} created with expiration date: {expire_date}"
            )
            scheduler.add_job(
                task_expire, trigger="date", run_date=expire_date, args=[new_link.id]
            )

        return new_link

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create link for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create link")


@router_link.delete("/delete/{id}", tags=["Links"], summary="Delete link")
async def delete(
    id: int, user_id: int = Depends(get_token), db: AsyncSession = Depends(get_db)
):
    logger.info(f"User {user_id} attempting to delete link ID {id}")
    query = await db.execute(select(Links).where(Links.id == id))
    item = query.scalar_one_or_none()
    if not item:
        logger.warning(f"Delete failed: link ID {id} not found")
        raise HTTPException(
            status_code=404, detail=f"The link with id:{id} was not found"
        )
    if user_id == item.owner_id:
        try:
            await db.delete(item)
            await db.commit()
            await redis.delete(f"link:{item.shortened}", f"clicks:{item.shortened}")
            logger.info(f"Link ID {id} successfully deleted by owner {user_id}")
            return {"status": 200, "result": item, "message": "Successfuly deleted"}
        except Exception:
            await db.rollback()
            logger.error(f"Error deleting link ID {id}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Failed to delete from the database"
            )
    elif user_id is None or user_id != item.owner_id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this link"
        )


@router_link.patch("/update", tags=["Links"], summary="Update link")
async def update(
    data: Update, user_id: int = Depends(get_token), db: AsyncSession = Depends(get_db)
):
    logger.info(f"User {user_id} attempting to update link ID {data.id}")
    query = await db.execute(select(Links).where(Links.id == data.id))
    item = query.scalar_one_or_none()

    if not item:
        logger.warning(f"Update failed: link ID {data.id} not found")
        raise HTTPException(status_code=404, detail=f"Link with id:{data.id} not found")

    if user_id == item.owner_id:
        try:
            item.original = str(data.url)
            await db.commit()
            await db.refresh(item)
            await redis.delete(f"link:{item.shortened}", f"clicks:{item.shortened}")
            logger.info(f"Link ID {data.id} successfully updated by owner {user_id}")
            return {"status": 200, "result": item, "message": "Succesfuly updated"}
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating link ID {data.id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Error while updating from the database"
            )
    else:
        logger.warning(
            f"Unauthorized update attempt: User {user_id} on link ID {data.id}"
        )
        raise HTTPException(
            status_code=403, detail="You don't have permission to update this link"
        )
