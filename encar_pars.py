import asyncio
import aiofiles
import aiohttp
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import bs4
import time
from bot import bot


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
        model = soup.find(attrs={"class": "DetailSummary_tit_car__0OEVh"}).text.strip()
        year = soup.find(attrs={"class": "DetailSummary_info_summary__YtVVw"}).find_all("dd")[0].text.strip()
        km = soup.find(attrs={"class": "DetailSummary_info_summary__YtVVw"}).find_all("dd")[1].text.strip()
        price = soup.find(attrs={"class": "DetailLeadCase_point__vdG4b"}).text.strip()
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
            time.sleep(10)
            new_window = browser.window_handles[1]
            browser.switch_to.window(new_window)
            time.sleep(0.5)
            html = browser.page_source
            soup = bs4.BeautifulSoup(html, 'lxml')
            model = soup.find(attrs={"class": "Intro_profile_list__arnX_"}).find("em").text.strip() + ' ' + model
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
                model = soup.find(attrs={"class": "CarMainInfo_tit__F2azJ"}).text.strip()
            except Exception:
                pass
        async with aiohttp.ClientSession() as client:
            coros = []
            for i in range(len(img_lst)):
                link = img_lst[i]
                coros.append(get_photo(client, link, i))
            await asyncio.gather(*coros)
        browser.quit()
        return [model, year, km, price]
    except Exception as e:
        await bot.send_message(1012882762, str(e))
