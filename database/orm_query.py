from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from database.models import User, session_maker




async def set_user(tg_id) -> None:
    async with session_maker() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def orm_add_annotation(session: AsyncSession, annotation: str, tg_id: int) -> None:
    query = update(User).where(User.tg_id == tg_id).values(annotation=annotation)
    await session.execute(query)
    await session.commit()


async def orm_deleate_annotation(session: AsyncSession, tg_id: int) -> None:
    query = update(User).where(User.tg_id == tg_id).values({User.annotation: None})
    await session.execute(query)
    await session.commit()
    
async def orm_view_annotation(session: AsyncSession, tg_id: int) -> None:
    query = select(User.annotation).where(User.tg_id == tg_id)
    result = await session.execute(query)
    annotation = result.scalar()
    if annotation is None:
        return "Заметок не найдено"
    else:
        return f'Ваша заметка:\n\n{str(annotation)}'    

