import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.parsers.site import site_parsing_code as sc
from main_code.workers import work_with_data_base as wwdb, work_with_files as wwf
from real_estate_bot.helpers import variables


class Response(StatesGroup):
    file_format_handler = State()


async def file_format_handler(message: types.Message, state: FSMContext):
    file_format_response = message.text
    await state.update_data(user_response=file_format_response)

    if message.text == ".csv":
        if variables.task == 'site':
            await sc.site_parsing_finish(req_res='csv')
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.creating_filename(freshness='load')}.csv", "rb"))
            await end_of_work(message)
        elif variables.task == 'table':
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{variables.table_name_upd}.csv", "rb"))
            await end_of_work(message)
    elif message.text == ".xlsx":
        if variables.task == 'site':
            await sc.site_parsing_finish(req_res='xlsx')
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.creating_filename(freshness='load')}.xlsx", "rb"))
            await end_of_work(message)
        elif variables.task == 'table':
            await wwf.converting_csv_to_xlsx(from_where=variables.task)
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{variables.table_name_upd}.xlsx", "rb"))
            await end_of_work(message)
    elif message.text == ".txt":
        if variables.task == 'site':
            await sc.site_parsing_finish(req_res='txt')
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.creating_filename(freshness='load')}.txt", "rb"))
            await end_of_work(message)
        elif variables.task == 'table':
            await wwf.converting_csv_to_txt(from_where=variables.task)
            await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{variables.table_name_upd}.txt", "rb"))
            await end_of_work(message)
    elif message.text == "Все форматы":
        if variables.task == 'site':
            await sc.site_parsing_finish(req_res='all')
            await file_sender(message)
            await wwf.file_deleting(from_where=variables.task)
            await wwdb.delete_advertisement_table()
            with contextlib.suppress(Exception):
                await ac.close_connection()
        elif variables.task == 'table':
            await table_all_formats_finish(message)

    await state.finish()


async def file_sender(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваши файлы", reply_markup=markup_start)

    if variables.task == 'site':
        result_file = await wwf.creating_filename(freshness='load')
        result_file = f"{src}{result_file}"
    else:
        result_file = variables.table_name_upd

    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.csv", "rb"))
    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.xlsx", "rb"))
    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.txt", "rb"))
    await req_to_upd_db(message)


async def table_parser_end_with_settings(message: types.Message):
    user_settings = await wwdb.get_user_settings(user_id=message.chat.id)
    if user_settings == "None":
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Вся информация обновлена. В каком формате вы хотите получить результат?',
                                       reply_markup=markup_result, parse_mode="Markdown")
        await Response.file_format_handler.set()
    elif variables.task == 'table':
        if user_settings == 'all':
            await table_all_formats_finish(message)
        else:
            if user_settings == 'txt':
                await wwf.converting_csv_to_txt(from_where=variables.task)
            elif user_settings == 'xlsx':
                await wwf.converting_csv_to_xlsx(from_where=variables.task)

            await bot_aiogram.send_message(chat_id=message.chat.id, text=f"Ваш .{user_settings} файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{variables.table_name_upd}.{user_settings}", "rb"))
            await end_of_work(message)


async def site_parser_end_with_settings(message: types.Message):
    user_settings = await wwdb.get_user_settings(user_id=message.chat.id)
    if user_settings == "None":
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?', reply_markup=markup_result)
        await Response.file_format_handler.set()
    elif variables.task == 'site':
        await sc.site_parsing_finish(req_res=user_settings)
        if user_settings == 'all':
            await sc.site_parsing_finish(req_res='all')
            await file_sender(message)
            await wwf.file_deleting(from_where=variables.task)
            await wwdb.delete_advertisement_table()
            with contextlib.suppress(Exception):
                await ac.close_connection()
        else:
            await bot_aiogram.send_message(chat_id=message.chat.id, text=f"Ваш .{user_settings} файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.creating_filename(freshness='load')}.{user_settings}", "rb"))
            await end_of_work(message)


async def end_of_work(message: types.Message):
    await req_to_upd_db(message)

    if variables.task == 'site':
        await wwf.file_deleting(from_where=variables.task)
    elif variables.task == 'table':
        await wwf.file_deleting(from_where=variables.task)
        await wwdb.delete_update_ad_table()

    with contextlib.suppress(Exception):
        await ac.close_connection()


async def table_all_formats_finish(message):
    await wwf.converting_csv_to_xlsx(from_where=variables.task)
    await wwf.converting_csv_to_txt(from_where=variables.task)
    await file_sender(message)
    await wwf.file_deleting(from_where=variables.task)
    await wwdb.delete_update_ad_table()
    with contextlib.suppress(Exception):
        await ac.close_connection()


async def req_to_upd_db(message: types.Message):
    if variables.task == 'site':
        await wwdb.update_user_data(
            user_id=message.chat.id,
            num_site_req=True,
            num_table_req=False,
            date_last_site_req=await wwf.creating_filename(freshness='load'),
            date_last_table_req=False
        )
    else:
        await wwdb.update_user_data(
            user_id=message.chat.id,
            num_site_req=False,
            num_table_req=True,
            date_last_site_req=False,
            date_last_table_req=await wwf.creating_filename(freshness='new')
        )


def register_handlers_helper(dp: Dispatcher):  # noqa
    dp.register_message_handler(file_format_handler, state=Response.file_format_handler)
