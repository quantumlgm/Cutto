from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, JSON
from datetime import datetime

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class Links(Base):
    __tablename__ = 'links'
    original: Mapped[str] = mapped_column(nullable=False)
    shortened: Mapped[str] = mapped_column(unique=True)
    clicks: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    expire_at: Mapped[datetime] = mapped_column(nullable=True)

class Templates(Base):
    __tablename__ = 'templates'
    template: Mapped[dict] = mapped_column(JSON, nullable=False)