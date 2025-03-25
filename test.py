import asyncio
import aiofiles
import aiohttp
from selenium.webdriver.chrome.options import Options
from translate import Translator
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import bs4
import time
import requests

# #kbchacha
res = requests.get('https://m.kcar.com/bc/detail/carInfoDtl?i_sCarCd=EC61151582')
html = res.text
soup = bs4.BeautifulSoup(html, 'lxml')
print(soup.prettify())
# imgs = soup.find(attrs={"id": "divCarPhotoList"}).find_all("img")
# for img in imgs:
#     print(img)
# title = soup.find(attrs={"property": "og:description"}).get('content')
# translator = Translator(from_lang="ko", to_lang="en")
# translation = translator.translate(title)
# price = soup.find(attrs={"class": "car-intro__cost-highlight"}).find('strong').text.strip()
# print(title)
# print(translation)
# print(price)

# res = requests.get('https://m.kcar.com/ur/RentDtl?rentCarCd=RC138499&rentMth=12&ecCarCd')
# html = res.text
# soup = bs4.BeautifulSoup(html, 'lxml')
# name = soup.find(attrs={"class": "carName"})
# print(name)


# chrome_driver_path = ChromeDriverManager().install()
# browser_service = Service(executable_path=chrome_driver_path)
# options = Options()
# options.add_argument("--start-maximized")
# options.page_load_strategy = 'eager'
# options.add_argument('--disable-blink-features=AutomationControlled')
# browser = Chrome(service=browser_service, options=options)
# browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#     'source': '''
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
#         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
#     '''
#     })
# res = []
# browser.get(f'https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.Mileage.range(80000..150000)._.Price.range(500..1700)._.(C.CarType.Y._.Manufacturer.%EC%A0%9C%EB%84%A4%EC%8B%9C%EC%8A%A4.))%22%2C%22title%22%3A%22%EC%A0%9C%EB%84%A4%EC%8B%9C%EC%8A%A4%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D')
# input()