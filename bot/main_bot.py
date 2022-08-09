import contextlib

from aiogram import executor
from aiogram.dispatcher import FSMContext
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

global table_name_upd, table_name, id_url, task, possibility


class Answer(StatesGroup):
    response_as_link = State()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"{message.from_user.full_name}, добро пожаловать в бот помощник по недвижимости!\
                     \nЯ в любое время могу собирать информацию о необходимых тебе объектах.\
                     \nТакже я могу подыскать информацию по любым указанными тобой параметрам.\
                     \nСобирать всю эту информацию в удобном тебе виде и обновлять ее по твоему желанию.\
                     \nВо время использования моего функционала, пользуйтесь кнопками снизу клавиатуры, Вам так будет намного удобнее.\
                     \n\nДля того чтобы узнать все мои команды нажмите на кнопку /help на клавиатуре.", reply_markup=markup_start)


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='Доступные команды:\
            \n/links - узнать сайты с которыми я могу работать и их ссылки\
            \n/new_table - собрать новую информацию по вашим параметрам\
            \n/update_table - обновить информацию уже по имеющейся базе данных\
            \n/feedback - отправка отзыва, пожелания, замечания или бага\
            \n/settings - мои настройки')


@dp.message_handler(commands=['links'])
async def links(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="На данный момент я работаю с сайтами:\
            \n• [УПН](https://upn.ru)\
            \n• [ЦИАН](https://ekb.cian.ru)\
            \n• [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg)\
            \n• [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost)", disable_web_page_preview=True, parse_mode="MarkdownV2")


@dp.message_handler(commands=['new_table'])
async def new_table(message: types.Message, call=0):
    global task, possibility

    task = 'site'
    possibility = True

    if call == 0:
        await ac.start_connection()
        await sc.site_parsing_start()

    await bot.send_message(chat_id=message.chat.id, text="С какого сайта Вы хотите получить информацию?", reply_markup=markup_site_question, parse_mode="Markdown")


@dp.message_handler(commands=['update_table'])
async def update_table(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Отправьте мне файл, информацию в котором Вы хотите обновить", reply_markup=markup_quit, parse_mode="Markdown")


@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    try:
        global table_name, table_name_upd, task

        task = 'table'

        await ac.start_connection()
        await tc.table_parsing_start()

        await message.document.download(destination_file=f"{src}{message.document.file_name}")

        await bot.send_message(chat_id=message.chat.id, text="Отлично! Я начал обновлять информацию.\n\nПрогресс выполнения работы:", reply_markup=markup_quit, parse_mode="Markdown")

        table_name, table_name_upd = await wwf.table_name_handler(message)

        await tc.table_parsing_main(message)

    except Exception as ex:
        print('[ERROR] [HANDLE_DOCS] - ', ex)


@dp.message_handler(state=Answer.response_as_link)
async def get_site_url(message: types.Message, state: FSMContext):
    global task

    user_response = message.text
    await state.update_data(user_response=user_response)

    point = 0

    if user_response[:14] == 'https://upn.ru' and id_url == 'upn':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с УПНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=1, url_upn=user_response, url_cian=None, url_yandex=None, url_avito=None, message=message)
    elif user_response[:19] == 'https://ekb.cian.ru' and id_url == 'cian':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с ЦИАНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=2, url_upn=None, url_cian=user_response, url_yandex=None, url_avito=None, message=message)
    elif user_response[:24] == 'https://realty.yandex.ru' and id_url == 'yandex':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Яндекс Недвижимости, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=3, url_upn=None, url_cian=None, url_yandex=user_response, url_avito=None, message=message)
    elif user_response[:20] == 'https://www.avito.ru' and id_url == 'avito':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Авито, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=4, url_upn=None, url_cian=None, url_yandex=None, url_avito=user_response, message=message)
    elif user_response == 'Завершить работу':
        point = 1
        await bot.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)
    else:
        task = 'fast_quit'
        point = 1
        await getting_site_link(message, status_url='error')

    if point == 0 and possibility is True:
        await bot.send_message(chat_id=message.chat.id, text="С этим сайтом я закончил, хотите добавить еще сайт для поиска?", reply_markup=markup_continue_question, parse_mode="Markdown")
    await state.finish()


async def getting_site_link(message: types.Message, status_url):
    try:
        global id_url

        if status_url == 'upn':
            id_url = 'upn'
            message_text = 'Перейдите на сайт [УПН](https://upn.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

            await Answer.response_as_link.set()
        elif status_url == 'cian':
            id_url = 'cian'
            message_text = "Перейдите на сайт [ЦИАН](https://ekb.cian.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне"
            await bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

            await Answer.response_as_link.set()
        elif status_url == 'yandex':
            id_url = 'yandex'
            message_text = 'Перейдите на сайт [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее' \
                           ' мне'
            await bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

            await Answer.response_as_link.set()
        elif status_url == 'avito':
            id_url = 'avito'
            message_text = 'Перейдите на сайт [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

            await Answer.response_as_link.set()
        elif status_url == 'error':
            message_text = 'Введена неверная ссылка. Пожалуйста проверьте правильность ссылки и отправьте ее мне.'
            await bot.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup_quit)

            await Answer.response_as_link.set()

    except Exception as ex:
        print('[ERROR] [GETTING_SITE_LINK] - ', ex)


