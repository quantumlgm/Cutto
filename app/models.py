from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class Links(Base):
    __tablename__ = 'links'
    original: Mapped[str] = mapped_column(nullable=False)
    shortened: Mapped[str] = mapped_column(unique=True)
    clicks: Mapped[int] = mapped_column(default=0)