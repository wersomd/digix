from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Specialist(Base):
    __tablename__ = "specialists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    spec_category: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(100), nullable=False)
    work_format: Mapped[str] = mapped_column(String(100), nullable=False)
    cv: Mapped[str] = mapped_column(String(150))
    cv_text: Mapped[str] = mapped_column(String(2000))


class ClientQuery(Base):
    __tablename__ = "client_query"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query_category: Mapped[str] = mapped_column(String(100), nullable=False)
    query: Mapped[str] = mapped_column(String(160), nullable=False)