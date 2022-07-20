from table_parser import *
from main_code import *

import psycopg2
import telebot
import shutil
import glob

# create table advertisement(
#     id SERIAL PRIMARY KEY,
#     adres varchar(255),
#     price varchar(30),
#     square varchar(10),
#     url varchar(255)
# );

# select * from advertisement;

# drop table advertisement;

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

token = '5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0'

global bot
bot = telebot.TeleBot(token)


def data_base(adres, price, square, url):
    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(
                f"""INSERT INTO advertisement (adres, price, square, url) VALUES ('{adres}', '{price}', '{square}', '{url}');"""
            )
        # print("[INFO] Data was successfully inserted")
    except Exception as ex:
        print("[ERROR DB] - ", ex)
        quit()


def convert_table_csv_to_xlsx():
    sheet = pyexcel.get_sheet(file_name=f"{new_table_name}.csv", delimiter=";")
    sheet.save_as(f"{new_table_name}.xlsx")

    table = op.load_workbook(f"{new_table_name}.xlsx")
    main_sheet = table[f"{new_table_name}.csv"]
    main_sheet.column_dimensions['B'].width = 30
    main_sheet.column_dimensions['C'].width = 10
    main_sheet.column_dimensions['E'].width = 40
    table.save(f"{new_table_name}.xlsx")

    print("[INFO] - Copy .csv to .xlsx successfully")


def convert_table_csv_to_txt():
    shutil.copy(f"{new_table_name}.csv", 'garages_table_4txt.csv')
    os.rename('garages_table_4txt.csv', f"{new_table_name}.txt")

    print("[INFO] - Copy .csv to .txt successfully")


