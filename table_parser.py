from bs4 import BeautifulSoup as BS
from selenium import webdriver
from bs2json import bs2json
import pandas as pd
import html_to_json
import psycopg2
import requests
import telebot
# import lxml
import glob
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

token = '5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0'
bot = telebot.TeleBot(token)


def namer(message):
    global table_name
    table_name = message.document.file_name
    print(f"[INFO] - File successfully saved. File name: {table_name}")


def add_driver():
    global driver
    driver = webdriver.Safari()
    print("[INFO] - Driver started")


def reformer():
    global new_table_name
    if table_name[-3:] == 'txt':
        df = pd.read_csv(f"{table_name}")
        new_table_name = f"{str(table_name)[:-4]}_upd.csv"
        df.to_csv(f"{new_table_name}", index=False, header=True)

        print("[INFO] - Copy .txt to .csv  successfully")
    elif table_name[-4:] == 'xlsx':
        df = pd.read_excel(f"{table_name}")
        new_table_name = f"{str(table_name)[:-5]}_upd.csv"
        df.to_csv(f"{new_table_name}", index=False, header=True, sep=";")
        # df = pd.DataFrame(pd.read_csv(f"{new_table_name}"))

        print("[INFO] - Copy .xlsx to .csv  successfully")
    else:
        new_table_name = f"{str(table_name)[:-4]}_upd.csv"
        os.rename(f"{table_name}", f"{new_table_name}")

        print('[INFO] - Already .csv file')


def table_file_remover():
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name}")
        os.remove(f"{new_table_name}")
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{table_name[:-4]}.txt")
        os.remove(f"{table_name[:-4]}.txt")
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{table_name[:-5]}.xlsx")
        os.remove(f"{table_name[:-5]}.xlsx")
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name[:-4]}.txt")
        os.remove(f"{new_table_name[:-4]}.txt")
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name[:-4]}.xlsx")
        os.remove(f"{new_table_name[:-4]}.xlsx")
    except:
        pass


def add_to_table():
    connection_add = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    connection_add.autocommit = True
    cursor_add = connection_add.cursor()

    cursor_add.execute(f"""COPY update_ad FROM '/Users/user/PycharmProjects/Parser/{new_table_name}' DELIMITER ';' CSV HEADER;""")
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную

    if connection_add:
        cursor_add.close()
        connection_add.close()


def update_table_parser(message):
    try:
        glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        glob.connection.autocommit = True
        glob.cursor = glob.connection.cursor()
        print("[INFO] - PostgreSQL connection started")
    except:
        pass

    reformer()

    add_to_table()

    connection_max_row = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    connection_max_row.autocommit = True
    cursor_max_row = connection_max_row.cursor()
    cursor_max_row.execute("""SELECT count(*) FROM update_ad;""")
    max_row = cursor_max_row.fetchall()[0][0]
    if connection_max_row:
        cursor_max_row.close()
        connection_max_row.close()

    for i in range(max_row):
        global old_price
        global url
        glob.cursor.execute("""SELECT url FROM update_ad;""")
        url = glob.cursor.fetchall()[i][0]
        glob.cursor.execute("""SELECT price FROM update_ad;""")
        old_price = glob.cursor.fetchall()[i][0]
        if url[:14] == 'https://upn.ru':
            try:
                upn_table_parser()
            except Exception as ex:
                print('[ERROR UPN] - ', ex)
        elif url[:19] == 'https://ekb.cian.ru':
            try:
                add_driver()
            except:
                pass
            try:
                cian_table_parser()
            except Exception as ex:
                print('[ERROR CIAN] - ', ex)
        elif url[:24] == 'https://realty.yandex.ru':
            try:
                add_driver()
            except:
                pass
            try:
                yandex_table_parser()
            except Exception as ex:
                print('[ERROR YANDEX] - ', ex)
        elif url[:20] == 'https://www.avito.ru':
            try:
                add_driver()
            except:
                pass
            try:
                avito_table_parser()
            except Exception as ex:
                print('[ERROR AVITO] - ', ex)

    try:
        close_driver()
    except:
        pass

    markup_res = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_res = telebot.types.KeyboardButton(".csv")
    btn2_res = telebot.types.KeyboardButton(".xlsx")
    btn3_res = telebot.types.KeyboardButton(".txt")
    btn4_res = telebot.types.KeyboardButton("Все форматы")
    markup_res.add(btn1_res, btn2_res, btn3_res, btn4_res)
    bot.send_message(message.chat.id, text="Вся информация обновлена. В каком формате вы хотите получить результат?", reply_markup=markup_res, parse_mode="Markdown")
    # bot.send_document(message.chat.id, open(f"{new_table_name}", "rb"))
    # table_file_remover()
    print("[INFO] - Table successfully updated")


def upn_table_parser():
    request = requests.get(url, headers=headers).text
    response = BS(request, 'lxml')
    try:
        availability = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][0]['div']['div'][0]['b']['text']
    except:
        availability = 1
    if availability == 'НЕ НАЙДЕНО':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div']['div']['span'][0]['meta'][3]['attributes']['content']
        try:
            change = int(old_price) - int(new_price)
        except:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
            pass
        else:
            if change > 0:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↓' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↓ ' + str(new_price)}")
            else:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↑' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↑ ' + str(new_price)}")
    time.sleep(0.5)


def cian_table_parser():
    driver.get(url=url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['main'][0]
    try:
        availability = full_page['div'][0]['div'][2]['_value']
    except:
        availability = 1
    if availability == 'Объявление снято с публикации':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][2]['div'][0]['div'][0]['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        try:
            change = int(old_price) - int(new_price)
        except:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
            pass
        else:
            if change > 0:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↓' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↓ ' + str(new_price)}")
            else:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↑' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↑ ' + str(new_price)}")
    time.sleep(0.5)


def yandex_table_parser():
    driver.get(url=url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][1]['div'][0]['div'][3]['div'][0]['div'][0]
    try:
        availability = full_page['div'][2]['div'][0]['div'][0]['div'][0]['_value']
    except:
        availability = 1
    if availability == 'объявление снято или устарело':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][1]['h1'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        try:
            change = int(old_price) - int(new_price)
        except:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
            pass
        else:
            if change > 0:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↓' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↓ ' + str(new_price)}")
            else:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↑' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↑ ' + str(new_price)}")
    time.sleep(0.5)


def avito_table_parser():
    driver.get(url=url)
    try:
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][2]['div'][0]['div'][0]
    except:
        pass
    try:
        availability = full_page['div'][0]['div'][0]['div'][1]['div'][0]['a'][0]['span'][0]['_value']
    except:
        try:
            availability = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][0]['h1'][0]['_value']
        except:
            availability = 1
    if availability == 'Объявление снято с публикации.' or availability == 'Ой! Такой страницы на нашем сайте нет :(':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][0]['div'][1]['div'][1]['div'][1]['div'][0]['div'][0]['div'][0]['div'][0]
        new_price = new_price['div'][0]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')
        try:
            change = int(old_price) - int(new_price)
        except:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
            pass
        else:
            if change > 0:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↓' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↓ ' + str(new_price)}")
            else:
                glob.cursor.execute(
                    f""" UPDATE update_ad SET price = '{'↑' + str(new_price)}' WHERE url = '{url}';""")
                print(f"[INFO] - Price update successfully | {'↑ ' + str(new_price)}")
    time.sleep(0.5)


def close_driver():
    driver.quit()
    print("[INFO] - Driver closed")
