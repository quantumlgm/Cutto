from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
import logging

from ..schemas import CheckAuth
from ..database import get_db
from ..models import Users
from ..functions import create_token

router_auth = APIRouter()
pwd_context = CryptContext(schemes="bcrypt", deprecated="auto")
logger = logging.getLogger(__name__)


@router_auth.post("/registration", tags=["Authorisation"], summary="Create new account")
async def registration(data: CheckAuth, db: AsyncSession = Depends(get_db)):
    logger.info(f"Attempting to register a new user with login: {data.login}")
    hash_password = pwd_context.hash(data.password)
    try:
        new_user = Users(login=data.login, password=hash_password)
        db.add(new_user)
        await db.commit()
        logger.info(f"User '{data.login}' successfully registered")
        return {"login": data.login}
    except IntegrityError:
        await db.rollback()
        logger.warning(f"Registration failed: login '{data.login}' is already taken")
        raise HTTPException(
            status_code=400, detail="User with this login already exists"
        )
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Unexpected error during registration for '{data.login}': {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router_auth.post("/login", tags=["Authorisation"], summary="Log in your account")
async def login(
    data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    logger.info(f"Login attempt for user: {data.username}")
    try:
        query = await db.execute(select(Users).where(Users.login == data.username))
        item = query.scalar_one_or_none()

        if not item:
            logger.warning(f"Login failed: user '{data.username}' not found")
            raise HTTPException(
                status_code=404, detail="No such user exists. Please register"
            )

        if not pwd_context.verify(data.password, item.password):
            logger.warning(
                f"Login failed: incorrect password for user '{data.username}'"
            )
            raise HTTPException(status_code=401, detail="Invalid password")

        access_token = await create_token(data={"sub": str(item.id)})
        logger.info(f"User '{data.username}' (ID: {item.id}) logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Unexpected login error for user '{data.username}': {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
