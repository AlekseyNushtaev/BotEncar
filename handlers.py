from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import requests
from bot import bot
from config import CHANEL_ID, ADMIN_IDS, KEY_EXCHANGERATE
from encar_pars import encar_pars
from translator import trans

router = Router()

async def create_text(car_list):
    model_ = await trans(car_list[0])
    model = model_.replace('The ', '').replace('Benz', 'Mercedes-Benz').replace('the ', '')
    year = '20' + car_list[1][:2]
    if ',' in car_list[3]:
        price_co = float((car_list[3].replace(',', '.'))) * 10000000
    else:
        price_co = int(car_list[3]) * 10000
    response = requests.get(f"https://v6.exchangerate-api.com/v6/{KEY_EXCHANGERATE}/latest/USD")
    currency_usd = response.json()["conversion_rates"]["KRW"]
    price_usd = str((int(price_co/currency_usd + 1500) // 100) * 100)
    if len(price_usd) > 3:
        price_usd = price_usd[:-3] + ' ' + price_usd[-3:]
    km = ''
    km_ = car_list[2]
    for k in km_:
        if k.isdigit():
            km += k
    if len(km) > 3:
        km = km[:-3] + ' ' + km[-3:]
    text =f"""
Доступен к заказу из 🇰🇷
{model}
{year} год
{km} км
Без дтп и окрасов
Бюджет под 🔑 до Москвы {price_usd} $
Возможна доставка во все регионы РФ 🇷🇺

💭 89033635817, Михаил 🟢
"""
    return text

@router.message(CommandStart(), F.from_user.id.in_(ADMIN_IDS))
async def process_start_admin(message: Message):
    await message.answer(text="Здравствуйте, скиньте корректную ссылку на авто с сайта fem.encar.com для формирования сообщения в группу")


@router.message(F.text, F.from_user.id.in_(ADMIN_IDS))
async def parsing(message: types.Message):
    await message.answer('Началась обработка ссылки, займет около 30 сек...')
    try:
        link = message.text
        car_list = await encar_pars(link)
        text = await create_text(car_list)
        for i in range(10):
            media = [types.InputMediaPhoto(type='photo', media=types.FSInputFile(f'pics/{i * 2 + 1}.jpg'))]
            if i != 9:
                media.append(types.InputMediaPhoto(type='photo', media=types.FSInputFile(f'pics/{i * 2 + 2}.jpg')))
            else:
                media.append(types.InputMediaPhoto(type='photo', media=types.FSInputFile(f'pics/{i * 2 + 2}.jpg'), caption=text))
            await bot.send_media_group(CHANEL_ID, media)
        await message.answer('Сообщение сформировано и направлено в канал')
    except Exception as e:
        print(e)
        await message.answer(
"""
Что-то пошло не так, проверьте корректность ссылки в браузере:
1. Если ссылка не корректна, исправьте ее и направьте мне повторно.
2. Если ссылка корректна - свяжитесь с разработчиком.
""")