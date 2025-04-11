from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from sqlalchemy import select, update, delete, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
bot = Bot(token="7467186280:AAFrTYhr5SBy-EDyGr3vGUvGglUePUxpNZc")
dp = Dispatcher()

#SQLAlchemy setup
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
    interval_hours = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


# FSM
class CreateAutoposting(StatesGroup):
    waiting_name = State()
    waiting_url = State()
    waiting_interval = State()


# Database manager
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
                interval_hours=interval
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


#Main menu
async def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🔄 Существующие автопостинги"),
        types.KeyboardButton(text="➕ Создать новый автопостинг")
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# Handlers
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в менеджер автопостингов!",
        reply_markup=await main_menu()
    )


@dp.message(F.text == "➕ Создать новый автопостинг")
async def create_autoposting(message: types.Message, state: FSMContext):
    await state.set_state(CreateAutoposting.waiting_name)
    await message.answer("Введите название для постинга:")


@dp.message(CreateAutoposting.waiting_name)
async def process_url(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateAutoposting.waiting_url)
    await message.answer("Введите URL для парсинга")


@dp.message(CreateAutoposting.waiting_url)
async def process_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await state.set_state(CreateAutoposting.waiting_interval)
    await message.answer("Введите интервал парсинга в часах:")


@dp.message(CreateAutoposting.waiting_interval)
async def process_interval(message: types.Message, state: FSMContext):
    try:
        interval = int(message.text)
        if interval <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректное значение. Введите целое число больше 0")
        return

    data = await state.get_data()
    await Database.create_autopost(
        name=data['name'],
        url=data['url'],
        interval=interval
    )
    await message.answer("✅ Автопостинг успешно создан!", reply_markup=await main_menu())
    await state.clear()


@dp.message(F.text == "🔄 Существующие автопостинги")
async def show_autopostings(message: types.Message):
    autoposts = await Database.get_autoposts()

    if not autoposts:
        await message.answer("❌ У вас нет активных автопостингов")
        return

    builder = InlineKeyboardBuilder()
    for post in autoposts:
        status = "✅" if post.is_active else "❌"
        builder.row(
            types.InlineKeyboardButton(
                text=f"{status} {post.id} - {post.name}",
                callback_data=f"toggle_{post.id}"
            ),
            types.InlineKeyboardButton(
                text="❌ Удалить",
                callback_data=f"delete_{post.id}"
            )
        )

    await message.answer(
        "📂 Ваши автопостинги:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_autoposting(callback: types.CallbackQuery):
    post_id = int(callback.data.split("_")[1])
    success = await Database.toggle_autopost(post_id)

    if success:
        autoposts = await Database.get_autoposts()
        builder = InlineKeyboardBuilder()
        for post in autoposts:
            status = "✅" if post.is_active else "❌"
            builder.row(
                types.InlineKeyboardButton(
                    text=f"{status} {post.id} - {post.name}",
                    callback_data=f"toggle_{post.id}"
                ),
                types.InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_{post.id}"
                )
            )
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer("Статус обновлен!")
    else:
        await callback.answer("❌ Ошибка обновления статуса")


@dp.callback_query(F.data.startswith("delete_"))
async def delete_autoposting(callback: types.CallbackQuery):
    post_id = int(callback.data.split("_")[1])
    success = await Database.delete_autopost(post_id)

    if success:
        autoposts = await Database.get_autoposts()
        if not autoposts:
            await callback.message.delete()
            await callback.answer("Автопостинг удален!")
            return

        builder = InlineKeyboardBuilder()
        for post in autoposts:
            status = "✅" if post.is_active else "❌"
            builder.row(
                types.InlineKeyboardButton(
                    text=f"{status} {post.id} - {post.name}",
                    callback_data=f"toggle_{post.id}"
                ),
                types.InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"delete_{post.id}"
                )
            )
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer("Автопостинг удален!")
    else:
        await callback.answer("❌ Не удалось удалить автопостинг")


#Startup
async def on_startup():
    await Database.init_db()


async def main():
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())