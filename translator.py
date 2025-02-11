from translate import Translator
from bot import bot


async def trans(string):
    try:
        translator = Translator(from_lang="ko", to_lang="en")
        translation = translator.translate(string)
        return translation
    except Exception as e:
        await bot.send_message(1012882762, str(e))