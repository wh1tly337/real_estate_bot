import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.connectors import all_connections as ac
from main_code.workers import work_with_data_base as wwdb


class Response(StatesGroup):
    settings_handler = State()


async def settings_start(message: types.Message):
    message_text = \
        'Вы можете выбрать в каком формате будете получать результаты работы, чтобы каждый раз не выбирать его во время работы.\
        \nПотом этот выбор можно будет всегда поменять или отменить в этих же настройках.'
    await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_settings)
    await Response.settings_handler.set()


async def settings_handler(message: types.Message, state: FSMContext):
    settings_response = message.text
    await state.update_data(user_response=settings_response)
    point = True
    with contextlib.suppress(Exception):
        await ac.start_connection()
    if settings_response == '.csv':
        settings_response = 'csv'
        await wwdb.update_user_data_settings(settings_format=settings_response, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .csv формате.\nВы всегда можете это поменять в настройках'
    elif settings_response == '.xlsx':
        settings_response = 'xlsx'
        await wwdb.update_user_data_settings(settings_format=settings_response, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .xlsx формате.\nВы всегда можете это поменять в настройках'
    elif settings_response == '.txt':
        settings_response = 'txt'
        await wwdb.update_user_data_settings(settings_format=settings_response, user_id=message.chat.id)
        message_text = 'Отлично! Теперь все результаты моей работы будут приходить в .txt формате.\nВы всегда можете это поменять в настройках'
    elif settings_response == 'Все форматы':
        settings_response = 'all'
        await wwdb.update_user_data_settings(settings_format=settings_response, user_id=message.chat.id)
        message_text = 'Отлично! Теперь по окончании работы я буду присылать вам файлы во всех форматах.\nВы всегда можете это поменять в настройках'
    elif settings_response == 'Буду выбирать каждый раз':
        settings_response = None
        await wwdb.update_user_data_settings(settings_format=settings_response, user_id=message.chat.id)
        message_text = 'Отлично! Теперь по окончании работы я каждый раз буду спрашивать у вас в каком формате отправить файл.\nВы всегда можете это поменять в настройках'
    else:
        point = False
        message_text = 'Такой настойки нет. Попробуйте воспользоваться функцией еще раз. Лучше всего полбзоваться кнопками внизу клавиатуры'

    await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_start)

    await state.finish()
    with contextlib.suppress(Exception):
        await ac.close_connection()

    if point:
        logger.info(f"User - {message.chat.id} update his settings to {settings_response}")


def register_handlers_settings(dp: Dispatcher):  # noqa
    dp.register_message_handler(settings_start, commands=['settings'])
    dp.register_message_handler(settings_handler, state=Response.settings_handler)
