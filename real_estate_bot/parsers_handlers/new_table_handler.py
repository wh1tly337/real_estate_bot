import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.parsers.new_table import new_table_code as ntc
from real_estate_bot.helpers import keyboard_result_handler as krh, variables

global id_url


class Response(StatesGroup):
    new_table_site_selection_handler = State()
    site_link_handler = State()


async def new_table_creating(message: types.Message, call=0):
    variables.task = 'new_table'
    variables.possibility = True

    if call == 0:
        with contextlib.suppress(Exception):
            await ac.start_connection()
        await ntc.site_parsing_start()

    await bot_aiogram.send_message(chat_id=message.chat.id, text='С какого сайта Вы хотите получить информацию?', reply_markup=markup_site_selection, parse_mode='Markdown')
    await Response.new_table_site_selection_handler.set()


async def site_selection_handler(message: types.Message, state: FSMContext):
    site_selection_response = message.text
    await state.update_data(user_response=site_selection_response)

    if site_selection_response == 'УПН':
        await getting_site_selection(message, state, status_url='upn')
    elif site_selection_response == 'ЦИАН':
        await getting_site_selection(message, state, status_url='cian')
    elif site_selection_response == 'Яндекс Недвижимость':
        await getting_site_selection(message, state, status_url='yandex')
    elif site_selection_response == 'Авито':
        await getting_site_selection(message, state, status_url='avito')
    elif site_selection_response == 'Завершить работу':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
        await state.finish()
        with contextlib.suppress(Exception):
            await ac.close_connection()


async def site_link_handler(message: types.Message, state: FSMContext):
    site_link_response = message.text
    await state.update_data(user_response=site_link_response)

    point = 0

    if site_link_response[:14] == 'https://upn.ru' and id_url == 'upn':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с УПНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await ntc.site_parsing_main(req_site=1, url_upn=site_link_response, url_cian=None, url_yandex=None, url_avito=None, message=message)
    elif site_link_response[:19] == 'https://ekb.cian.ru' and id_url == 'cian':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с ЦИАНа, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await ntc.site_parsing_main(req_site=2, url_upn=None, url_cian=site_link_response, url_yandex=None, url_avito=None, message=message)
    elif site_link_response[:24] == 'https://realty.yandex.ru' and id_url == 'yandex':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Яндекс Недвижимости, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await ntc.site_parsing_main(req_site=3, url_upn=None, url_cian=None, url_yandex=site_link_response, url_avito=None, message=message)
    elif site_link_response[:20] == 'https://www.avito.ru' and id_url == 'avito':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Авито, это может занять некоторое время.\n\nПрогресс выполнения работы:')
        await ntc.site_parsing_main(req_site=4, url_upn=None, url_cian=None, url_yandex=None, url_avito=site_link_response, message=message)
    elif site_link_response == 'Завершить работу':
        point = 1
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_confidence)
        await krh.Response.confidence_handler.set()
    else:
        point = 1
        await getting_site_selection(message, state, status_url='error')

    if point == 0 and variables.possibility is True:
        await bot_aiogram.send_message(chat_id=message.chat.id, text='С этим сайтом я закончил, хотите добавить еще сайт для поиска?', reply_markup=markup_continuation_question, parse_mode='Markdown')
        await krh.Response.continuation_handler.set()


async def getting_site_selection(message: types.Message, state: FSMContext, status_url):
    try:
        global id_url

        if status_url == 'upn':
            id_url = 'upn'
            message_text = 'Перейдите на сайт [УПН](https://upn.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'cian':
            id_url = 'cian'
            message_text = 'Перейдите на сайт [ЦИАН](https://ekb.cian.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'yandex':
            id_url = 'yandex'
            message_text = 'Перейдите на сайт [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее' \
                           ' мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'avito':
            id_url = 'avito'
            message_text = 'Перейдите на сайт [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='MarkdownV2', disable_web_page_preview=True, reply_markup=markup_quit)
        elif status_url == 'error':
            message_text = 'Введена неверная ссылка. Пожалуйста проверьте правильность ссылки и отправьте ее мне.'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=markup_quit)
            await state.finish()

        await Response.site_link_handler.set()

    except Exception as ex:
        logger.error(ex)


def register_handlers_new_table(dp: Dispatcher):  # noqa
    dp.register_message_handler(new_table_creating, commands=['new_table'])
    dp.register_message_handler(site_selection_handler, state=Response.new_table_site_selection_handler)
    dp.register_message_handler(site_link_handler, state=Response.site_link_handler)
