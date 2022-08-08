import asyncio
import contextlib
import glob
import shutil
from datetime import datetime

import aiofiles
import openpyxl as op
import pandas as pd
import psycopg2
import pyexcel
from aiofiles import os
from aiogram import Bot, Dispatcher
from bob_telegram_tools.bot import TelegramBot
from bob_telegram_tools.utils import TelegramTqdm
from selenium import webdriver

import site_parser as sp
import table_parser as tp
from all_markups import *
from req_data import *

global table_name, table_name_upd, filename, driver, old_price, table_url, loaded_filename

bot = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot)


async def filename_creator(freshness):
    global loaded_filename, filename

    if freshness == 'new':
        today = datetime.now()

        minute = f'0{str(today.minute)}' if int(today.minute) < 10 else today.minute
        filename = f"{today.day}.{today.month}.{today.year} - {today.hour}.{minute}"
        loaded_filename = filename

        return filename

    else:
        return loaded_filename


async def add_driver():
    try:
        global driver

        driver = webdriver.Safari()

        print("[INFO] - Driver started")

        return driver

    except Exception as ex:
        print('[ERROR] [ADD_DRIVER] - ', ex)


async def start_connection():
    try:
        glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

        glob.connection.autocommit = True
        glob.cursor = glob.connection.cursor()

        print("[INFO] - PostgreSQL connection started")

    except Exception as ex:
        print('[ERROR] [START_CONNECTION] - ', ex)


async def table_name_handler(message):
    try:
        global table_name, table_name_upd

        table_name = message.document.file_name
        if table_name[-3:] == 'txt' or table_name[-4:] != 'xlsx':
            table_name_upd = f"{str(table_name)[:-4]}_upd"
        else:
            table_name_upd = f"{str(table_name)[:-5]}_upd"

        return table_name, table_name_upd

    except Exception as ex:
        print('[ERROR] [TABLE_NAME_HANDLER] - ', ex)


async def convert_csv_to_xlsx(from_where):
    try:
        if from_where == 'site':
            file_name_to_convert = 'pars_site'
        else:
            file_name_to_convert = table_name_upd

        sheet = pyexcel.get_sheet(file_name=f"{file_name_to_convert}.csv", delimiter=";")
        sheet.save_as(f"{file_name_to_convert}.xlsx")

        table = op.load_workbook(f"{file_name_to_convert}.xlsx")
        main_sheet = table[f"{file_name_to_convert}.csv"]
        main_sheet.column_dimensions['B'].width = 30
        main_sheet.column_dimensions['C'].width = 10
        main_sheet.column_dimensions['E'].width = 40
        table.save(f"{file_name_to_convert}.xlsx")

        print("[INFO] - Copy .csv to .xlsx successfully")

    except Exception as ex:
        print('[ERROR] [CONVERT_CSV_TO_XLSX] - ', ex)


async def convert_csv_to_txt(from_where):
    try:
        if from_where == 'site':
            file_name_to_convert = 'pars_site'
        else:
            file_name_to_convert = table_name_upd

        shutil.copyfile(f"{file_name_to_convert}.csv", 'garages_table_4txt.csv')
        await os.rename('garages_table_4txt.csv', f"{file_name_to_convert}.txt")

        async with aiofiles.open(f"{file_name_to_convert}.txt", 'r') as file:
            df = await file.read()
            df = df.replace(';', ' | ')
            df = df.replace('"', '')

        async with aiofiles.open(f"{file_name_to_convert}.txt", 'w') as file:
            await file.write(df)

        print("[INFO] - Copy .csv to .txt successfully")

    except Exception as ex:
        print('[ERROR] [CONVERT_CSV_TO_XLSX] - ', ex)


async def convert_txt_to_csv():
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


async def data_base(status, adres, price, square, url):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""INSERT INTO advertisement (status, adres, price, square, url) VALUES ('{status}', '{adres}', '{price}', '{square}', '{url}');"""
        )


async def add_data_to_data_base():
    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""COPY update_ad FROM '/Users/user/PycharmProjects/Parser/{table_name_upd}.csv' DELIMITER ';' CSV HEADER;""")

    except Exception as ex:
        print('[ERROR] [ADD_DATA_TO_TABLE] - ', ex)


