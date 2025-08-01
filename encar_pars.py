import asyncio
import datetime
from pprint import pprint

import aiofiles
import aiohttp
import requests
from selenium.common import NoAlertPresentException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
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


def drom_nalog(volume, year, price, browser):
    year_now = datetime.datetime.now().year
    delta_ = year_now - int(year)
    if delta_ < 3:
        delta = 'UNDER_3'
    elif delta_ > 5:
        delta = 'OVER_5'
    else:
        delta = 'FROM_3_TO_5'
    browser.get(f'https://www.drom.ru/world/calculator/?price={int(price)}&currency=KRW&vehicleAge={delta}&engineType=DIESEL_OR_GASOLINE&engineVolumeInCubicCentimeters={int(volume)}&importPurpose=USAGE')
    time.sleep(4)
    html = browser.page_source
    soup = bs4.BeautifulSoup(html, 'lxml')
    poshlina_ = soup.find_all(attrs={"class": "css-17h77f e1pqbk745"})[1].text.strip()
    poshlina = ''
    for p in poshlina_:
        if p.isdigit():
            poshlina += p
    browser.quit()
    return int(poshlina)


async def encar_pars(link):
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
        browser.get(link)
        time.sleep(20)
        html = browser.page_source
        soup = bs4.BeautifulSoup(html, 'lxml')
        model_ = soup.find(attrs={"class": "DetailSummary_tit_car__0OEVh"}).text.strip()
        year = '20' + soup.find(attrs={"class": "DetailSummary_info_summary__YtVVw"}).find_all("dd")[0].text.strip()[:2]
        km = soup.find(attrs={"class": "DetailSummary_info_summary__YtVVw"}).find_all("dd")[1].text.strip()
        price_ = soup.find(attrs={"class": "DetailLeadCase_point__vdG4b"}).text.strip()
        if ',' in price_:
            price = float((price_.replace(',', '.'))) * 10000000
        else:
            price = int(price_) * 10000
        img_lst = []
        img_ = soup.find(attrs={"class": "DetailCarPhotoPc_img_big__LNVDo"}).find_all("img")
        for im in img_[1:-1]:
            img = im.get("data-src")
            if img == None:
                img = im.get("src")
            img_lst.append(img)
            time.sleep(0.2)
        try:
            model_link = soup.find(attrs={"class": "DetailMocha_link_model__W7WLe"}).get('href')
        except:
            model_link = None
        try:
            volume = ''
            browser.find_element(By.CLASS_NAME, "DetailSummary_btn_detail__msm-h").click()
            time.sleep(2)
            html = browser.page_source
            soup = bs4.BeautifulSoup(html, 'lxml')
            techs_ = soup.find(attrs={"class": "DetailSpec_list_default__Gx+ZA"}).find_all("li")
            for tech in techs_:
                title = tech.find(attrs={"class": "DetailSpec_tit__BRQb+"}).text.strip()
                if title == '배기량':
                    volume_ = tech.find(attrs={"class": "DetailSpec_txt__NGapF"}).text.strip()
                    for e in volume_:
                        if e.isdigit():
                            volume += e
                    volume = int(volume)
                    break
        except Exception as e:
            print(e)
            volume = ''

        if model_link:
            try:
                browser.get(model_link)
                time.sleep(10)
                html = browser.page_source
                soup = bs4.BeautifulSoup(html, 'lxml')
                model_ = soup.find(attrs={"class": "tit_mocha"}).text.strip()
                print(model_)
            except Exception:
                pass

        async with aiohttp.ClientSession() as client:
            coros = []
            for i in range(len(img_lst)):
                link = img_lst[i]
                coros.append(get_photo(client, link, i))
            await asyncio.gather(*coros)
        model = await trans(model_)
        model = model.split('\n')[0].replace('The ', '').replace('Benz', 'Mercedes-Benz').replace('the ', '')
        time_pars = datetime.datetime.now()
        response = requests.get(f"https://v6.exchangerate-api.com/v6/{KEY_EXCHANGERATE}/latest/USD")
        currency_krw = response.json()["conversion_rates"]["KRW"]
        currency_rub = response.json()["conversion_rates"]["RUB"]
        try:
            poshlina = drom_nalog(volume, year, price, browser)
            price_rub = str(((int((price / currency_krw + 2000) * currency_rub + 380000 + poshlina)) // 1000) * 1000)
        except Exception as e:
            print(e)
            price_rub = 'Требует уточнения'
        browser.quit()
        return [model, year, km, price_rub, img_lst, time_pars]
    except Exception as e:
        await bot.send_message(1012882762, str(e))


def handle_alert(driver, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print("Alert text:", alert.text)
        alert.accept()  # или alert.dismiss()
        return True
    except (NoAlertPresentException, TimeoutException):
        return False


async def encar_filter(link):
    res = []
    chrome_driver_path = ChromeDriverManager().install()
    browser_service = Service(executable_path=chrome_driver_path)
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'eager'
    browser = Chrome(service=browser_service, options=options)
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;    
        '''
    })
    browser.maximize_window()
    browser.get(link)
    time.sleep(50)
    html = browser.page_source
    soup = bs4.BeautifulSoup(html, 'lxml')
    cars = soup.find_all(attrs={"class": "ItemBigImage_item__6bPnX"})
    for car in cars:
        link = car.find('a').get("href")
        res.append(link)
    browser.quit()
    time.sleep(2)
    return res


async def main():
    link = 'https://fem.encar.com/cars/detail/39215068?pageid=dc_carsearch&listAdvType=normal&carid=39215068&view_type=hs_ad&adv_attribute=hs_ad&wtClick_korList=019&advClickPosition=kor_normal_p1_g8&tempht_arg=I1ppJ3Af83C7_7'
    res = await encar_pars(link)
    pprint(res)


if __name__ == "__main__":
    asyncio.run(main())


