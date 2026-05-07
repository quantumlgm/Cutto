from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import func, JSON, LargeBinary, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class Users(Base):
    __tablename__ = 'users'
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    links: Mapped[list['Links']] = relationship(back_populates='owner')

class Links(Base):
    __tablename__ = 'links'
    original: Mapped[str] = mapped_column(nullable=False)
    shortened: Mapped[str] = mapped_column(unique=True)
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    expire_at: Mapped[datetime] = mapped_column(nullable=True)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)    
    owner: Mapped["Users"] = relationship(back_populates="links")

class Templates(Base):
    __tablename__ = 'templates'
    template: Mapped[dict] = mapped_column(JSON, nullable=False)

