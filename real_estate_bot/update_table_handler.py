import contextlib

from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    work_with_files as wwf,
    table_code as tc
)
from main_code.connectors import all_connections as ac
from real_estate_bot import variables


async def update_table(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text="Отправьте мне файл, информацию в котором Вы хотите обновить", reply_markup=markup_quit, parse_mode="Markdown")


async def handle_docs(message: types.Message):
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
    dp.register_message_handler(update_table, commands=['update_table'])
    dp.register_message_handler(handle_docs, content_types=['document'])
