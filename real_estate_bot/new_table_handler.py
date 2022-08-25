import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    site_code as sc
)
from main_code.connectors import all_connections as ac
from real_estate_bot import (
    variables,
    keyboard_result_handler as krh
)

global id_url


class Answer(StatesGroup):
    new_table_site_response = State()
    response_as_link = State()


async def new_table(message: types.Message, call=0):
    variables.task = 'site'
    variables.possibility = True

    if call == 0:
        with contextlib.suppress(Exception):
            await ac.start_connection()
        await sc.site_parsing_start()

    await bot_aiogram.send_message(chat_id=message.chat.id, text="С какого сайта Вы хотите получить информацию?", reply_markup=markup_site_question, parse_mode="Markdown")
    await Answer.new_table_site_response.set()


async def new_table_response_handler(message: types.Message, state: FSMContext):
    site_response = message.text
    await state.update_data(user_response=site_response)

    if site_response == "УПН":
        await getting_site_link(message, status_url='upn')
    elif site_response == "ЦИАН":
        await getting_site_link(message, status_url='cian')
    elif site_response == "Яндекс Недвижимость":
        await getting_site_link(message, status_url='yandex')
    elif site_response == "Авито":
        await getting_site_link(message, status_url='avito')
    elif site_response == "Завершить работу":
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
        await state.finish()
        with contextlib.suppress(Exception):
            await ac.close_connection()


async def get_site_url(message: types.Message, state: FSMContext):
    user_response = message.text
    await state.update_data(user_response=user_response)

    point = 0

    if user_response[:14] == 'https://upn.ru' and id_url == 'upn':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с УПНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=1, url_upn=user_response, url_cian=None, url_yandex=None, url_avito=None, message=message)
    elif user_response[:19] == 'https://ekb.cian.ru' and id_url == 'cian':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с ЦИАНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=2, url_upn=None, url_cian=user_response, url_yandex=None, url_avito=None, message=message)
    elif user_response[:24] == 'https://realty.yandex.ru' and id_url == 'yandex':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Яндекс Недвижимости, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=3, url_upn=None, url_cian=None, url_yandex=user_response, url_avito=None, message=message)
    elif user_response[:20] == 'https://www.avito.ru' and id_url == 'avito':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Авито, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await sc.site_parsing_main(req_site=4, url_upn=None, url_cian=None, url_yandex=None, url_avito=user_response, message=message)
    elif user_response == 'Завершить работу':
        point = 1
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)
        await krh.Answer.sure_response.set()
    else:
        variables.task = 'fast_quit'
        point = 1
        await getting_site_link(message, status_url='error')

    if point == 0 and variables.possibility is True:
        await bot_aiogram.send_message(chat_id=message.chat.id, text="С этим сайтом я закончил, хотите добавить еще сайт для поиска?", reply_markup=markup_continue_question, parse_mode="Markdown")
        await krh.Answer.continue_response.set()


async def getting_site_link(message: types.Message, status_url):
    try:
        global id_url

        if status_url == 'upn':
            id_url = 'upn'
            message_text = 'Перейдите на сайт [УПН](https://upn.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'cian':
            id_url = 'cian'
            message_text = "Перейдите на сайт [ЦИАН](https://ekb.cian.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне"
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'yandex':
            id_url = 'yandex'
            message_text = 'Перейдите на сайт [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее' \
                           ' мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'avito':
            id_url = 'avito'
            message_text = 'Перейдите на сайт [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'error':
            message_text = 'Введена неверная ссылка. Пожалуйста проверьте правильность ссылки и отправьте ее мне.'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.response_as_link.set()

    except Exception as ex:
        logger.error(ex)


def register_handlers_new_table(dp: Dispatcher):
    dp.register_message_handler(new_table, commands=['new_table'])
    dp.register_message_handler(new_table_response_handler, state=Answer.new_table_site_response)
    dp.register_message_handler(get_site_url, state=Answer.response_as_link)
