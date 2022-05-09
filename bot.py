import os
import urllib

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from deploy.config import TOKEN
from new_parser import all_parsing

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands='start')
async def scan_message(msg: types.Message):
    await bot.send_message(chat_id=msg.chat.id, text="Жду файл для обработки, формат файла xlsx")


@dp.message_handler(content_types=['document'])
async def scan_message(msg: types.Message):
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    file_name = msg.document.file_name
    type_file = file_name.split('.')[-1]
    user_path = f'file/{msg.from_user.id}'
    if type_file != 'xlsx':
        await bot.send_message(msg.from_user.id, "Данный формат файла не поддердивается, работаем только с xlsx")
    elif os.path.exists(f'{user_path}/{file_name}'):
        await bot.send_message(msg.from_user.id, "Я уже работаю с этим файлом")
    else:
        try:
            user_path = f'file/{msg.from_user.id}'
            copy_file_name = 'copy' + file_name
            os.makedirs(user_path, exist_ok=True)
            original_file_path = urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',
                                                            f'{user_path}/{file_name}')
            copy_file_path = urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',
                                                        f'{user_path}/{copy_file_name}')
            await bot.send_message(msg.from_user.id, 'Начинаю парсинг')
            copy_file = await all_parsing(original_file_path[0], copy_file_path[0])
            await bot.send_document(msg.from_user.id, open(copy_file, 'rb'))
        except Exception as e:
            text = "Что то пошло не так\nОшибка\n" + str(e)
            await bot.send_message(msg.from_user.id, text)
        finally:
            os.remove(original_file_path[0])
            os.remove(copy_file_path[0])


@dp.message_handler()
async def file_handle(message: types.message):
    text = 'Это функция, для демонстрации асинхронной работы\nВаше сообщение\n' + message.text
    await bot.send_message(message.chat.id, text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
