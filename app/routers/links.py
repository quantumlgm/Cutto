from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from datetime import datetime, timedelta

import secrets

from ..schemas import CheckUrl, CheckCreate, Update, CheckTemporary
from ..database import get_db
from ..models import Links
from ..functions import scheduler, task_expire

router_link = APIRouter()
    
@router_link.get(
    '/all',
    tags=['Statistics'],
    summary='Get all links',
)
async def all(
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(select(Links))
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail='No links found')
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f'Server error: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router_link.get(
    '/leaderboard',
    tags=['Statistics'],
    summary='Get most popular links'
)
async def leaderboard(
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(
            select(Links)
            .order_by(Links.clicks.desc())
        )
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail='No links found') 
        return item
    except HTTPException:
        raise
    except Exception as e:
        print(f'Server error: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router_link.get(
    '/{link}',
    tags=['Links'],
    summary="Redirect from short link",
    description='Usage: Enter http://your_domain/{short_link} in your browser'
)
async def get_link(
    link: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(select(Links).where(Links.shortened == link))
        item = query.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail='No links found')    
        item.clicks += 1
        await db.commit()     
        return RedirectResponse(url=item.original)
    except HTTPException:
        raise
    except Exception as e:
        print(f'Server error: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router_link.post(
    '/shorten',
    tags=['Create'],
    summary="Create a short link"
)
async def add_shorten(
    data: CheckUrl,
    db: AsyncSession = Depends(get_db)
):
    while True: 
        try:
            short_link = secrets.token_urlsafe(4)[:5] 
            item = Links(
                original=str(data.url),
                shortened=short_link
            )
            db.add(item)            
            await db.commit()
            return {
                'original': data.url,
                'shortened': short_link,
            }
        except IntegrityError:
            await db.rollback()
        except Exception as e:
            await db.rollback()
            print(f"Server error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

@router_link.post(    
    '/personal',
    tags=['Create'],
    summary="Create a personal link"
)
async def add_personal(
    data: CheckCreate,
    db: AsyncSession = Depends(get_db)
):
    new_link = Links(
        original=str(data.url),
        shortened=data.text
    )
    try:            
        db.add(new_link)
        await db.commit()
        return {
            'original': data.url,
            'short': data.text,
            data.url: data.text
        }                
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"The short link '{data.text}' is already taken. Please choose another one"
        )
    except Exception as e:
        await db.rollback()
        print(f"Server error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router_link.post(    
    '/temporary',
    tags=['Create'],
    summary="Create a temporary link"
)
async def temporary_link(
    data: CheckTemporary,
    db: AsyncSession = Depends(get_db)
):
    while True: 
        try:
            short_link = secrets.token_urlsafe(4)[:5] 
            expire_date = datetime.now() + timedelta(hours=data.time)
            item = Links(
                original=str(data.url),
                shortened=short_link,
                expire_at=expire_date
            )   
            db.add(item)            
            await db.commit()
            await db.refresh(item)
            scheduler.add_job(
                task_expire, 
                trigger='date',
                run_date=item.expire_at,
                args=[item.id]
            )
            return {
                'original': data.url,
                'shortened': short_link,
                'time': expire_date,
            }              
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"The short link '{data.text}' is already taken. Please choose another one"
            )
        except Exception as e:
            await db.rollback()
            print(f"Server error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    
@router_link.post(
    '/delete/{id}',
    tags=['Links'],
    summary="Delete link"
)
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db)
):   
    query = await db.execute(select(Links).where(Links.id == id))
    item = query.scalar_one_or_none()  
    if not item:            
        raise HTTPException(
            status_code=404,
            detail=f"The link with id:{id} was not found"
        )
    try:
        await db.delete(item)
        await db.commit()
        return {
            'status': 200,
            'result': item,
            'message': 'Successfuly deleted'
        }
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete from the database")
    
@router_link.patch(
    '/update',
    tags=['Links'],
    summary='Update link'
)
async def update(
    data: Update,
    db: AsyncSession = Depends(get_db)
):   
    query = await db.execute(select(Links).where(Links.id == data.id))
    item = query.scalar_one_or_none()  
    if not item:            
        raise HTTPException(
            status_code=404,
            detail=f"Link with id:{data.id} not found"
        )
    try:
        item.original = str(data.url)
        await db.commit()
        await db.refresh(item)
        return {
            'status': 200,
            'result': item,
            'message': 'Succesfuly updated'
        }
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error while updating from the database")


    



    
            


    