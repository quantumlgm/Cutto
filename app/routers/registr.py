from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from passlib.context import CryptContext

from ..schemas import CheckAuth
from ..database import get_db
from ..models import Users

router_auth = APIRouter()
pwd_context = CryptContext(schemes='bcrypt', deprecated='auto')

@router_auth.post('/registration')
async def registration(
    data: CheckAuth,
    db: AsyncSession = Depends(get_db) 
):
    hash_password = pwd_context.hash(data.password)
    try:
        new_user = Users(
            login=data.login,
            password=hash_password
        )
        db.add(new_user)
        await db.commit()
        return {
            "login": data.login,
            "password": 'password'
        }
    except IntegrityError: 
        await db.rollback()
        raise HTTPException(status_code=400, detail="User with this login already exists")
    except Exception as e:
        await db.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router_auth.post('/login')
async def login(
    data: CheckAuth,
    db: AsyncSession = Depends(get_db) 
):
    try:        
        query = await db.execute(select(Users).where(Users.login == data.login))
        result = query.scalar_one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail='No such user exists. Please register')    
        if not pwd_context.verify(data.password, result.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return {"message": "Login successful", "user_id": result.id}
    except Exception as e:
        await db.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        