async def create_advertisement_table():
    # Create new advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """CREATE TABLE advertisement(
                id SERIAL PRIMARY KEY,
                status VARCHAR(255),
                adres VARCHAR(255),
                price VARCHAR(30),
                square VARCHAR(10),
                url VARCHAR(255));"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table created")


async def create_update_ad_table():
    # Create new update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """CREATE TABLE update_ad(
                id SERIAL PRIMARY KEY,
                status VARCHAR(255),
                adres VARCHAR(255),
                price VARCHAR(30),
                square VARCHAR(10),
                url VARCHAR(255));"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table created")


async def site_parsing_start():
    try:
        try:
            await create_advertisement_table()
        except Exception:
            await delete_advertisement_table()
            await create_advertisement_table()

    except Exception as ex:
        print('[ERROR] [SITE_PARSING_START] - ', ex)


async def table_parsing_start():
    try:
        try:
            await create_update_ad_table()
        except Exception:
            await delete_update_ad_table()
            await create_update_ad_table()

    except Exception as ex:
        print('[ERROR] [TABLE_PARSING_START] - ', ex)


async def site_parsing_main(req_site, url_upn, url_cian, url_yandex, url_avito, message):
    if req_site == 1:
        await sp.upn_site_parser(message, url_upn)
    elif req_site == 2:
        await sp.cian_site_parser(message, url_cian)
    elif req_site == 3:
        await sp.yandex_site_parser(message, url_yandex)
    elif req_site == 4:
        await sp.avito_site_parser(message, url_avito)


