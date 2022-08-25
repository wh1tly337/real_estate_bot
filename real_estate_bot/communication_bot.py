from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *

global communication_id_response


class Answer(StatesGroup):
    communication_id = State()
    communication_message = State()


async def communication_id(message: types.Message, state: FSMContext):
    global communication_id_response

    communication_id_response = message.text
    await state.update_data(user_response=communication_id_response)

    if communication_id_response == 'Отмена':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', parse_mode="Markdown", reply_markup=markup_start)
        await state.finish()
    else:
        message_text = 'Введите сообщение для пользователя'
        await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_communication)
        await Answer.communication_message.set()


async def communication_message(message: types.Message, state: FSMContext):
    communication_message_response = message.text
    await state.update_data(user_response=communication_message_response)

    if communication_id_response == 'Отмена':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', parse_mode="Markdown", reply_markup=markup_start)
        await state.finish()
    else:
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Сообщение отправлено', parse_mode="Markdown", reply_markup=markup_start)
        message_text = f"Сообщение от админа этого бота:\n\n{communication_message_response}"
        await bot_aiogram.send_message(chat_id=communication_id_response, text=message_text, parse_mode="Markdown", reply_markup=markup_communication)
        logger.info(f"Communication has been made with {communication_id_response}")

    await state.finish()


def register_handlers_communication(dp: Dispatcher):
    dp.register_message_handler(communication_id, state=Answer.communication_id)
    dp.register_message_handler(communication_message, state=Answer.communication_message)
