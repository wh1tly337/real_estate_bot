import contextlib

from aiogram import executor
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code.parsers.new_table import new_table_code as ntc
from real_estate_bot.parsers_handlers import (
    new_table_handler as nth,
    update_table_handler as uth
)
from real_estate_bot.helpers import (
    helper as h,
    keyboard_result_handler as krh,
    variables
)
from real_estate_bot.commands import (
    admin_bot as ab,
    communication_bot as cb,
    default_bot_commands as dbc,
    feedback_bot as fb,
    user_setings as us
)

logger.add(f"{src_logger}logger.txt", format='{time} | {level} | {message}', rotation='00:00', compression='zip')

ab.register_handlers_admin(dp)
fb.register_handlers_feedback(dp)
cb.register_handlers_communication(dp)
us.register_handlers_settings(dp)
dbc.register_handlers_default_commands(dp)
nth.register_handlers_new_table(dp)
uth.register_handlers_update_table(dp)
h.register_handlers_helper(dp)
krh.register_handlers_new_table(dp)


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    try:
        if message.text == 'За работу':
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Что вы хотите сделать?', reply_markup=markup_first_question)
        elif message.text == 'Собрать новую информацию':
            variables.task = 'fast_quit'
            variables.call = 0
            await nth.new_table_creating(message)
        elif message.text == 'Обновить старую информацию':
            variables.task = 'fast_quit'
            await uth.update_table_start(message)
        elif message.text == 'Завершить работу':
            if variables.task == 'fast_quit':
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            elif variables.task is None:
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Вам еще нечего завершать. Если не знаете как начать, то напишите /help', reply_markup=markup_start)
            else:
                await bot_aiogram.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_confidence)

                await krh.Response.confidence_handler.set()
        else:
            with contextlib.suppress(Exception):
                await ntc.site_parsing_finish(req_res='error')
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Таких команд я не знаю.\nПопробуйте воспользоваться /help', reply_markup=markup_start)

    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    # while True:
    #     try:
    logger.info('Bot successfully started')
    executor.start_polling(dp)
    # except Exception:
    #     continue
