from sqlalchemy import select, delete, update
from db.models import engine, Base, async_session, Autopost


class Database:
    @staticmethod
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def create_autopost(name: str, url: str, interval: int):
        async with async_session() as session:
            autopost = Autopost(
                name=name,
                url=url,
                interval=interval
            )
            session.add(autopost)
            await session.commit()
            return autopost

    @staticmethod
    async def get_autoposts():
        async with async_session() as session:
            result = await session.execute(
                select(Autopost)
            )
            return result.scalars().all()

    @staticmethod
    async def toggle_autopost(post_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Autopost)
                .where(Autopost.id == post_id)
            )
            autopost = result.scalar_one_or_none()

            if autopost:
                autopost.is_active = not autopost.is_active
                await session.commit()
                return True
            return False

    @staticmethod
    async def delete_autopost(post_id: int):
        async with async_session() as session:
            result = await session.execute(
                delete(Autopost)
                .where(Autopost.id == post_id)
            )
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def update_links(post_id: int, new_links: str):
        async with async_session() as session:
            result = await session.execute(
                update(Autopost)
                .where(Autopost.id == post_id)
                .values(links=new_links)
            )
            await session.commit()