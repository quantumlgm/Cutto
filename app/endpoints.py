from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
import secrets

from .schemas import CheckUrl, CheckCreate, Update
from .database import get_db
from .models import Links

router = APIRouter()
    
@router.get(
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
    except Exception as e:
        print(f'Ошибка при получении всех ссылок: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get(
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
    except Exception as e:
        print(f'Server error: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get(
    '/{link}',
    tags=['Links'],
    summary="Redirect from short link"
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
    except Exception as e:
        print(f'Server error: {e}')
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.post(
    '/shorten',
    tags=['Create'],
    summary="Create a short link"
)
async def add_shorten(
    link: CheckUrl,
    db: AsyncSession = Depends(get_db)
):
    while True: 
        try:
            short_link = secrets.token_urlsafe(4)[:5] 
            item = Links(
                original=str(link.url),
                shortened=short_link
            )
            db.add(item)            
            await db.commit()
            return {
                'original': link,
                'shortened': short_link,
            }
        except IntegrityError:
            await db.rollback()
        except Exception as e:
            await db.rollback()
            print(f"Server error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

@router.post(    
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

    
@router.post(
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
    
@router.patch(
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


    



    
            


    