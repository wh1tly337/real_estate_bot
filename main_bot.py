from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from main_code import *
from table_parser import *
from all_markups import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

bot = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot, storage=MemoryStorage())

global new_table_name
global table_name
global id_url
global task


class Answer(StatesGroup):
    url_answer = State()


async def data_base(adres, price, square, url):
    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(
                f"""INSERT INTO advertisement (adres, price, square, url) VALUES ('{adres}', '{price}', '{square}', '{url}');"""
            )
        # print("[INFO] Data was successfully inserted")
    except Exception as ex:
        print("[ERROR DB] - ", ex)
        quit()


async def convert_table_csv_to_xlsx():
    sheet = pyexcel.get_sheet(file_name=f"{new_table_name}.csv", delimiter=";")
    sheet.save_as(f"{new_table_name}.xlsx")

    table = op.load_workbook(f"{new_table_name}.xlsx")
    main_sheet = table[f"{new_table_name}.csv"]
    main_sheet.column_dimensions['B'].width = 30
    main_sheet.column_dimensions['C'].width = 10
    main_sheet.column_dimensions['E'].width = 40
    table.save(f"{new_table_name}.xlsx")

    print("[INFO] - Copy .csv to .xlsx successfully")


async def convert_table_csv_to_txt():
    shutil.copy(f"{new_table_name}.csv", 'garages_table_4txt.csv')
    await os.rename('garages_table_4txt.csv', f"{new_table_name}.txt")

    async with aiofiles.open(f"{new_table_name}.txt", 'r') as file:
        df = await file.read()
        df = df.replace(';', ' | ')
        df = df.replace('"', '')

    async with aiofiles.open(f"{new_table_name}.txt", 'w') as file:
        await file.write(df)

    print("[INFO] - Copy .csv to .txt successfully")


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
async def new_table(message: types.Message, counter=0):
    global task
    task = 'site'
    await start_connection()
    if counter == 0:
        await main_site_start()

    await bot.send_message(chat_id=message.chat.id, text="С какого сайта Вы хотите получить информацию?", reply_markup=markup_site_question, parse_mode="Markdown")


@dp.message_handler(commands=['update_table'])
async def update_table(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Отправьте мне файл, информацию в котором Вы хотите обновить", reply_markup=markup_quit, parse_mode="Markdown")


@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    try:
        global new_table_name
        global table_name
        global task
        task = 'table'

        with contextlib.suppress(Exception):
            await start_connection()
        with contextlib.suppress(Exception):
            await main_table_start()

        src = f"/Users/user/PycharmProjects/Parser/{message.document.file_name}"
        await message.document.download(destination_file=src)

        await namer(message)

        await bot.send_message(chat_id=message.chat.id, text="Отлично! Я начал обновлять информацию, это может занять некоторое время", reply_markup=markup_quit, parse_mode="Markdown")
        await bot.send_message(chat_id=message.chat.id, text="Чем больше объявлений в файле, тем дольше я буду работать")

        table_name = message.document.file_name
        if table_name[-3:] == 'txt' or table_name[-4:] != 'xlsx':
            new_table_name = f"{str(table_name)[:-4]}_upd"
        else:
            new_table_name = f"{str(table_name)[:-5]}_upd"

        await close_connection()

        await update_table_parser(message)

    except Exception as ex:
        print('[ERROR FILE] - ', ex)


@dp.message_handler(state=Answer.url_answer)
async def get_site_url(message: types.Message, state: FSMContext):
    user_response = message.text
    await state.update_data(user_response=user_response)

    point = 0
    if user_response[:14] == 'https://upn.ru' and id_url == 'upn':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с УПНа, это может занять некоторое время')
        await bot.send_message(chat_id=message.chat.id, text='Чем больше объявлений вы выбрали, тем дольше я буду работать')
        await main_site_main(req_site=1, url_upn=user_response, url_cian=None, url_yandex=None, url_avito=None, message=message)
    elif user_response[:19] == 'https://ekb.cian.ru' and id_url == 'cian':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с ЦИАНа, это может занять некоторое время')
        await bot.send_message(chat_id=message.chat.id, text='Чем больше объявлений вы выбрали, тем дольше я буду работать')
        await main_site_main(req_site=2, url_upn=None, url_cian=user_response, url_yandex=None, url_avito=None, message=message)

    elif user_response[:24] == 'https://realty.yandex.ru' and id_url == 'yandex':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Яндекс Недвижимости, это может занять некоторое время')
        await bot.send_message(chat_id=message.chat.id, text='Чем больше объявлений вы выбрали, тем дольше я буду работать')
        await main_site_main(req_site=3, url_upn=None, url_cian=None, url_yandex=user_response, url_avito=None, message=message)

    elif user_response[:20] == 'https://www.avito.ru' and id_url == 'avito':
        await bot.send_message(chat_id=message.chat.id, text='Я начал собирать информацию с Авито, это может занять некоторое время')
        await bot.send_message(chat_id=message.chat.id, text='Чем больше объявлений вы выбрали, тем дольше я буду работать')
        await main_site_main(req_site=4, url_upn=None, url_cian=None, url_yandex=None, url_avito=user_response, message=message)

    elif user_response == 'Завершить работу':
        point = 1
        await bot.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)
    else:
        point = 1
        await getting_site_link(message, id_link='error')
    if point == 0:
        await bot.send_message(chat_id=message.chat.id, text="С этим сайтом я закончил, хотите добавить еще сайт для поиска?", reply_markup=markup_continue_question, parse_mode="Markdown")

    await state.finish()


