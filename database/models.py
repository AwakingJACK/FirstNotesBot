import os
from dotenv import load_dotenv

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession

    

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'notes'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    annotation: Mapped[str] = mapped_column(String(1024), nullable=True)
    

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    
    
