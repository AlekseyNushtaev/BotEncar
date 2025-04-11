from sqlalchemy import select, update, delete, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime


# SQLAlchemy setup
Base = declarative_base()
DATABASE_URL = "sqlite+aiosqlite:///autoposts.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Model
class Autopost(Base):
    __tablename__ = "autoposts"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    interval = Column(String)
    links = Column(String, default='')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)