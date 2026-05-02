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
    
@router.get('/all')
async def all(
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(select(Links))
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail='Список ссылок пуст')
        return item
    except Exception as e:
        print(f'Ошибка при получении всех ссылок: {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    
@router.get('/liderboard')
async def liderboard(
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(
            select(Links)
            .order_by(Links.clicks.desc())
        )
        item = query.scalars().all()
        if not item:
            raise HTTPException(status_code=404, detail='Список ссылок пуст') 
        return item
    except Exception as e:
        print(f'Ошибка сервера: {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
@router.get('/{link}')
async def get_link(
    link: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = await db.execute(select(Links).where(Links.shortened == link))
        item = query.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail='Ссылка не найдена')    
        item.clicks += 1
        await db.commit()     
        return RedirectResponse(url=item.original)
    except Exception as e:
        print(f'Ошибка сервера: {e}')
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
@router.post('/shorten')
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
            print(f"Критическая ошибка: {e}")
            raise HTTPException(status_code=500, detail="Ошибка сервера")

@router.post('/personal')
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
            detail=f"Сокращение '{data.text}' уже занято. Выберите другое."
        )
    except Exception as e:
        await db.rollback()
        print(f"Критическая ошибка: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

    
@router.post('/delete/{id}')
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db)
):   
    query = await db.execute(select(Links).where(Links.id == id))
    item = query.scalar_one_or_none()  
    if not item:            
        raise HTTPException(
            status_code=404,
            detail=f"Ссылка с id:{id} не найдена"
        )
    try:
        await db.delete(item)
        await db.commit()
        return {
            'status': 200,
            'result': item,
            'message': 'Успешно удалено'
        }
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при удалении из базы данных")
    
@router.post('/update')
async def update(
    data: Update,
    db: AsyncSession = Depends(get_db)
):   
    query = await db.execute(select(Links).where(Links.id == data.id))
    item = query.scalar_one_or_none()  
    if not item:            
        raise HTTPException(
            status_code=404,
            detail=f"Ссылка с id:{data.id} не найдена"
        )
    try:
        item.original = str(data.url)
        await db.commit()
        await db.refresh(item)
        return {
            'status': 200,
            'result': item,
            'message': 'Успешно обновлено'
        }
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при обновлении из базы данных")


    



    
            


    