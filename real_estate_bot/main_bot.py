import contextlib

from aiogram import executor
from loguru import logger
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    work_with_data_base as wwdb,
    work_with_files as wwf,
    table_code as tc,
    site_code as sc,
    all_connections as ac
)
from real_estate_bot import (
    admin_bot as ab,
    feedback_bot as fb,
    communication_bot as cb,
    user_setings as us,
    default_bot_commands as dbc,
    new_table_handler as nth,
    update_table_handler as uth,
    helper as h
)

global table_name_upd, table_name, task, possibility

logger.add(f"{src_logger}logger.txt", format='{time} | {level} | {message}', rotation='00:00', compression='zip')


class Answer(StatesGroup):
    response_as_link = State()
    admin_panel = State()
    response_as_password = State()
    user_feedback = State()
    communication_id = State()
    communication_message = State()
    res_file_settings = State()


ab.register_handlers_admin(dp)
fb.register_handlers_feedback(dp)
cb.register_handlers_communication(dp)
us.register_handlers_settings(dp)
dbc.register_handlers_default_commands(dp)
nth.register_handlers_new_table(dp)
uth.register_handlers_update_table(dp)


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    global task

    try:
        if message.text == "За работу":
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Что вы хотите сделать?', reply_markup=markup_first_question)
        elif message.text == "Собрать новую информацию":
            task = 'fast_quit'
            await nth.new_table(message, call=0)
        elif message.text == "Обновить старую информацию":
            task = 'fast_quit'
            await uth.update_table(message)

        elif message.text == "УПН":
            await nth.getting_site_link(message, status_url='upn')
        elif message.text == "ЦИАН":
            await nth.getting_site_link(message, status_url='cian')
        elif message.text == "Яндекс Недвижимость":
            await nth.getting_site_link(message, status_url='yandex')
        elif message.text == "Авито":
            await nth.getting_site_link(message, status_url='avito')
        elif message.text == "Завершить работу":
            if task == 'fast_quit':
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            else:
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)

        elif message.text == "Да, уверен":
            global possibility

            if task == 'site':
                possibility = False
                check = await wwdb.get_data_from_data_base(from_where='check', row=None)

                if int(check) != 0:
                    await bot_aiogram.send_message(chat_id=message.chat.id, text='Хотите получить объявления которые я успел найти?',
                                                   reply_markup=markup_save_file)
                else:
                    await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                    await wwdb.delete_advertisement_table()
                    await wwf.file_remover(from_where=task)
                    with contextlib.suppress(Exception):
                        await ac.close_connection()
                    with contextlib.suppress(Exception):
                        await ac.close_driver()
            elif task == 'table':
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хотите получить таблицу с не до конца обновленными данными?',
                                               reply_markup=markup_save_file)
                with contextlib.suppress(Exception):
                    await ac.close_driver()
        elif message.text == "Нет, давай продолжим":
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_quit)

        elif message.text == "Да, хочу":
            if task == 'site':
                await h.site_parser_end_with_settings(message)
            elif task == 'table':
                await tc.table_parsing_finish()
                await h.table_parser_end_with_settings(message)
        elif message.text == "Нет, не хочу":
            if task == 'site':
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await wwdb.delete_advertisement_table()
                await wwf.file_remover(from_where=task)
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await wwf.file_remover(from_where=task)
                await wwdb.delete_update_ad_table()
                with contextlib.suppress(Exception):
                    await ac.close_connection()

        elif message.text == "Да":
            await nth.new_table(message, call=1)
        elif message.text == "Нет":
            await h.site_parser_end_with_settings(message)

        elif message.text == ".csv":
            if task == 'site':
                await sc.site_parsing_finish(req_res='csv')
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.csv", "rb"))
                await h.end_of_work(message)
            elif task == 'table':
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.csv", "rb"))
                await h.end_of_work(message)
        elif message.text == ".xlsx":
            if task == 'site':
                await sc.site_parsing_finish(req_res='xlsx')
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.xlsx", "rb"))
                await h.end_of_work(message)
            elif task == 'table':
                await wwf.convert_csv_to_xlsx(from_where=task)
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.xlsx", "rb"))
                await h.end_of_work(message)
        elif message.text == ".txt":
            if task == 'site':
                await sc.site_parsing_finish(req_res='txt')
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.txt", "rb"))
                await h.end_of_work(message)
            elif task == 'table':
                await wwf.convert_csv_to_txt(from_where=task)
                await bot_aiogram.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
                await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.txt", "rb"))
                await h.end_of_work(message)
        elif message.text == "Все форматы":
            if task == 'site':
                await sc.site_parsing_finish(req_res='all')
                await h.file_sender(message)
                await wwf.file_remover(from_where=task)
                await wwdb.delete_advertisement_table()
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await h.table_all_res_finish(message)
        else:
            with contextlib.suppress(Exception):
                await sc.site_parsing_finish(req_res='error')
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Таких команд я не знаю.\nПопробуй воспользоваться /help', reply_markup=markup_start)

    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    # while True:
    #     try:
    logger.info('Bot successfully started')
    executor.start_polling(dp)
    # except Exception:
    #     continue
