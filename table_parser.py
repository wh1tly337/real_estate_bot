import asyncio
import contextlib
# import lxml
import glob

import aiofiles
import html_to_json
import pandas as pd
import psycopg2
import requests
from aiofiles import os
from aiogram import Bot, Dispatcher, types
from bs2json import bs2json
from bs4 import BeautifulSoup as BS
from selenium import webdriver

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

bot = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot)


async def namer(message):
    global table_name
    table_name = message.document.file_name
    print(f"[INFO] - File successfully saved. File name: {table_name}")


async def add_driver():
    global driver
    driver = webdriver.Safari()
    print("[INFO] - Driver started")


async def reformer():
    global new_table_name

    if table_name[-3:] == 'txt':
        await txt_converter()
    elif table_name[-4:] == 'xlsx':
        # noinspection PyArgumentList
        df = pd.read_excel(f"{table_name}")
        new_table_name = f"{str(table_name)[:-5]}_upd.csv"
        df.to_csv(f"{new_table_name}", index=False, header=True, sep=";")
        # df = pd.DataFrame(pd.read_csv(f"{new_table_name}"))

        print("[INFO] - Copy .xlsx to .csv  successfully")
    else:
        new_table_name = f"{str(table_name)[:-4]}_upd.csv"
        await os.rename(f"{table_name}", f"{new_table_name}")

        print('[INFO] - Already .csv file')


async def txt_converter():
    global new_table_name

    async with aiofiles.open(f"{table_name}", 'r') as file:
        df = await file.read()
        df = df.replace(' | ', ';')

    async with aiofiles.open(f"{table_name}", 'w') as file:
        await file.write(df)

    df = pd.read_csv(f"{table_name}")
    new_table_name = f"{str(table_name)[:-4]}_upd.csv"
    df.to_csv(f"{new_table_name}", index=False, header=True)

    print("[INFO] - Copy .txt to .csv  successfully")


async def table_file_remover():
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name}")
        await os.remove(f"{new_table_name}")
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{table_name[:-4]}.txt")
        await os.remove(f"{table_name[:-4]}.txt")
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{table_name[:-5]}.xlsx")
        await os.remove(f"{table_name[:-5]}.xlsx")
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name[:-4]}.txt")
        await os.remove(f"{new_table_name[:-4]}.txt")
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{new_table_name[:-4]}.xlsx")
        await os.remove(f"{new_table_name[:-4]}.xlsx")


async def add_to_table():
    connection_add = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    connection_add.autocommit = True
    cursor_add = connection_add.cursor()

    cursor_add.execute(f"""COPY update_ad FROM '/Users/user/PycharmProjects/Parser/{new_table_name}' DELIMITER ';' CSV HEADER;""")
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную

    if connection_add:
        cursor_add.close()
        connection_add.close()


async def update_table_parser(message):
    with contextlib.suppress(Exception):
        glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        glob.connection.autocommit = True
        glob.cursor = glob.connection.cursor()
        print("[INFO] - PostgreSQL connection started")

    await reformer()

    await add_to_table()

    connection_max_row = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    connection_max_row.autocommit = True
    cursor_max_row = connection_max_row.cursor()
    cursor_max_row.execute("""SELECT count(*) FROM update_ad;""")
    max_row = cursor_max_row.fetchall()[0][0]
    if connection_max_row:
        cursor_max_row.close()
        connection_max_row.close()

    for row in range(max_row):
        try:
            global old_price
            global url
            glob.cursor.execute("""SELECT url FROM update_ad;""")
            url = glob.cursor.fetchall()[row][0]
            glob.cursor.execute("""SELECT price FROM update_ad;""")
            old_price = glob.cursor.fetchall()[row][0]
            if url[:14] == 'https://upn.ru':
                try:
                    await upn_table_parser()
                except Exception as ex:
                    print('[ERROR UPN] - ', ex)
            elif url[:19] == 'https://ekb.cian.ru':
                with contextlib.suppress(Exception):
                    await add_driver()
                try:
                    await cian_table_parser()
                except Exception as ex:
                    print('[ERROR CIAN] - ', ex)
            elif url[:24] == 'https://realty.yandex.ru':
                with contextlib.suppress(Exception):
                    await add_driver()
                try:
                    await yandex_table_parser()
                except Exception as ex:
                    print('[ERROR YANDEX] - ', ex)
            elif url[:20] == 'https://www.avito.ru':
                with contextlib.suppress(Exception):
                    await add_driver()
                try:
                    await avito_table_parser()
                except Exception as ex:
                    print('[ERROR AVITO] - ', ex)
        except Exception as ex:
            print('[ERROR TABLE] - ', ex)
            quit()

    with contextlib.suppress(Exception):
        await close_driver()
    markup_res = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_res = types.KeyboardButton(".csv")
    btn2_res = types.KeyboardButton(".xlsx")
    btn3_res = types.KeyboardButton(".txt")
    btn4_res = types.KeyboardButton("Все форматы")
    markup_res.add(btn1_res, btn2_res, btn3_res, btn4_res)
    await bot.send_message(chat_id=message.chat.id, text="Вся информация обновлена. В каком формате вы хотите получить результат?", reply_markup=markup_res, parse_mode="Markdown")
    # bot.send_document(message.chat.id, open(f"{new_table_name}", "rb"))
    # table_file_remover()
    print("[INFO] - Table successfully updated")