async def file_sender(message: types.Message, call):
    await bot.send_message(chat_id=message.chat.id, text="Ваши файлы", reply_markup=markup_start)

    if call == 'site':
        result_file = await wwf.filename_creator(freshness='load')
        result_file = f"{src}{result_file}"
    else:
        result_file = table_name_upd

    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.csv", "rb"))
    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.xlsx", "rb"))
    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.txt", "rb"))


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    global task

    try:
        if message.text == "За работу":
            await bot.send_message(chat_id=message.chat.id, text='Что вы хотите сделать?', reply_markup=markup_first_question)
        elif message.text == "Собрать новую информацию":
            task = 'fast_quit'
            await new_table(message, call=0)
        elif message.text == "Обновить старую информацию":
            task = 'fast_quit'
            await update_table(message)

        elif message.text == "УПН":
            await getting_site_link(message, status_url='upn')
        elif message.text == "ЦИАН":
            await getting_site_link(message, status_url='cian')
        elif message.text == "Яндекс Недвижимость":
            await getting_site_link(message, status_url='yandex')
        elif message.text == "Авито":
            await getting_site_link(message, status_url='avito')
        elif message.text == "Завершить работу":
            if task == 'fast_quit':
                await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            else:
                await bot.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)

        elif message.text == "Да, уверен":
            global possibility

            if task == 'site':
                possibility = False
                check = await wwdb.get_data_from_data_base(from_where='check', row=None)

                if int(check) != 0:
                    await bot.send_message(chat_id=message.chat.id, text='Хотите получить объявления которые я успел найти?',
                                           reply_markup=markup_save_file)
                else:
                    await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                    await wwdb.delete_advertisement_table()
                    await wwf.file_remover(from_where='site')
                    with contextlib.suppress(Exception):
                        await ac.close_connection()
                    with contextlib.suppress(Exception):
                        await ac.close_driver()
            elif task == 'table':
                await bot.send_message(chat_id=message.chat.id, text='Хотите получить таблицу с не до конца обновленными данными?',
                                       reply_markup=markup_save_file)
        elif message.text == "Нет, давай продолжим":
            await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_quit)

        elif message.text == "Да, хочу":
            if task == 'site':
                await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                       reply_markup=markup_result)
            elif task == 'table':
                await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                       reply_markup=markup_result)
                await tc.table_parsing_finish()
        elif message.text == "Нет, не хочу":
            if task == 'site':
                await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await wwdb.delete_advertisement_table()
                await wwf.file_remover(from_where='site')
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await wwf.file_remover(from_where='table')
                await wwdb.delete_update_ad_table()
                await ac.close_connection()

        elif message.text == "Да":
            await new_table(message, call=1)
        elif message.text == "Нет":
            await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                   reply_markup=markup_result)

        elif message.text == ".csv":
            if task == 'site':
                await sc.site_parsing_finish(req_res='csv')
                await bot.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.csv", "rb"))
                await wwf.file_remover(from_where='site')
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await bot.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.csv", "rb"))
                await wwf.file_remover(from_where='table')
                await wwdb.delete_update_ad_table()
                await ac.close_connection()
        elif message.text == ".xlsx":
            if task == 'site':
                await sc.site_parsing_finish(req_res='xlsx')
                await bot.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.xlsx", "rb"))
                await wwf.file_remover(from_where='site')
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await wwf.convert_csv_to_xlsx(from_where='table')
                await bot.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.xlsx", "rb"))
                await wwf.file_remover(from_where='table')
                await wwdb.delete_update_ad_table()
                await ac.close_connection()
        elif message.text == ".txt":
            if task == 'site':
                await sc.site_parsing_finish(req_res='txt')
                await bot.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{src}{await wwf.filename_creator(freshness='load')}.txt", "rb"))
                await wwf.file_remover(from_where='site')
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await wwf.convert_csv_to_txt(from_where='table')
                await bot.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
                await bot.send_document(chat_id=message.chat.id, document=open(f"{table_name_upd}.txt", "rb"))
                await wwf.file_remover(from_where='table')
                await wwdb.delete_update_ad_table()
                await ac.close_connection()
        elif message.text == "Все форматы":
            if task == 'site':
                await sc.site_parsing_finish(req_res='all')
                await file_sender(message, call=task)
                await wwf.file_remover(from_where='site')
                with contextlib.suppress(Exception):
                    await ac.close_connection()
            elif task == 'table':
                await wwf.convert_csv_to_xlsx(from_where='table')
                await wwf.convert_csv_to_txt(from_where='table')
                await file_sender(message, call=task)
                await wwf.file_remover(from_where='table')
                await wwdb.delete_update_ad_table()
                await ac.close_connection()
        else:
            with contextlib.suppress(Exception):
                await sc.site_parsing_finish(req_res='error')
            await bot.send_message(chat_id=message.chat.id, text='Таких команд я не знаю 😔\nПопробуй воспользоваться /help', reply_markup=markup_start)

    except Exception as ex:
        print('[ERROR] [TEXT MESSAGES] - ', ex)


if __name__ == '__main__':
    # while True:
    #     try:
    print('[INFO] - Bot successfully started')
    executor.start_polling(dp)
    # except Exception:
    #     continue
