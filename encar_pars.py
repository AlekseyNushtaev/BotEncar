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
        time.sleep(10)
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
            try:
                browser.find_element(By.XPATH,
                                 '/html/body/div[1]/div/div[1]/div[1]/div[4]/div[5]/div[2]/div[4]/div[2]/button').click()
            except Exception:
                try:
                    buttons = browser.find_elements(By.TAG_NAME, 'button')
                    for button in buttons:
                        if button.text.strip() == '차량이력 자세히 보기':
                            button.click()
                            break
                except Exception:
                    browser.find_element(By.CSS_SELECTOR,
                                         '#detailStatus > div.ResponsiveTemplete_box_type__10yIs > div:nth-child(4) > div.ResponsiveTemplete_button_type__pjT76 > button').click()
            time.sleep(15)
            new_window = browser.window_handles[1]
            browser.switch_to.window(new_window)
            time.sleep(0.5)
            html = browser.page_source
            soup = bs4.BeautifulSoup(html, 'lxml')
            model_ = soup.find(attrs={"class": "Intro_profile_list__arnX_"}).find("em").text.strip() + ' ' + model_
        except Exception:
            try:
                try:
                    browser.find_element(By.XPATH,
                                         '/html/body/div[1]/div/div[1]/div[1]/div[4]/div[5]/div[2]/div[2]/div[3]/button').click()
                except Exception:
                    try:
                        buttons = browser.find_elements(By.TAG_NAME, 'button')
                        for button in buttons:
                            if button.text.strip() == '차량관리상태 모두보기':
                                button.click()
                                break
                    except Exception:
                        browser.find_element(By.CSS_SELECTOR,
                                             '#detailStatus > div.ResponsiveTemplete_box_type__10yIs > div.ResponsiveTemplete_text_image_type__tycpJ > div.ResponsiveTemplete_button_type__pjT76 > button').click()
                time.sleep(5)
                new_window = browser.window_handles[1]
                browser.switch_to.window(new_window)
                time.sleep(1)
                html = browser.page_source
                soup = bs4.BeautifulSoup(html, 'lxml')
                model_ = soup.find(attrs={"class": "CarMainInfo_tit__F2azJ"}).text.strip()
            except Exception:
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
    options.add_argument('--headless')
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
    cars = soup.find(attrs={"class": "car_list"}).find_all("a")
    for car in cars:
        link = 'http://www.encar.com/' + car.get("href")
        res.append(link)
    browser.quit()
    time.sleep(2)
    return res


async def main():
    link = 'http://www.encar.com/dc/dc_carsearchlist.do?carType=kor#!%7B%22action%22%3A%22(And.Hidden.N._.CarType.Y._.Mileage.range(..100000)._.Year.range(202000..202299).)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22ModifiedDate%22%2C%22page%22%3A1%2C%22limit%22%3A20%2C%22searchKey%22%3A%22%22%2C%22loginCheck%22%3Afalse%7D'
    res = await encar_filter(link)
    pprint(res)
    result = await encar_pars(res[0])
    print(result)

if __name__ == "__main__":
    asyncio.run(main())


