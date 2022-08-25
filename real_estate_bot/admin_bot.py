import contextlib

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from main_code import (
    work_with_data_base as wwdb,
    work_with_files as wwf
)
from main_code.connectors import all_connections as ac
from real_estate_bot import (
    communication_bot as cb
)


class Response(StatesGroup):
    admin_panel_main = State()
    admin_password_handler = State()


async def admin_panel_start(message: types.Message):
    await bot_aiogram.send_message(chat_id=message.chat.id, text='Введите пароль', parse_mode="Markdown", reply_markup=markup_start)
    await Response.admin_password_handler.set()


async def admin_password_handler(message: types.Message, state: FSMContext):
    admin_password_response = message.text
    await state.update_data(user_response=admin_password_response)

    if admin_password_response == admin_password:
        if message.chat.id == admin_id:
            logger.info('Admin logged in')
            message_text = 'Добро пожаловать. Что вы хотите сделать?'
            await bot_aiogram.send_message(chat_id=admin_id, text=message_text, parse_mode="Markdown", reply_markup=markup_admin)
            await Response.admin_panel_main.set()
        else:
            logger.info(f"Fake admin ({message.chat.id}) logged in. Need to change password!")
            message_text = 'Попытка хорошая, но вы не админ, так что даже не пытайтесь)'
            await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_start)
            message_text = f"Нас взломали! Нужно менять пароль!\nВзломщик - {message.chat.id}"
            await bot_aiogram.send_message(chat_id=admin_id, text=message_text, parse_mode="Markdown", reply_markup=markup_admin)
    else:
        message_text = 'Неверный пароль. Чтобы попробовать заново введите /admin'
        await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_start)


async def admin_panel_main(message: types.Message, state: FSMContext):
    admin_response = message.text
    await state.update_data(user_response=admin_response)

    if admin_response == "Получить базу данных":
        with contextlib.suppress(Exception):
            await ac.start_connection()
        await wwdb.get_user_data_table()
        await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src}user_data.csv"), reply_markup=markup_start)
        logger.info('Admin get user-data table')
        await wwf.file_deleting(from_where='admin')
        with contextlib.suppress(Exception):
            await ac.close_connection()
        await state.finish()
    elif admin_response == "Получить логгер":
        logger.info('Admin get logg file')
        await bot_aiogram.send_document(chat_id=message.chat.id, document=open(f"{src_logger}logger.txt"), reply_markup=markup_start)
        await state.finish()
    elif admin_response == "Написать пользователю":
        message_text = 'Введите id пользователя которому хотите написать'
        await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode="Markdown", reply_markup=markup_communication)
        await cb.Response.communication_id_handler.set()


def register_handlers_admin(dp: Dispatcher):  # noqa
    dp.register_message_handler(admin_panel_start, commands=['admin'])
    dp.register_message_handler(admin_password_handler, state=Response.admin_password_handler)
    dp.register_message_handler(admin_panel_main, state=Response.admin_panel_main)
