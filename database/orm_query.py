from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Specialist



async def orm_add_specialist(session: AsyncSession, data: dict):
    obj = Specialist(
        spec_category=data["spec_category"],
        specialization=data["specialization"],
        full_name=data["full_name"],
        city=data["city"],
        age=int(data["age"]),
        gender=data["gender"],
        work_format=data["work_format"],
        cv=data["cv"],
    )

    session.add(obj)
    await session.commit()


async def orm_get_specialists(session: AsyncSession):
    query = select(Specialist)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_specialists_category(session: AsyncSession, category: str):
    result = await session.execute(
        select(Specialist).where(Specialist.spec_category == category)
    )
    return result.scalars().all()


async def orm_get_specialist(session: AsyncSession, specialist_id: int):
    query = select(Specialist).where(Specialist.id == specialist_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_specialist(session: AsyncSession, specialist_id: int, data):
    query = update(Specialist).where(Specialist.id == specialist_id).values(
        spec_category=data["spec_category"],
        specialization=data["specialization"],
        full_name=data["full_name"],
        city=data["city"],
        age=int(data["age"]),
        gender=data["gender"],
        work_format=data["work_format"],
        cv=data["cv"],
    )

    await session.execute(query)
    await session.commit()


async def orm_delete_specialist(session: AsyncSession, specialist_id: int):
    query = delete(Specialist).where(Specialist.id == specialist_id)
    await session.execute(query)
    await session.commit()