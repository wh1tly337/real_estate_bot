import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    work_with_data_base as wwdb
)
from main_code.connectors import all_connections as ac


class Answer(StatesGroup):
    res_file_settings = State()


async def settings(message: types.Message):
    message_text = \
        'Вы можете выбрать в каком формате будете получать результаты работы, чтобы каждый раз не выбирать его во время работы.\
        \nПотом этот выбор можно будет всегда поменять или отменить в этих же настройках.'
    await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_settings)
    await Answer.res_file_settings.set()


async def settings_response(message: types.Message, state: FSMContext):
    res_file_settings = message.text
    await state.update_data(user_response=res_file_settings)
    point = True
    with contextlib.suppress(Exception):
        await ac.start_connection()
    if res_file_settings == '.csv':
        res_file_settings = 'csv'
        await wwdb.update_user_data_settings(settings_format=res_file_settings, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .csv формате.\nВы всегда можете это поменять в настройках'
    elif res_file_settings == '.xlsx':
        res_file_settings = 'xlsx'
        await wwdb.update_user_data_settings(settings_format=res_file_settings, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .xlsx формате.\nВы всегда можете это поменять в настройках'
    elif res_file_settings == '.txt':
        res_file_settings = 'txt'
        await wwdb.update_user_data_settings(settings_format=res_file_settings, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .txt формате.\nВы всегда можете это поменять в настройках'
    elif res_file_settings == 'Все форматы':
        res_file_settings = 'all'
        await wwdb.update_user_data_settings(settings_format=res_file_settings, user_id=message.chat.id)
        message_text = 'Отлично! Теперь по окончании работы я буду присылать вам файлы во всех форматах.\nВы всегда можете это поменять в настройках'
    elif res_file_settings == 'Буду выбирать каждый раз':
        res_file_settings = None
        await wwdb.update_user_data_settings(settings_format=res_file_settings, user_id=message.chat.id)
        message_text = 'Отлично! Теперь по окончании работы я каждый раз буду спрашивать у вас в каком формате отправить файл.\nВы всегда можете это поменять в настройках'
    else:
        point = False
        message_text = 'Такой настойки нет. Попробуйте воспользоваться функцией еще раз. Лучше всего полбзоваться кнопками внизу клавиатуры'

    await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_start)

    await state.finish()
    with contextlib.suppress(Exception):
        await ac.close_connection()

    if point:
        logger.info(f"User - {message.chat.id} update his settings to {res_file_settings}")


def register_handlers_settings(dp: Dispatcher):  # noqa
    dp.register_message_handler(settings, commands=['settings'])
    dp.register_message_handler(settings_response, state=Answer.res_file_settings)
