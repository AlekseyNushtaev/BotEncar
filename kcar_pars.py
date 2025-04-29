import asyncio
import datetime

import aiofiles
import aiohttp
import requests
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
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


async def kcar_pars(link):
    try:
        chrome_driver_path = ChromeDriverManager().install()
        browser_service = Service(executable_path=chrome_driver_path)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.page_load_strategy = 'eager'
        browser = Chrome(service=browser_service, options=options)
        browser.maximize_window()
        if 'm.kcar' in link:
            link = link.replace('https://m.kcar.com/', 'https://www.kcar.com/')
        browser.get(link)
        time.sleep(40)
        html = browser.page_source.replace('<br>', ' ')
        soup = bs4.BeautifulSoup(html, 'lxml')
        model_ = soup.find(attrs={"class": "carName"}).text.strip()
        year = '20' + soup.find(attrs={"class": "carNameWrap drct"}).find_all("li")[1].text.strip()[:2]
        km = soup.find(attrs={"class": "carNameWrap drct"}).find_all("li")[2].text.strip()
        price__ = soup.find(attrs={"class": "price"}).find("em").text.strip()
        price_ = soup.find(attrs={"class": "price"}).text.replace(price__, '').strip()
        if ',' in price_:
            price = float((price_.replace(',', '.'))) * 10000000
        else:
            price = int(price_) * 10000
        try:
            browser.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/button').click()
        except:
            pass
        img_lst = []
        img_ = soup.find(attrs={"class": "el-carousel el-carousel--horizontal"}).find_all("img")
        for im in img_:
            img = im.get("src")
            if 'RBRST' not in img and img not in img_lst:
                img_lst.append(img)
            if len(img_lst) == 18:
                break
        if len(img_lst) != 18:
            img_lst = [img_lst[0]]
            while True:
                try:
                    browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[2]/div[1]/div[5]/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]').click()
                    time.sleep(2)
                    break
                except:
                    pass
            while len(img_lst) < 18:
                try:
                    browser.find_element(By.XPATH,
                                         '/html/body/div[1]/div/div/div[2]/div/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[2]/div/div[2]/div[2]').click()
                    time.sleep(3)
                    html = browser.page_source
                    soup = bs4.BeautifulSoup(html, 'lxml')
                    img = soup.find(attrs={"class": "kaps-img"}).get("style").replace('background-image: url("', '').replace('");', '')
                    if 'RBRST' not in img and img not in img_lst:
                        img_lst.append(img)
                except:
                    pass
        async with aiohttp.ClientSession() as client:
            coros = []
            for i in range(len(img_lst)):
                link = img_lst[i]
                coros.append(get_photo(client, link, i))
            await asyncio.gather(*coros)
        browser.quit()
        model = await trans(model_)
        model = model.replace('The ', '').replace('Benz', 'Mercedes-Benz').replace('the ', '')
        time_pars = datetime.datetime.now()
        response = requests.get(f"https://v6.exchangerate-api.com/v6/{KEY_EXCHANGERATE}/latest/USD")
        currency_usd = response.json()["conversion_rates"]["KRW"]
        price_usd = str((int(price / currency_usd + 1500) // 100) * 100)
        return [model, year, km, price_usd, img_lst, time_pars]
    except Exception as e:
        await bot.send_message(1012882762, str(e))
