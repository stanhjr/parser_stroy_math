import datetime
import os
import urllib

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import ContentType
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from deploy.config import TOKEN
from parser import parser

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(content_types=['document'])
async def scan_message(msg: types.Message):
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    file_name = msg.document.file_name
    user_path = f'file/{msg.from_user.id}'
    copy_file_name = 'copy' + file_name
    os.makedirs(user_path, exist_ok=True)
    original_file_path = urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'{user_path}/{file_name}')
    copy_file_path = urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'{user_path}/{copy_file_name}')
    await bot.send_message(msg.from_user.id, 'Начинаю парсинг')
    copy_file = await parser(original_file_path[0], copy_file_path[0])
    await bot.send_document(msg.from_user.id, open(copy_file, 'rb'))
    os.remove(original_file_path[0])
    os.remove(copy_file_path[0])


@dp.message_handler()
async def file_handle(message: types.message):
    await bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)