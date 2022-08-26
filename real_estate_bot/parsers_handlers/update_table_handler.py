import contextlib

from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.parsers.table import table_parsing_code as tc
from main_code.workers import work_with_files as wwf
from real_estate_bot.helpers import variables


async def update_table_start(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text="Отправьте мне файл, информацию в котором Вы хотите обновить", reply_markup=markup_quit, parse_mode="Markdown")


async def docs_handler(message: types.Message):
    try:
        variables.task = 'table'

        with contextlib.suppress(Exception):
            await ac.start_connection()
        await tc.table_parsing_start()
        await message.document.download(destination_file=f"{src}{message.document.file_name}")
        await bot_aiogram.send_message(chat_id=message.chat.id, text="Отлично! Я начал обновлять информацию.\n\nПрогресс выполнения работы:", reply_markup=markup_quit, parse_mode="Markdown")

        variables.table_name, variables.table_name_upd = await wwf.table_name_handler(message)

        await tc.table_parsing_main(message)

    except Exception as ex:
        logger.error(ex)


def register_handlers_update_table(dp: Dispatcher):  # noqa
    dp.register_message_handler(update_table_start, commands=['update_table'])
    dp.register_message_handler(docs_handler, content_types=['document'])