async def table_parsing_main(message):
    try:
        global driver, table_name, table_name_upd

        bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
        tqdm = TelegramTqdm(bot_tqdm)

        await file_format_reformer()

        await add_data_to_data_base()

        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM update_ad;""")
            max_row = glob.cursor.fetchall()[0][0]

        requirement, driver, counter = False, None, 1

        for row in tqdm(range(max_row)):
            # maybe this stopper work not correctly
            if counter is None:
                break
            else:
                for id_handler in range(max_row):
                    try:
                        global old_price, table_url

                        with glob.connection.cursor() as glob.cursor:
                            glob.cursor.execute("""SELECT id FROM update_ad;""")
                            ad_id = glob.cursor.fetchall()[row][0]
                        with glob.connection.cursor() as glob.cursor:
                            glob.cursor.execute("""SELECT url FROM update_ad;""")
                            table_url = glob.cursor.fetchall()[row][0]
                        with glob.connection.cursor() as glob.cursor:
                            glob.cursor.execute("""SELECT price FROM update_ad;""")
                            old_price = glob.cursor.fetchall()[row][0]

                        if ad_id != counter:
                            continue
                        else:
                            if table_url[:14] == 'https://upn.ru':
                                try:
                                    await tp.upn_table_parser(table_url=table_url, old_price=old_price)

                                except Exception as ex:
                                    print('[ERROR] [UPN_TABLE_PARSER] - ', ex)

                            elif table_url[:19] == 'https://ekb.cian.ru':
                                if driver is None:
                                    driver = await add_driver()

                                requirement = True

                                try:
                                    await tp.cian_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [CIAN_TABLE_PARSER] - ', ex)

                            elif table_url[:24] == 'https://realty.yandex.ru':
                                if driver is None:
                                    driver = await add_driver()

                                requirement = True

                                try:
                                    await tp.yandex_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [YANDEX_TABLE_PARSER] - ', ex)

                            elif table_url[:20] == 'https://www.avito.ru':
                                if driver is None:
                                    driver = await add_driver()

                                requirement = True

                                try:
                                    await tp.avito_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [AVITO_TABLE_PARSER] - ', ex)

                            counter += 1

                    except Exception as ex:
                        await asyncio.sleep(5)
                        print('[ERROR] [TABLE_CYCLE] - ', ex)
                        counter = None
                        break

        if requirement:
            await close_driver()

        if counter is not None:
            await table_parsing_finish()

            await bot.send_message(chat_id=message.chat.id, text="Вся информация обновлена. В каком формате вы хотите получить результат?", reply_markup=markup_result, parse_mode="Markdown")

            print("[INFO] - Table successfully updated")

    except Exception as ex:
        print('[ERROR] [TABLE_PARSER_MAIN] - ', ex)


async def file_format_reformer():
    try:
        if table_name[-3:] == 'txt':
            await convert_txt_to_csv()
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


async def file_renamer():
    try:
        with contextlib.suppress(Exception):
            await os.rename('pars_site.txt', f"{await filename_creator(freshness='new')}.txt")

        with contextlib.suppress(Exception):
            await os.rename('pars_site.csv', f"{await filename_creator(freshness='new')}.csv")

        with contextlib.suppress(Exception):
            await os.rename('pars_site.xlsx', f"{await filename_creator(freshness='new')}.xlsx")

        print("[INFO] - Renaming of all files was successful")

    except Exception as ex:
        print('[ERROR] [FILE_RENAMER] - ', ex)


async def file_remover(from_where):
    try:
        if from_where == 'site':
            with contextlib.suppress(Exception):
                await os.remove(f"{await filename_creator(freshness='load')}.csv")
            with contextlib.suppress(Exception):
                await os.remove(f"{await filename_creator(freshness='load')}.xlsx")
            with contextlib.suppress(Exception):
                await os.remove(f"{await filename_creator(freshness='load')}.txt")

        else:
            with contextlib.suppress(Exception):
                await os.remove(f"{table_name_upd}.csv")
            with contextlib.suppress(Exception):
                await os.remove(f"{table_name}")
            with contextlib.suppress(Exception):
                await os.remove(f"{table_name}")
            with contextlib.suppress(Exception):
                await os.remove(f"{table_name_upd}.txt")
            with contextlib.suppress(Exception):
                await os.remove(f"{table_name_upd}.xlsx")

        print("[INFO] - Removing of all files was successful")

    except Exception as ex:
        print('[ERROR] [FILE_REMOVER] - ', ex)


async def delete_advertisement_table():
    # Delete advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE advertisement;"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table deleted")


async def delete_update_ad_table():
    # Delete update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE update_ad;"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table deleted")


async def site_parsing_finish(req_res):
    try:
        if req_res == 'error':
            pass
        else:
            with glob.connection.cursor() as glob.cursor:
                glob.cursor.execute(
                    """COPY advertisement TO '/Users/user/PycharmProjects/Parser/pars_site.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
                )
            # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную

            await delete_advertisement_table()

            if req_res == 'csv':
                await file_renamer()
            elif req_res == 'xlsx':
                await convert_csv_to_xlsx(from_where='site')
                await file_renamer()
            elif req_res == 'txt':
                await convert_csv_to_txt(from_where='site')
                await file_renamer()
            elif req_res == 'all':
                await convert_csv_to_xlsx(from_where='site')
                await convert_csv_to_txt(from_where='site')
                await file_renamer()

    except Exception as ex:
        print('[ERROR] [SITE_PARSING_FINISH] - ', ex)


async def table_parsing_finish():
    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(
                f"""COPY update_ad TO '/Users/user/PycharmProjects/Parser/{table_name_upd}.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
            )

    except Exception as ex:
        print('[ERROR] [TABLE_PARSING_FINISH] - ', ex)


async def close_connection():
    try:
        if glob.connection:
            glob.cursor.close()
            glob.connection.close()
            print("[INFO] - PostgreSQL connection closed")

    except Exception as ex:
        print('[ERROR] [CLOSE_CONNECTION] - ', ex)


async def close_driver():
    try:
        driver.quit()
        print("[INFO] - Driver closed")

    except Exception as ex:
        print('[ERROR] [CLOSE_DRIVER] - ', ex)
