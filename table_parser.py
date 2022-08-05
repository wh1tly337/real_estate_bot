import asyncio
import contextlib
# import lxml
import glob

import aiofiles
import html_to_json
import pandas as pd
import requests
from aiofiles import os
from aiogram import Bot, Dispatcher
from bs2json import bs2json
from bs4 import BeautifulSoup

import main_code as mc
from all_markups import *
from req_data import *

bot = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot)

global table_name, table_name_upd, old_price, table_url, driver


async def file_format_reformer():
    try:
        if table_name[-3:] == 'txt':
            await converter_txt_to_csv()
        elif table_name[-4:] == 'xlsx':
            # noinspection PyArgumentList
            df = pd.read_excel(f"{table_name}")
            df.to_csv(f"{table_name_upd}.csv", index=False, header=True, sep=";")

            print("[INFO] - Copy .xlsx to .csv  successfully")
        else:
            await os.rename(f"{table_name}", f"{table_name_upd}.csv")

            print('[INFO] - Already .csv file')

    except Exception as ex:
        print('[ERROR] [FILE_FORMAT_REFORMER] - ', ex)


async def converter_txt_to_csv():
    try:
        async with aiofiles.open(f"{table_name}", 'r') as file:
            df = await file.read()
            df = df.replace(' | ', ';')

        async with aiofiles.open(f"{table_name}", 'w') as file:
            await file.write(df)

        df = pd.read_csv(f"{table_name}")
        df.to_csv(f"{table_name_upd}.csv", index=False, header=True)

        print("[INFO] - Copy .txt to .csv  successfully")

    except Exception as ex:
        print('[ERROR] [CONVERTER_TXT_TO_CSV] - ', ex)


async def add_data_to_table():
    try:
        glob.cursor.execute(f"""COPY update_ad FROM '/Users/user/PycharmProjects/Parser/{table_name_upd}.csv' DELIMITER ';' CSV HEADER;""")

    except Exception as ex:
        print('[ERROR] [ADD_DATA_TO_TABLE] - ', ex)


async def update_table_parser(message):
    try:
        global driver, table_name, table_name_upd

        with contextlib.suppress(Exception):
            await mc.start_connection()

        table_name, table_name_upd = await mc.table_name_handler(message)

        await file_format_reformer()

        await add_data_to_table()

        glob.cursor.execute("""SELECT count(*) FROM update_ad;""")
        max_row = glob.cursor.fetchall()[0][0]

        requirement, driver, counter = False, None, 1

        for row in range(max_row):
            # maybe this stopper work not correctly
            if counter is None:
                break
            else:
                for id_handler in range(max_row):
                    try:
                        global old_price, table_url

                        glob.cursor.execute("""SELECT id FROM update_ad;""")
                        ad_id = glob.cursor.fetchall()[row][0]
                        glob.cursor.execute("""SELECT url FROM update_ad;""")
                        table_url = glob.cursor.fetchall()[row][0]
                        glob.cursor.execute("""SELECT price FROM update_ad;""")
                        old_price = glob.cursor.fetchall()[row][0]

                        if ad_id != counter:
                            continue
                        else:
                            if table_url[:14] == 'https://upn.ru':
                                try:
                                    await upn_table_parser()

                                except Exception as ex:
                                    print('[ERROR] [UPN_TABLE_PARSER] - ', ex)

                            elif table_url[:19] == 'https://ekb.cian.ru':
                                if driver is None:
                                    driver = await mc.add_driver()

                                requirement = True

                                try:
                                    await cian_table_parser()

                                except Exception as ex:
                                    print('[ERROR] [CIAN_TABLE_PARSER] - ', ex)

                            elif table_url[:24] == 'https://realty.yandex.ru':
                                if driver is None:
                                    driver = await mc.add_driver()

                                requirement = True

                                try:
                                    await yandex_table_parser()

                                except Exception as ex:
                                    print('[ERROR] [YANDEX_TABLE_PARSER] - ', ex)

                            elif table_url[:20] == 'https://www.avito.ru':
                                if driver is None:
                                    driver = await mc.add_driver()

                                requirement = True

                                try:
                                    await avito_table_parser()

                                except Exception as ex:
                                    print('[ERROR] [AVITO_TABLE_PARSER] - ', ex)

                            counter += 1

                    except Exception as ex:
                        await asyncio.sleep(5)
                        print('[ERROR] [TABLE_CYCLE] - ', ex)
                        counter = None
                        break

        if requirement:
            await mc.close_driver()

        if counter is not None:
            await mc.table_parsing_finish()

            await bot.send_message(chat_id=message.chat.id, text="Вся информация обновлена. В каком формате вы хотите получить результат?", reply_markup=markup_result, parse_mode="Markdown")

            print("[INFO] - Table successfully updated")

    except Exception as ex:
        print('[ERROR] [UPDATE_TABLE_PARSER] - ', ex)


async def db_price_updater(new_price):
    try:
        change = int(old_price) - int(new_price)
    except Exception:
        change = int(str(old_price)[1:]) - int(new_price)

    if change == 0:
        print('[INFO] - Price don`t changed')
    elif change > 0:
        glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{str(new_price)}'}' WHERE url = '{table_url}';""")

        print(f"[INFO] - Price update successfully | {f'↓ {str(new_price)}'}")
    else:
        glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{str(new_price)}'}' WHERE url = '{table_url}';""")

        print(f"[INFO] - Price update successfully | {f'↑ {str(new_price)}'}")


async def upn_table_parser():
    request = requests.get(table_url, headers=headers).text
    response = BeautifulSoup(request, 'lxml')
    try:
        availability = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][0]['div']['div'][0]['b']['text']
    except Exception:
        availability = 1
    if availability == 'ОБЪЕКТ НЕ НАЙДЕН':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{table_url}';""")
        print('[INFO] - Advertisement deleted')
    else:
        new_price = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div']['div']['span'][0]['meta'][3]['attributes']['content']
        await db_price_updater(new_price=new_price)
    await asyncio.sleep(1)


async def cian_table_parser():
    driver.get(url=table_url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['main'][0]
    try:
        availability = full_page['div'][0]['div'][2]['_value']
    except Exception:
        availability = 1
    if availability == 'Объявление снято с публикации':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{table_url}';""")
        print('[INFO] - Advertisement deleted')
    else:
        new_price = full_page['div'][2]['div'][0]['div'][0]['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        await db_price_updater(new_price=new_price)
    await asyncio.sleep(1)


async def yandex_table_parser():
    driver.get(url=table_url)
    full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][1]['div'][0]['div'][3]['div'][0]['div'][0]
    try:
        availability = full_page['div'][2]['div'][0]['div'][0]['div'][0]['_value']
    except Exception:
        availability = 1
    if availability == 'объявление снято или устарело':
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{table_url}';""")
        print('[INFO] - Advertisement deleted')
    else:
        new_price = full_page['div'][1]['h1'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        await db_price_updater(new_price=new_price)
    await asyncio.sleep(1)


async def avito_table_parser():
    driver.get(url=table_url)
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
        glob.cursor.execute(f"""UPDATE update_ad SET square = 'DELETED' WHERE url = '{table_url}';""")
        print('[INFO] - Advertisement deleted')
    else:
        new_price = full_page['div'][0]['div'][1]['div'][1]['div'][1]['div'][0]['div'][0]['div'][0]['div'][0]
        new_price = new_price['div'][0]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')
        await db_price_updater(new_price=new_price)
    await asyncio.sleep(1)
