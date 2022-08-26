import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.parsers.update_table import update_table_code as utc
from main_code.workers import work_with_data_base as wwdb, work_with_files as wwf
from real_estate_bot.helpers import (
    helper as h,
    variables
)
from real_estate_bot.parsers_handlers import new_table_handler as nth


class Response(StatesGroup):
    continuation_handler = State()
    confidence_handler = State()
    safe_files_handler = State()
    # quit_response = State()


async def continuation_handler(message: types.Message, state: FSMContext):
    continue_response = message.text
    await state.update_data(user_response=continue_response)

    if continue_response == 'Да':
        await nth.new_table_creating(message, call=1)
    elif continue_response == 'Нет':
        await h.site_parser_end_with_settings(message)
        await state.finish()


# noinspection DuplicatedCode
async def confidence_handler(message: types.Message, state: FSMContext):
    confidence_response = message.text
    await state.update_data(user_response=confidence_response)

    if confidence_response == 'Да, уверен':
        if variables.task == 'new_table':
            variables.possibility = False
            check = await wwdb.get_data_from_data_base(from_where='check', row=None)

            if int(check) != 0:
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хотите получить объявления которые я успел найти?', reply_markup=markup_save_file)
                await Response.safe_files_handler.set()
            else:
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await wwdb.delete_advertisement_table()
                await wwf.file_deleting(from_where=variables.task)
                await state.finish()
                with contextlib.suppress(Exception):
                    await ac.close_connection()
                with contextlib.suppress(Exception):
                    await ac.close_driver()
        elif variables.task == 'update_table':
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Хотите получить таблицу с не до конца обновленными данными?', reply_markup=markup_save_file)
            await Response.safe_files_handler.set()

            with contextlib.suppress(Exception):
                await ac.close_driver()

    elif confidence_response == 'Нет, давай продолжим':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_quit)


# noinspection DuplicatedCode
async def safe_files_handler(message: types.Message, state: FSMContext):
    safe_file_response = message.text
    await state.update_data(user_response=safe_file_response)

    if safe_file_response == 'Да, хочу':
        if variables.task == 'new_table':
            await h.site_parser_end_with_settings(message)
            await state.finish()
        elif variables.task == 'update_table':
            await utc.table_parsing_finish()
            await h.table_parser_end_with_settings(message)
            await state.finish()
    elif safe_file_response == 'Нет, не хочу':
        if variables.task == 'new_table':
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            await wwdb.delete_advertisement_table()
            await wwf.file_deleting(from_where=variables.task)
            await state.finish()
            with contextlib.suppress(Exception):
                await ac.close_connection()
        elif variables.task == 'update_table':
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            await wwf.file_deleting(from_where=variables.task)
            await wwdb.delete_update_ad_table()
            await state.finish()
            with contextlib.suppress(Exception):
                await ac.close_connection()


# async def force_quit(message: types.Message, state: FSMContext):
#     quit_response = message.text
#     await state.update_data(user_response=quit_response)
#
#     if quit_response == 'Завершить работу':
#         await bot_aiogram.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)
#
#         await Answer.sure_response.set()


def register_handlers_new_table(dp: Dispatcher):  # noqa
    dp.register_message_handler(confidence_handler, state=Response.confidence_handler)
    dp.register_message_handler(safe_files_handler, state=Response.safe_files_handler)
    dp.register_message_handler(continuation_handler, state=Response.continuation_handler)
    # dp.register_message_handler(force_quit, state=Answer.quit_response)