async def upn_table_parser():
    request = requests.get(url, headers=headers).text
    response = BS(request, 'lxml')
    try:
        availability = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][0]['div']['div'][0]['b']['text']
    except Exception:
        availability = 1
    if availability == 'НЕ НАЙДЕНО':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div']['div']['span'][0]['meta'][3]['attributes']['content']
        try:
            change = int(old_price) - int(new_price)
        except Exception:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
        elif change > 0:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↓ {str(new_price)}'}")
        else:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↑ {str(new_price)}'}")
    await asyncio.sleep(0.3)


async def cian_table_parser():
    driver.get(url=url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['main'][0]
    try:
        availability = full_page['div'][0]['div'][2]['_value']
    except Exception:
        availability = 1
    if availability == 'Объявление снято с публикации':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][2]['div'][0]['div'][0]['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        try:
            change = int(old_price) - int(new_price)
        except Exception:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
        elif change > 0:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↓ {str(new_price)}'}")
        else:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↑ {str(new_price)}'}")
    await asyncio.sleep(0.3)


async def yandex_table_parser():
    driver.get(url=url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][1]['div'][0]['div'][3]['div'][0]['div'][0]
    try:
        availability = full_page['div'][2]['div'][0]['div'][0]['div'][0]['_value']
    except Exception:
        availability = 1
    if availability == 'объявление снято или устарело':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][1]['h1'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        try:
            change = int(old_price) - int(new_price)
        except Exception:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
        elif change > 0:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↓ {str(new_price)}'}")
        else:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{str(new_price)}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↑ {str(new_price)}'}")
    await asyncio.sleep(0.3)


async def avito_table_parser():
    driver.get(url=url)
    with contextlib.suppress(Exception):
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][2]['div'][0]['div'][0]
    try:
        availability = full_page['div'][0]['div'][0]['div'][1]['div'][0]['a'][0]['span'][0]['_value']
    except Exception:
        try:
            availability = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][0]['h1'][0]['_value']
        except Exception:
            availability = 1
    if availability in {'Объявление снято с публикации.', 'Ой! Такой страницы на нашем сайте нет :('}:
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{url}';""")
    else:
        new_price = full_page['div'][0]['div'][1]['div'][1]['div'][1]['div'][0]['div'][0]['div'][0]['div'][0]
        new_price = new_price['div'][0]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')
        try:
            change = int(old_price) - int(new_price)
        except Exception:
            change = int(str(old_price)[1:]) - int(new_price)
        if change == 0:
            print('[INFO] - Price don`t changed')
        elif change > 0:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{new_price}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↓ {new_price}'}")
        else:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{new_price}'}' WHERE url = '{url}';""")

            print(f"[INFO] - Price update successfully | {f'↑ {new_price}'}")
    await asyncio.sleep(0.3)


async def close_driver():
    driver.quit()
    print("[INFO] - Driver closed")
