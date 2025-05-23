import asyncio
import datetime
import time

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
import requests
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot import bot
from config import CHANEL_ID, ADMIN_IDS, KEY_EXCHANGERATE, DELTA
from db.utils import Database
from encar_pars import encar_pars, encar_filter
from image_creator import image_all
from json_maker import json_maker
from kbchachacha_pars import kbchachacha_pars
from kcar_pars import kcar_pars
from translator import trans
from vk import vk_post

router = Router()

class CreateAutoposting(StatesGroup):
    waiting_name = State()
    waiting_url = State()
    waiting_interval = State()


async def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🔄 Существующие автопостинги"),
        types.KeyboardButton(text="➕ Создать новый автопостинг")
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def send_media(text):
    while True:
        try:
            media = []
            for i in range(1, 9):
                if i != 8:
                    media.append(types.InputMediaPhoto(type='photo',
                                                       media=types.FSInputFile(f'pics/{i}.jpg')))
                else:
                    media.append(types.InputMediaPhoto(type='photo',
                                                       media=types.FSInputFile(f'pics/{i}.jpg'),
                                                       caption=text))
            await bot.send_media_group(CHANEL_ID, media)
            time.sleep(3)
            break
        except:
            await asyncio.sleep(1)


async def create_text(car_list):
    model = car_list[0]
    year = car_list[1]
    km = ''
    km_ = car_list[2]
    for k in km_:
        if k.isdigit():
            km += k
    if len(km) > 3:
        km = km[:-3] + ' ' + km[-3:]
    price_usd = car_list[3]
    if len(price_usd) > 3:
        price_usd = price_usd[:-3] + ' ' + price_usd[-3:]
    text =f"""
Доступен к заказу из 🇰🇷
{model}
{year} год
{km} км
Без дтп и окрасов
Цена в Корее {price_usd} $
Возможна доставка во все регионы РФ 🇷🇺

💭 89033635817, Михаил 🟢
"""
    return text


async def scheduler():
    while True:
        flag = False
        autoposts = await Database.get_autoposts()
        time = int(datetime.datetime.now().hour) + DELTA
        for post in autoposts:
            res_bd_links = post.links.split()
            print(res_bd_links)
            interval = post.interval.split()
            for time_post in interval:
                if time == int(time_post):
                    flag = True
                    try:
                        res_links = await encar_filter(post.url)
                        for link in res_links:
                            print(link)
                            if link not in res_bd_links:
                                try:
                                    res_bd_links.append(link)
                                    if 'encar' in link:
                                        car_list = await encar_pars(link)
                                    elif 'kcar' in link:
                                        car_list = await kcar_pars(link)
                                    elif 'kbchachacha' in link:
                                        car_list = await kbchachacha_pars(link)
                                    text = await create_text(car_list)
                                    json_maker(car_list, text)
                                    image_all()
                                    await send_media(text)
                                    await vk_post(text)
                                except Exception as e:
                                    print(e)
                                    await bot.send_message(1012882762, str(e))
                                    await bot.send_message(1012882762, 'Ошибка парсинга по ссылке из фильтра')
                                new_links = ' '.join(res_bd_links)
                                print(new_links)
                                await Database.update_links(
                                    post_id=post.id,
                                    new_links=new_links
                                )
                                break
                    except Exception as e:
                        await bot.send_message(1012882762, str(e))
                        await bot.send_message(1012882762, 'Ошибка парсинга по фильтру')
        if flag:
            timedelta = (60 - int(datetime.datetime.now().minute)) * 60
            print(timedelta)
            await asyncio.sleep(timedelta)
        else:
            await asyncio.sleep(60)


@router.message(Command("start"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в менеджер автопостингов!",
        reply_markup=await main_menu()
    )


@router.message(F.text == "➕ Создать новый автопостинг", F.from_user.id.in_(ADMIN_IDS))
async def create_autoposting(message: types.Message, state: FSMContext):
    await state.set_state(CreateAutoposting.waiting_name)
    await message.answer("Введите название для автопостинга (например BMW):")


@router.message(CreateAutoposting.waiting_name, F.from_user.id.in_(ADMIN_IDS))
async def process_url(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateAutoposting.waiting_url)
    await message.answer("Введите URL для автопостинга (ссылку на фильтр)")


@router.message(CreateAutoposting.waiting_url, F.from_user.id.in_(ADMIN_IDS))
async def process_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await state.set_state(CreateAutoposting.waiting_interval)
    await message.answer("Введите время автопостинга по мск через пробел\n(Например 9 12 21)")


@router.message(CreateAutoposting.waiting_interval, F.from_user.id.in_(ADMIN_IDS))
async def process_interval(message: types.Message, state: FSMContext):
    try:
        interval_lst = message.text.split()
        print(interval_lst)
        interval = []
        for item in interval_lst:
            flag = int(item)
            interval.append(str(item))
        interval = ' '.join(interval)
    except:
        await message.answer("❌ Некорректное значение. Введите целые числа от 0 до 23 через пробел")
        return

    data = await state.get_data()
    await Database.create_autopost(
        name=data['name'],
        url=data['url'],
        interval=interval
    )
    await message.answer("✅ Автопостинг успешно создан!", reply_markup=await main_menu())
    await state.clear()


@router.message(F.text == "🔄 Существующие автопостинги", F.from_user.id.in_(ADMIN_IDS))
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


@router.callback_query(F.data.startswith("toggle_"), F.from_user.id.in_(ADMIN_IDS))
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


@router.callback_query(F.data.startswith("delete_"), F.from_user.id.in_(ADMIN_IDS))
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

@router.message(F.text, F.from_user.id.in_(ADMIN_IDS))
async def parsing(message: types.Message):
    await message.answer('Началась обработка ссылки...')
    try:
        link = message.text
        if 'encar' in link:
            car_list = await encar_pars(link)
        elif 'kcar' in link:
            car_list = await kcar_pars(link)
        elif 'kbchachacha' in link:
            car_list = await kbchachacha_pars(link)
        text = await create_text(car_list)
        json_maker(car_list, text)
        image_all()
        media = []
        for i in range(1, 9):
            if i != 8:
                media.append(types.InputMediaPhoto(type='photo', media=types.FSInputFile(f'pics/{i}.jpg')))
            else:
                media.append(types.InputMediaPhoto(type='photo', media=types.FSInputFile(f'pics/{i}.jpg'), caption=text))
        await bot.send_media_group(CHANEL_ID, media)
        await message.answer('Сообщение сформировано и направлено в канал ТГ')
        try:
            await vk_post(text)
            await message.answer('Сообщение сформировано и направлено в сообщество ВК')
        except Exception:
            pass
    except Exception as e:
        print(e)
        await bot.send_message(1012882762, str(e))
        await message.answer(
"""
Что-то пошло не так, проверьте корректность ссылки в браузере:
1. Если ссылка не корректна, исправьте ее и направьте мне повторно.
2. Если ссылка корректна - свяжитесь с разработчиком.
""")
