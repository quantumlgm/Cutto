from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets

from ..schemas import Update, CheckAll
from ..database import get_db
from ..models import Links, Users
from ..functions import scheduler, task_expire, get_token, get_admin

router_link = APIRouter()


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
        query = await db.execute(
            select(Links)
            .limit(limit)
            .offset(offset)
            .order_by(Links.created_at.desc())
        )
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
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
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Log in to see your links")
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
            return {
                "links": [],
                'detail': 'You dont have links. Please create it'
            }
        return {"links": item}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get(
    "/get/{id}",
    tags=["Statistics"],
    summary="Get links for a specific user",
)
async def get_by_user(
    id: int, admin: Users = Depends(get_admin), db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(select(Links).where(Links.owner_id == id))
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get("/leaderboard", tags=["Statistics"], summary="Get most popular links")
async def leaderboard(
    admin: Users = Depends(get_admin), db: AsyncSession = Depends(get_db),
):
    try:
        query = await db.execute(select(Links).order_by(Links.clicks.desc()))
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail="No links found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.get(
    "/{link}",
    tags=["Links"],
    summary="Redirect from short link",
    description="Usage: Enter http://your_domain/{short_link} in your browser",
)
async def get_link(link: str, db: AsyncSession = Depends(get_db)):
    try:
        query = await db.execute(select(Links).where(Links.shortened == link))
        item = query.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="No links found")
        item.clicks += 1
        await db.commit()
        return RedirectResponse(url=item.original)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_link.post("/create", tags=["Create"], summary="Universal short link creator")
async def create(
    data: CheckAll,
    user_id: int = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    final_short_link = None
    expire_date = None

    if data.text:
        query = await db.execute(select(Links).where(Links.shortened == data.text))
        if query.scalar_one_or_none():
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
        db.add(new_link)
        await db.commit()
        await db.refresh(new_link)

        if expire_date:
            scheduler.add_job(
                task_expire, trigger="date", run_date=expire_date, args=[new_link.id]
            )

        return new_link

    except Exception as e:
        await db.rollback()
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create link")


@router_link.delete("/delete/{id}", tags=["Links"], summary="Delete link")
async def delete(
    id: int, 
    user_id: int = Depends(get_token),
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(select(Links).where(Links.id == id))
    item = query.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=404, detail=f"The link with id:{id} was not found"
        )
    if user_id == item.owner_id:
        try:
            await db.delete(item)
            await db.commit()
            return {"status": 200, "result": item, "message": "Successfuly deleted"}
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="Failed to delete from the database"
            )
    elif user_id is None or user_id != item.owner_id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this link"
        )


@router_link.patch("/update", tags=["Links"], summary="Update link")
async def update(
    data: Update,
    user_id: int = Depends(get_token), 
    db: AsyncSession = Depends(get_db)
):
    query = await db.execute(select(Links).where(Links.id == data.id))
    item = query.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail=f"Link with id:{data.id} not found")
    if user_id == item.owner_id:
        try:
            item.original = str(data.url)
            await db.commit()
            await db.refresh(item)
            return {"status": 200, "result": item, "message": "Succesfuly updated"}
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="Error while updating from the database"
            )
    elif user_id is None or user_id != item.owner_id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this link"
        )
