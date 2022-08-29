import contextlib

from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.workers import work_with_data_base as wwdb


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    with contextlib.suppress(Exception):
        await ac.start_connection()

    all_users = await wwdb.get_data_from_data_base(from_where='start', row=None)

    if message.chat.id not in all_users:
        await wwdb.user_data(
            user_id=message.chat.id,
            user_full_name=message.from_user.full_name,
            user_username=message.from_user.username,
            settings=None,
            num_site_req=0,
            num_table_req=0,
            date_last_site_req=0,
            date_last_table_req=0
        )

        logger.info('New user add')

    with contextlib.suppress(Exception):
        await ac.close_connection()

    await bot_aiogram.send_message(chat_id=message.chat.id, text=f'{message.from_user.full_name}, добро пожаловать в бот помощник по недвижимости!\
                     \nЯ в любое время могу собирать информацию о необходимых тебе объектах.\
                     \nТакже я могу подыскать информацию по любым указанными тобой параметрам.\
                     \nСобирать всю эту информацию в удобном тебе виде и обновлять ее по твоему желанию.\
                     \nВо время использования моего функционала, пользуйтесь кнопками снизу клавиатуры, так будет намного удобнее.\
                     \n\nДля того чтобы узнать все мои команды нажмите на кнопку /help на клавиатуре', reply_markup=markup_start)


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text='Доступные команды:\
            \n/links - узнать сайты с которыми я могу работать и их ссылки\
            \n/new_table - собрать новую информацию по вашим параметрам\
            \n/update_table - обновить информацию уже по имеющейся базе данных\
            \n/feedback - отправка отзыва, пожелания, замечания или бага для этого бота\
            \n/manual - получение инструкции по пользованию ботом\
            \n/settings - ваши настройки', reply_markup=markup_start)


@dp.message_handler(commands=['links'])
async def getting_links(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text='На данный момент я работаю с сайтами:\
            \n• [УПН](https://upn.ru)\
            \n• [ЦИАН](https://ekb.cian.ru)\
            \n• [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg)\
            \n• [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost)', disable_web_page_preview=True, parse_mode='MarkdownV2', reply_markup=markup_start)


@dp.message_handler(commands=['manual'])
async def getting_manual(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text='Инструкция пользования ботом', parse_mode='Markdown', reply_markup=markup_start)
    await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}MANUAL.txt"))

    logger.info(f"User {message.chat.id} received the instruction")


def register_handlers_default_commands(dp: Dispatcher):  # noqa
    dp.register_message_handler(start_message, commands=['start'])
    dp.register_message_handler(help_message, commands=['help'])
    dp.register_message_handler(getting_links, commands=['links'])
