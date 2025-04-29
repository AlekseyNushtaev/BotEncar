import asyncio
import datetime

import aiofiles
import aiohttp
import requests
import bs4
import time
from bot import bot
from config import KEY_EXCHANGERATE
from translator import trans


async def get_photo(client, link, i):
    async with client.get(url=link) as response:
        f = await aiofiles.open(f'pics/{i + 1}.jpg', mode='wb')
        await f.write(await response.read())
        await f.close()


async def kbchachacha_pars(link):
    try:
        if 'm.kbchachacha' not in link:
            link = link.replace('www.kbchachacha.com/public/car', 'm.kbchachacha.com/public/web/car')
        response = requests.get(link)
        html = response.text.replace('<br>', ' ')
        soup = bs4.BeautifulSoup(html, 'lxml')
        content = soup.find(attrs={"property": "og:description"}).get('content')
        model_ = content.split(')')[1].split(' | ')[0]
        year = '20' + content.split(' | ')[1][:2]
        km = content.split(' | ')[2]
        price_ = soup.find(attrs={"class": "car-intro__cost-highlight"}).find('strong').text.strip()
        if ',' in price_:
            price = float((price_.replace(',', '.'))) * 10000000
        else:
            price = int(price_) * 10000
        img_lst = []
        img_ = soup.find(attrs={"id": "divCarPhotoList"}).find_all("img")
        for im in img_:
            img = im.get("data-src")
            if not img:
                img = im.get("src")
            if img not in img_lst:
                img_lst.append(img)
        async with aiohttp.ClientSession() as client:
            coros = []
            for i in range(len(img_lst)):
                link = img_lst[i]
                coros.append(get_photo(client, link, i))
            await asyncio.gather(*coros)
        model_ = await trans(model_)
        model = model_.replace('The ', '').replace('Benz', 'Mercedes-Benz').replace('the ', '')
        time_pars = datetime.datetime.now()
        response = requests.get(f"https://v6.exchangerate-api.com/v6/{KEY_EXCHANGERATE}/latest/USD")
        currency_usd = response.json()["conversion_rates"]["KRW"]
        price_usd = str((int(price / currency_usd + 1500) // 100) * 100)
        return [model, year, km, price_usd, img_lst, time_pars]
    except Exception as e:
        await bot.send_message(1012882762, str(e))