def telegram_bot():
    print("[INFO] - Bot started")

    @bot.message_handler(commands=['start'])
    def start_message(message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton("За работу")
        btn2 = telebot.types.KeyboardButton("/help")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         '{0.first_name}, добро пожаловать в бот помощник по недвижимости!\
            \nЯ в любое время могу собирать информацию о необходимых тебе объектах.\
            \nТакже я могу подыскать информацию по любым указанными тобой параметрам.\
            \nСобирать всю эту информацию в удобном тебе виде и обновлять ее по твоему желанию.\
            \nВо время использования моего функционала, пользуйтесь кнопками снизу клавиатуры, Вам так будет намного удобнее.\
            \n\nДля того чтобы узнать все мои команды нажмите на кнопку /help на клавиатуре.'.format(
                             message.from_user, bot.get_me()), reply_markup=markup, parse_mode='html')

    @bot.message_handler(commands=['help'])
    def help_message(message):
        bot.send_message(message.chat.id, 'Доступные команды:\
                \n/links - узнать сайты с которыми я могу работать и их ссылки\
                \n/new_table - собрать новую информацию по вашим параметрам\
                \n/update_table - обновить информацию уже по имеющейся базе данных\
                \n/feedback - отправка отзыва, пожелания, замечания или бага\
                \n/settings - мои настройки')

    @bot.message_handler(commands=['links'])
    def links(message):
        bot.send_message(message.chat.id, text="На данный момент я работаю с сайтами:\
                \n• [УПН](https://upn.ru)\
                \n• [ЦИАН](https://ekb.cian.ru)\
                \n• [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg)\
                \n• [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost)", disable_web_page_preview=True, parse_mode="MarkdownV2")

    @bot.message_handler(commands=['new_table'])
    def new_table(message, counter=0):
        global task
        task = 'site'
        start_connection()
        if counter == 0:
            main_site_start()
        markup_new = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_new = telebot.types.KeyboardButton("УПН")
        btn2_new = telebot.types.KeyboardButton("ЦИАН")
        btn3_new = telebot.types.KeyboardButton("Яндекс Недвижимость")
        btn4_new = telebot.types.KeyboardButton("Авито")
        btn5_new = telebot.types.KeyboardButton("Завершить работу")
        markup_new.add(btn1_new, btn2_new), markup_new.add(btn3_new, btn4_new), markup_new.add(btn5_new)
        bot.send_message(message.chat.id, text="С какого сайта Вы хотите получить информацию?", reply_markup=markup_new, parse_mode="Markdown")

    @bot.message_handler(commands=['update_table'])
    def update_table(message):
        markup_new = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_new = telebot.types.KeyboardButton("Завершить работу")
        markup_new.add(btn1_new)
        bot.send_message(message.chat.id, text="Отправьте мне файл, информацию в котором Вы хотите обновить", reply_markup=markup_new, parse_mode="Markdown")

    @bot.message_handler(content_types=['document'])
    def handle_docs(message):
        # try:
        global task
        task = 'table'
        try:
            start_connection()
        except:
            pass
        try:
            main_table_start()
        except:
            pass

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        namer(message)

        src = '/Users/user/PycharmProjects/Parser/' + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        markup_new = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_new = telebot.types.KeyboardButton("Завершить работу")
        markup_new.add(btn1_new)
        bot.send_message(message.chat.id, text="Отлично! Я начал обновлять информацию, это может занять некоторое время", reply_markup=markup_new,
                         parse_mode="Markdown")
        bot.send_message(message.chat.id, text="Чем больше объявлений в файле, тем дольше я буду работать")

        global new_table_name
        global table_name
        table_name = message.document.file_name
        if table_name[-3:] == 'txt':
            new_table_name = f"{str(table_name)[:-4]}_upd"
        elif table_name[-4:] == 'xlsx':
            new_table_name = f"{str(table_name)[:-5]}_upd"
        else:
            new_table_name = f"{str(table_name)[:-4]}_upd"
        close_connection()

        update_table_parser(message)

        delete_update_ad_table()

        close_connection()

    # except Exception as ex:
    #     print('[ERROR FILE] - ', ex)

    def get_site_url(message):
        user_response = message.text
        point = 0
        if user_response[:14] == 'https://upn.ru' and ID_url == 'upn':
            bot.send_message(message.chat.id, text="Я начал собирать информацию с УПНа, это может занять некоторое время")
            bot.send_message(message.chat.id, text="Чем больше объявлений вы выбрали, тем дольше я буду работать")
            main_site_main(req_site=1, url_upn=user_response, url_cian=None, url_yandex=None, url_avito=None, message=message)
        elif user_response[:19] == 'https://ekb.cian.ru' and ID_url == 'cian':
            bot.send_message(message.chat.id, text="Я начал собирать информацию с ЦИАНа, это может занять некоторое время")
            bot.send_message(message.chat.id, text="Чем больше объявлений вы выбрали, тем дольше я буду работать")
            main_site_main(req_site=2, url_upn=None, url_cian=user_response, url_yandex=None, url_avito=None, message=message)
        elif user_response[:24] == 'https://realty.yandex.ru' and ID_url == 'yandex':
            bot.send_message(message.chat.id, text="Я начал собирать информацию с Яндекс Недвижимости, это может занять некоторое время")
            bot.send_message(message.chat.id, text="Чем больше объявлений вы выбрали, тем дольше я буду работать")
            main_site_main(req_site=3, url_upn=None, url_cian=None, url_yandex=user_response, url_avito=None, message=message)
        elif user_response[:20] == 'https://www.avito.ru' and ID_url == 'avito':
            bot.send_message(message.chat.id, text="Я начал собирать информацию с Авито, это может занять некоторое время")
            bot.send_message(message.chat.id, text="Чем больше объявлений вы выбрали, тем дольше я буду работать")
            main_site_main(req_site=4, url_upn=None, url_cian=None, url_yandex=None, url_avito=user_response, message=message)
        elif user_response == 'Завершить работу':
            point = 1
            markup_quit = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1_quit = telebot.types.KeyboardButton("Да, уверен")
            btn2_quit = telebot.types.KeyboardButton("Нет, давай продолжим")
            markup_quit.add(btn1_quit, btn2_quit)
            bot.send_message(message.chat.id, text="Вы уверены?", reply_markup=markup_quit)
        else:
            point = 1
            getting_site_link(message, ID_link='error')
        if point == 0:
            markup_q = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1_q = telebot.types.KeyboardButton("Да")
            btn2_q = telebot.types.KeyboardButton("Нет")
            markup_q.add(btn1_q, btn2_q)
            bot.send_message(message.chat.id, text="С этим сайтом я закончил, хотите добавить еще сайт для поиска?", reply_markup=markup_q, parse_mode="Markdown")

    def getting_site_link(message, ID_link):
        markup_quit = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_quit = telebot.types.KeyboardButton("Завершить работу")
        markup_quit.add(btn1_quit)
        global ID_url
        if ID_link == 'upn':
            ID_url = 'upn'
            sent = bot.send_message(message.chat.id,
                                    text="Перейдите на сайт [УПН](https://upn.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне",
                                    parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
            bot.register_next_step_handler(sent, get_site_url)
        elif ID_link == 'cian':
            ID_url = 'cian'
            sent = bot.send_message(message.chat.id,
                                    text="Перейдите на сайт [ЦИАН](https://ekb.cian.ru), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне",
                                    parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
            bot.register_next_step_handler(sent, get_site_url)
        elif ID_link == 'yandex':
            ID_url = 'yandex'
            sent = bot.send_message(message.chat.id,
                                    text="Перейдите на сайт [Яндекс Недвижимость](https://realty.yandex.ru/ekaterinburg), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне",
                                    parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
            bot.register_next_step_handler(sent, get_site_url)
        elif ID_link == 'avito':
            ID_url = 'avito'
            sent = bot.send_message(message.chat.id,
                                    text="Перейдите на сайт [Авито](https://www.avito.ru/ekaterinburg/nedvizhimost), настройте все необходимые Вам фильтры, скопируйте ссылку в адресной строке и отправьте ее мне",
                                    parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup_quit)
            bot.register_next_step_handler(sent, get_site_url)
        elif ID_link == 'error':
            sent = bot.send_message(message.chat.id, text="Введена неверная ссылка. Пожалуйста проверьте правильность ссылки и отправьте ее мне.", parse_mode="Markdown",
                                    disable_web_page_preview=True,
                                    reply_markup=markup_quit)
            bot.register_next_step_handler(sent, get_site_url)

    @bot.message_handler(content_types=['text'])
    def text(message):

        markup_res = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_res = telebot.types.KeyboardButton(".csv")
        btn2_res = telebot.types.KeyboardButton(".xlsx")
        btn3_res = telebot.types.KeyboardButton(".txt")
        btn4_res = telebot.types.KeyboardButton("Все форматы")
        markup_res.add(btn1_res, btn2_res, btn3_res, btn4_res)

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = telebot.types.KeyboardButton("За работу")
        btn2 = telebot.types.KeyboardButton("/help")
        markup.add(btn1, btn2)

        markup_second_quit = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_second_quit = telebot.types.KeyboardButton("Да, уверен")
        btn2_second_quit = telebot.types.KeyboardButton("Нет, давай продолжим")
        markup_second_quit.add(btn1_second_quit, btn2_second_quit)

        markup_quit_q = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_quit_q = telebot.types.KeyboardButton("Да, хочу")
        btn2_quit_q = telebot.types.KeyboardButton("Нет, не хочу")
        markup_quit_q.add(btn1_quit_q, btn2_quit_q)

        markup_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_start = telebot.types.KeyboardButton("Собрать новую информацию")
        btn2_start = telebot.types.KeyboardButton("Обновить старую информацию")
        markup_start.add(btn1_start, btn2_start)

        markup_first_quit = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1_first_quit = telebot.types.KeyboardButton("Завершить работу")
        markup_first_quit.add(btn1_first_quit)

        if message.text == "За работу":
            bot.send_message(message.chat.id, text="Что вы хотите сделать?", reply_markup=markup_start)
        elif message.text == "Собрать новую информацию":
            new_table(message, counter=0)
        elif message.text == "Обновить старую информацию":
            update_table(message)
        elif message.text == "УПН":
            getting_site_link(message, ID_link='upn')
        elif message.text == "ЦИАН":
            getting_site_link(message, ID_link='cian')
        elif message.text == "Яндекс Недвижимость":
            getting_site_link(message, ID_link='yandex')
        elif message.text == "Авито":
            getting_site_link(message, ID_link='avito')
        elif message.text == "Завершить работу":
            bot.send_message(message.chat.id, text="Вы уверены?", reply_markup=markup_second_quit)
        elif message.text == "Да, уверен":
            connection_quit = psycopg2.connect(host=host, user=user, password=password, database=db_name)
            connection_quit.autocommit = True
            cursor_quit = connection_quit.cursor()
            cursor_quit.execute("""SELECT count(*) FROM advertisement;""")
            check = cursor_quit.fetchall()[0][0]
            if int(check) != 0:
                bot.send_message(message.chat.id, text="Хотите получить объявления которые я успел найти?", reply_markup=markup_quit_q)
            else:
                bot.send_message(message.chat.id, text="Хорошо", reply_markup=markup)
                main_site_finish(req_res='error')
                renamer()
                remover()
                try:
                    close_connection()
                except:
                    pass
            if connection_quit:
                cursor_quit.close()
                connection_quit.close()
        elif message.text == "Да, хочу":
            bot.send_message(message.chat.id, text="Отлично! В каком формате вы хотите получить результат?", reply_markup=markup_res)
        elif message.text == "Нет, не хочу":
            main_site_finish(req_res='error')
            renamer()
            remover()
            bot.send_message(message.chat.id, text="Хорошо", reply_markup=markup)
            try:
                close_connection()
            except:
                pass
        elif message.text == "Нет, давай продолжим":
            bot.send_message(message.chat.id, text="Хорошо", reply_markup=markup_first_quit)
        elif message.text == "Да":
            new_table(message, counter=1)
        elif message.text == "Нет":
            bot.send_message(message.chat.id, text="Отлично! В каком формате вы хотите получить результат?", reply_markup=markup_res)
        elif message.text == ".csv":
            if task == 'site':
                main_site_finish(req_res='csv')
                bot.send_message(message.chat.id, text="Ваш .csv файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{file_name}.csv", "rb"))
                remover()
                try:
                    close_connection()
                except:
                    pass
            elif task == 'table':
                bot.send_message(message.chat.id, text="Ваш .csv файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{new_table_name}.csv", "rb"))
                table_file_remover()
        elif message.text == ".xlsx":
            if task == 'site':
                main_site_finish(req_res='xlsx')
                bot.send_message(message.chat.id, text="Ваш .xlsx файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{file_name}.xlsx", "rb"))
                remover()
                try:
                    close_connection()
                except:
                    pass
            elif task == 'table':
                convert_table_csv_to_xlsx()
                bot.send_message(message.chat.id, text="Ваш .xlsx файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{new_table_name}.xlsx", "rb"))
                table_file_remover()
        elif message.text == ".txt":
            if task == 'site':
                main_site_finish(req_res='txt')
                bot.send_message(message.chat.id, text="Ваш .txt файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{file_name}.txt", "rb"))
                remover()
                try:
                    close_connection()
                except:
                    pass
            elif task == 'table':
                convert_table_csv_to_txt()
                bot.send_message(message.chat.id, text="Ваш .txt файл", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{new_table_name}.txt", "rb"))
                table_file_remover()
        elif message.text == "Все форматы":
            if task == 'site':
                main_site_finish(req_res='all')
                bot.send_message(message.chat.id, text="Ваши файлы", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{file_name}.csv", "rb"))
                bot.send_document(message.chat.id, open(f"{file_name}.xlsx", "rb"))
                bot.send_document(message.chat.id, open(f"{file_name}.txt", "rb"))
                remover()
                try:
                    close_connection()
                except:
                    pass
            elif task == 'table':
                convert_table_csv_to_xlsx()
                convert_table_csv_to_txt()
                os.rename(f"{new_table_name}.csv", f"{new_table_name}.csv")
                bot.send_message(message.chat.id, text="Ваши файлы", reply_markup=markup)
                bot.send_document(message.chat.id, open(f"{new_table_name}.csv", "rb"))
                bot.send_document(message.chat.id, open(f"{new_table_name}.xlsx", "rb"))
                bot.send_document(message.chat.id, open(f"{new_table_name}.txt", "rb"))
                table_file_remover()
        else:
            try:
                main_site_finish(req_res='error')
            except:
                pass
            bot.send_message(message.chat.id, text="Таких команд я не знаю 😔\nПопробуй воспользоваться /help", reply_markup=markup)

    bot.polling(none_stop=True)


if __name__ == '__main__':
    telegram_bot()

# 1) Проблема перезапуска бота. После второго прогона парсинга невозможно остановить его принудительно
# Ее нужно фиксить через перезапуск самого кода в heroku
#
# 2) Настроить или поменять работу функции "Завершить работу" для обновления таблицы
#
# 3) Сделать так, чтобы если вдруг появлялась ошибка, то бот не останавливался, а продолжал работать и пользователю приходило сообщение об ошибке
#
# 4) Написать описание бота, то как все работает. Чтобы у пользователя не возникало вопросов о том как все работает
#
# 5) Сделать прогресс бар в боте
