import contextlib
import glob
import shutil
from datetime import datetime

import aiofiles
import openpyxl as op
import psycopg2
import pyexcel
from aiofiles import os
from selenium import webdriver

import site_parser as sp
import table_parser as tp
from req_data import *

global table_name, table_name_upd, filename_creator, driver

today = datetime.now()
minute = f'0{str(today.minute)}' if int(today.minute) < 10 else today.minute
filename_creator = f"{today.day}.{today.month}.{today.year} - {today.hour}.{minute}"


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


async def table_name_handler(message, from_where):
    try:
        if from_where == 'mb':
            global table_name, table_name_upd

            table_name = message.document.file_name
            if table_name[-3:] == 'txt' or table_name[-4:] != 'xlsx':
                table_name_upd = f"{str(table_name)[:-4]}_upd"
            else:
                table_name_upd = f"{str(table_name)[:-5]}_upd"

            return table_name, table_name_upd

        else:
            table_name = message.document.file_name

            return table_name

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


async def data_base(adres, price, square, url):
    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(
                f"""INSERT INTO advertisement (adres, price, square, url) VALUES ('{adres}', '{price}', '{square}', '{url}');"""
            )

    except Exception as ex:
        print("[ERROR] [DATA_BASE] - ", ex)
        quit()


async def create_advertisement_table():
    # Create new advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """CREATE TABLE advertisement(
                id SERIAL PRIMARY KEY,
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


async def file_renamer():
    try:
        with contextlib.suppress(Exception):
            await os.rename('pars_site.txt', f'{filename_creator}.txt')

        with contextlib.suppress(Exception):
            await os.rename('pars_site.csv', f'{filename_creator}.csv')

        with contextlib.suppress(Exception):
            await os.rename('pars_site.xlsx', f'{filename_creator}.xlsx')

        print("[INFO] - Renaming of all files was successful")

    except Exception as ex:
        print('[ERROR] [FILE_RENAMER] - ', ex)


async def file_remover(from_where):
    try:
        if from_where == 'site':
            with contextlib.suppress(Exception):
                await os.remove(f"{filename_creator}.csv")
            with contextlib.suppress(Exception):
                await os.remove(f"{filename_creator}.xlsx")
            with contextlib.suppress(Exception):
                await os.remove(f"{filename_creator}.txt")

        else:
            with contextlib.suppress(Exception):
                await os.remove(f"{tp.table_name_upd_tp}")
            with contextlib.suppress(Exception):
                await os.remove(f"{tp.table_name_tp[:-4]}.txt")
            with contextlib.suppress(Exception):
                await os.remove(f"{tp.table_name_tp[:-5]}.xlsx")
            with contextlib.suppress(Exception):
                await os.remove(f"{tp.table_name_upd_tp[:-4]}.txt")
            with contextlib.suppress(Exception):
                await os.remove(f"{tp.table_name_upd_tp[:-4]}.xlsx")

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
    with contextlib.suppress(Exception):
        await start_connection()

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
        table_name_upd_tp = await tp.repeater()

        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(
                f"""COPY update_ad TO '/Users/user/PycharmProjects/Parser/{table_name_upd_tp}' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
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
