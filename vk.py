import requests
from vk_api import VkApi, ApiError

from bot import bot
from config import VK_CHANEL, VK_TOKEN


async def vk_post(text):
    token = VK_TOKEN
    group_id = VK_CHANEL
    # Создаем объект VkApi
    vk_session = VkApi(token=token)

    # Получаем объект VK_API
    vk = vk_session.get_api()

    try:
        # Получаем URL для загрузки фото на стену
        upload_url = vk.photos.getWallUploadServer(group_id=group_id)['upload_url']
        attachment = []

        # Прикрепление изображений, если они есть
        for i in range(1, 11):
            # Загружаем фото на сервер VK
            with open(f'pics/{i}.jpg', 'rb') as photo_file:
                response = requests.post(upload_url, files={'photo': photo_file}).json()

            # Сохраняем фото на сервере VK
            save_result = vk.photos.saveWallPhoto(
                group_id=group_id,
                photo=response['photo'],
                server=response['server'],
                hash=response['hash']
            )

            # Формируем данные о загруженном фото
            photo_data = save_result[0]
            attachment.append(f"photo{photo_data['owner_id']}_{photo_data['id']}")
        attachment = ', '.join(attachment)
        # Публикуем пост на стене сообщества
        vk.wall.post(
            owner_id=f"-{group_id}",  # ID сообщества с отрицательным знаком
            message=text,
            attachments=attachment,
            from_group=1  # Публикация от имени сообщества
        )

    except ApiError as e:
        await bot.send_message(1012882762, f"Ошибка VK API: {e}")
    except Exception as e:
        await bot.send_message(1012882762, f"Общая ошибка при публикации в ВК: {e}")

