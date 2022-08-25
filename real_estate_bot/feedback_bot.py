from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *


class Answer(StatesGroup):
    user_feedback = State()


async def feedback(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text='Если хотите, можете оставить отзыв', parse_mode="Markdown", reply_markup=markup_feedback)
    await Answer.user_feedback.set()


async def feedback_handler(message: types.Message, state: FSMContext):
    feedback_response = message.text
    await state.update_data(user_response=feedback_response)

    if feedback_response == 'Нет, обойдемся без отзывов':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', parse_mode="Markdown", reply_markup=markup_start)
        await state.finish()
    else:
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Спасибо за отзыв!', parse_mode="Markdown", reply_markup=markup_start)
        message_text = f"Отзыв от {message.from_user.full_name} / {message.from_user.username}\nid: {message.chat.id}\n\n{feedback_response}"
        await bot_aiogram.send_message(chat_id=admin_id, text=message_text, parse_mode="HTML", reply_markup=markup_start)
        logger.info('Received a feedback')

    await state.finish()


def register_handlers_feedback(dp: Dispatcher):  # noqa
    dp.register_message_handler(feedback, commands=['feedback'])
    dp.register_message_handler(feedback_handler, state=Answer.user_feedback)
