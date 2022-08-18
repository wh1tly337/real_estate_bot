import contextlib

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    work_with_data_base as wwdb,
    work_with_files as wwf,
    site_code as sc,
    all_connections as ac
)

global table_name_upd, table_name, task, possibility


async def file_sender(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваши файлы", reply_markup=markup_start)

    if task == 'site':
        result_file = await wwf.filename_creator(freshness='load')
        result_file = f"{src}{result_file}"
    else:
        result_file = table_name_upd

    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.csv", "rb"))
    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.xlsx", "rb"))
    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{result_file}.txt", "rb"))

    await req_to_upd_db(message)


async def table_parser_end_with_settings(message: types.Message):
    user_settings = await wwdb.get_user_settings(user_id=message.chat.id)
    if user_settings == "None":
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Вся информация обновлена. В каком формате вы хотите получить результат?',
                                       reply_markup=markup_result, parse_mode="Markdown")
    elif task == 'table':
        if user_settings == 'all':
            await table_all_res_finish(message)

        else:
            if user_settings == 'txt':
                await wwf.convert_csv_to_txt(from_where=task)
            elif user_settings == 'xlsx':
                await wwf.convert_csv_to_xlsx(from_where=task)

            await bot_aiogram.send_message(chat_id=message.chat.id, text=f"Ваш .{user_settings} файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.{user_settings}", "rb"))
            await end_of_work(message)


async def site_parser_end_with_settings(message: types.Message):
    user_settings = await wwdb.get_user_settings(user_id=message.chat.id)
    if user_settings == "None":
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                       reply_markup=markup_result)
    elif task == 'site':
        await sc.site_parsing_finish(req_res=user_settings)
        if user_settings == 'all':
            await sc.site_parsing_finish(req_res='all')
            await file_sender(message)
            await wwf.file_remover(from_where=task)
            await wwdb.delete_advertisement_table()
            with contextlib.suppress(Exception):
                await ac.close_connection()
        else:
            await bot_aiogram.send_message(chat_id=message.chat.id, text=f"Ваш .{user_settings} файл", reply_markup=markup_start)
            await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.{user_settings}", "rb"))
            await end_of_work(message)


async def end_of_work(message: types.Message):
    await req_to_upd_db(message)

    if task == 'site':
        await wwf.file_remover(from_where=task)
    elif task == 'table':
        await wwf.file_remover(from_where=task)
        await wwdb.delete_update_ad_table()

    with contextlib.suppress(Exception):
        await ac.close_connection()


async def table_all_res_finish(message):
    await wwf.convert_csv_to_xlsx(from_where=task)
    await wwf.convert_csv_to_txt(from_where=task)
    await file_sender(message)
    await wwf.file_remover(from_where=task)
    await wwdb.delete_update_ad_table()
    with contextlib.suppress(Exception):
        await ac.close_connection()


async def req_to_upd_db(message: types.Message):
    if task == 'site':
        await wwdb.update_user_data(
            user_id=message.chat.id,
            num_site_req=True,
            num_table_req=False,
            date_last_site_req=await wwf.filename_creator(freshness='load'),
            date_last_table_req=False
        )
    else:
        await wwdb.update_user_data(
            user_id=message.chat.id,
            num_site_req=False,
            num_table_req=True,
            date_last_site_req=False,
            date_last_table_req=await wwf.filename_creator(freshness='new')
        )