async def getting_site_link(message: types.Message, id_link):
    global id_url

    if id_link == 'upn':
        id_url = 'upn'
        await bot.send_message(chat_id=message.chat.id, text="Перейдите на сайт [УПН](https://upn.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне",
                               parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.url_answer.set()

    elif id_link == 'cian':
        id_url = 'cian'
        await bot.send_message(chat_id=message.chat.id, text="Перейдите на сайт [ЦИАН](https://ekb.cian.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте "
                                                             "ее мне", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.url_answer.set()

    elif id_link == 'yandex':
        id_url = 'yandex'
        await bot.send_message(chat_id=message.chat.id, text="Перейдите на сайт [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg), настройте все необходимые Вам фильтры, скопируйте ссылку "
                                                             "в адресной строке и отправьте ее мне", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.url_answer.set()

    elif id_link == 'avito':
        id_url = 'avito'
        await bot.send_message(chat_id=message.chat.id, text="Перейдите на сайт [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost), настройте все необходимые Вам фильтры, скопируйте ссылку в "
                                                             "адресной строке и отправьте ее мне", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.url_answer.set()

    elif id_link == 'error':
        await bot.send_message(chat_id=message.chat.id, text="Введена неверная ссылка. Пожалуйста проверьте правильность ссылки и отправьте ее мне.", parse_mode="MarkdownV2",
                               disable_web_page_preview=True, reply_markup=markup_quit)

        await Answer.url_answer.set()


async def file_sender(message: types.Message, call):
    await bot.send_message(chat_id=message.chat.id, text="Ваши файлы", reply_markup=markup_start)
    
    if call == 'site':
        result_file = file_name
    else:
        result_file = new_table_name

    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.csv", "rb"))
    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.xlsx", "rb"))
    await bot.send_document(chat_id=message.chat.id, document=open(f"{result_file}.txt", "rb"))


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    global task

    if message.text == "За работу":
        await bot.send_message(chat_id=message.chat.id, text='Что вы хотите сделать?', reply_markup=markup_first_question)
    elif message.text == "Собрать новую информацию":
        task = 'fast_quit'
        await new_table(message, counter=0)
    elif message.text == "Обновить старую информацию":
        task = 'fast_quit'
        await update_table(message)

    elif message.text == "УПН":
        await getting_site_link(message, id_link='upn')
    elif message.text == "ЦИАН":
        await getting_site_link(message, id_link='cian')
    elif message.text == "Яндекс Недвижимость":
        await getting_site_link(message, id_link='yandex')
    elif message.text == "Авито":
        await getting_site_link(message, id_link='avito')
    elif message.text == "Завершить работу":
        if task == 'fast_quit':
            await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
        else:
            await bot.send_message(chat_id=message.chat.id, text='Вы уверены?', reply_markup=markup_sure)

    elif message.text == "Да, уверен":
        if task == 'site':
            connection_quit = psycopg2.connect(host=host, user=user, password=password, database=db_name)
            connection_quit.autocommit = True
            cursor_quit = connection_quit.cursor()
            cursor_quit.execute("""SELECT count(*) FROM advertisement;""")
            check = cursor_quit.fetchall()[0][0]
            if int(check) != 0:
                await bot.send_message(chat_id=message.chat.id, text='Хотите получить объявления которые я успел найти?',
                                       reply_markup=markup_save_file)
            else:
                await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
                await main_site_finish(req_res='error')
                await renamer()
                await remover()
                with contextlib.suppress(Exception):
                    await close_connection()
            if connection_quit:
                cursor_quit.close()
                connection_quit.close()
        elif task == 'table':
            await bot.send_message(chat_id=message.chat.id, text='Хотите получить таблицу с не до конца обновленными данными?',
                                   reply_markup=markup_save_file)
            with contextlib.suppress(Exception):
                await close_connection()
    elif message.text == "Нет, давай продолжим":
        await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_quit)

    elif message.text == "Да, хочу":
        if task == 'site':
            await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                   reply_markup=markup_result)
        elif task == 'table':
            with contextlib.suppress(Exception):
                await close_driver()
            await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                                   reply_markup=markup_result)
    elif message.text == "Нет, не хочу":
        if task == 'site':
            await main_site_finish(req_res='error')
            await renamer()
            await remover()
            await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            with contextlib.suppress(Exception):
                await close_connection()
        elif task == 'table':
            with contextlib.suppress(Exception):
                await close_driver()
            await bot.send_message(chat_id=message.chat.id, text='Хорошо', reply_markup=markup_start)
            await delete_update_ad_table()
            await close_connection()
            await table_file_remover()

    elif message.text == "Да":
        await new_table(message, counter=1)
    elif message.text == "Нет":
        await bot.send_message(chat_id=message.chat.id, text='Отлично! В каком формате вы хотите получить результат?',
                               reply_markup=markup_result)

    elif message.text == ".csv":
        if task == 'site':
            await main_site_finish(req_res='csv')
            await bot.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{file_name}.csv", "rb"))
            await remover()
            with contextlib.suppress(Exception):
                await close_connection()
        elif task == 'table':
            await bot.send_message(chat_id=message.chat.id, text="Ваш .csv файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{new_table_name}.csv", "rb"))
            await table_file_remover()
            await delete_update_ad_table()
            await close_connection()
    elif message.text == ".xlsx":
        if task == 'site':
            await main_site_finish(req_res='xlsx')
            await bot.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{file_name}.xlsx", "rb"))
            await remover()
            with contextlib.suppress(Exception):
                await close_connection()
        elif task == 'table':
            await convert_table_csv_to_xlsx()
            await bot.send_message(chat_id=message.chat.id, text="Ваш .xlsx файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{new_table_name}.xlsx", "rb"))
            await table_file_remover()
            await delete_update_ad_table()
            await close_connection()
    elif message.text == ".txt":
        if task == 'site':
            await main_site_finish(req_res='txt')
            await bot.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{file_name}.txt", "rb"))
            await remover()
            with contextlib.suppress(Exception):
                await close_connection()
        elif task == 'table':
            await convert_table_csv_to_txt()
            await bot.send_message(chat_id=message.chat.id, text="Ваш .txt файл", reply_markup=markup_start)
            await bot.send_document(chat_id=message.chat.id, document=open(f"{new_table_name}.txt", "rb"))
            await table_file_remover()
            await delete_update_ad_table()
            await close_connection()
    elif message.text == "Все форматы":
        if task == 'site':
            await main_site_finish(req_res='all')
            await file_sender(message, call=task)
            await remover()
            with contextlib.suppress(Exception):
                await close_connection()
        elif task == 'table':
            await convert_table_csv_to_xlsx()
            await convert_table_csv_to_txt()
            await os.rename(f"{new_table_name}.csv", f"{new_table_name}.csv")
            await file_sender(message, call=task)
            await table_file_remover()
            await delete_update_ad_table()
            await close_connection()
    else:
        with contextlib.suppress(Exception):
            await main_site_finish(req_res='error')
        await bot.send_message(chat_id=message.chat.id, text='Таких команд я не знаю 😔\nПопробуй воспользоваться /help', reply_markup=markup_start)


if __name__ == '__main__':
    # while True:
    #     try:
    print('[INFO] - Bot successfully started')
    executor.start_polling(dp)
    # except Exception:
    #     continue
