import datetime
import json
import shutil

from config import DELTA


def json_maker(car_list, text):
    try:
        with open('korea.json', 'r', encoding='utf-8') as f:
            dct = json.load(f)
            res = dct['data']['items']
    except:
        res = []
    model = car_list[0]
    year = int(car_list[1])
    km = ''
    km_ = car_list[2]
    for k in km_:
        if k.isdigit():
            km += k
    km = int(km)
    price_usd = int(car_list[3])
    img_lst = car_list[4]
    time_pars = car_list[5] + datetime.timedelta(hours=DELTA)
    time_pars_msk = time_pars.strftime('%Y-%m-%d %H:%M:%S')
    photos = []
    for i in range(len(img_lst)):
        photos.append({'photo_url': img_lst[i]})
    res.append({
        'model': model,
        'km': km,
        'year': year,
        'price_usd': price_usd,
        'photos': photos,
        'text': text,
        'time_stamp_msk': time_pars_msk
    })
    dct = {'data': {'items': res}}
    json_object = json.dumps(dct, indent=4)
    with open(f'korea.json', 'w', encoding='utf-8') as f:
        f.write(json_object)
    shutil.copy('korea.json', '/var/www/html/storage/korea.json')
