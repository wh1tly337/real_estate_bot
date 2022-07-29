import contextlib
import glob
import shutil
from datetime import datetime

import aiofiles
import openpyxl as op
import psycopg2
import pyexcel
from aiofiles import os

from site_parser import *

global file_name
today = datetime.now()
minute = f'0{str(today.minute)}' if int(today.minute) < 10 else today.minute
file_name = f"{today.day}.{today.month}.{today.year} - {today.hour}.{minute}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'


async def start_connection():
    glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)

    glob.connection.autocommit = True
    glob.cursor = glob.connection.cursor()

    print("[INFO] - PostgreSQL connection started")


async def create_new_site_table():
    # Create new advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """create table advertisement(
                id SERIAL PRIMARY KEY,
                adres varchar(255),
                price varchar(30),
                square varchar(10),
                url varchar(255));"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table created")


async def create_update_ad_table():
    # Create new update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """create table update_ad(
                id SERIAL PRIMARY KEY,
                adres varchar(255),
                price varchar(30),
                square varchar(10),
                url varchar(255));"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table created")


async def main_site_start():
    try:
        await create_new_site_table()
    except Exception:
        await delete_new_site_table()
        await create_new_site_table()


async def main_table_start():
    try:
        await create_update_ad_table()
    except Exception:
        await delete_update_ad_table()
        await create_update_ad_table()


async def main_site_main(req_site, url_upn, url_cian, url_yandex, url_avito, message):
    if req_site == 1:
        await upn_parser(message, url_upn)
    elif req_site == 2:
        await cian_parser(message, url_cian)
    elif req_site == 3:
        await yandex_parser(message, url_yandex)
    elif req_site == 4:
        await avito_parser(message, url_avito)


async def convert_site_csv_to_xlsx():
    sheet = pyexcel.get_sheet(file_name='pars_site.csv', delimiter=";")
    sheet.save_as("pars_site.xlsx")

    table = op.load_workbook("pars_site.xlsx")
    main_sheet = table['pars_site.csv']
    main_sheet.column_dimensions['B'].width = 30
    main_sheet.column_dimensions['C'].width = 10
    main_sheet.column_dimensions['E'].width = 40
    table.save("pars_site.xlsx")

    print("[INFO] - Copy .csv to .xlsx successfully")


async def convert_site_csv_to_txt():
    shutil.copyfile('pars_site.csv', 'garages_table_4txt.csv')
    await os.rename('garages_table_4txt.csv', 'pars_site.txt')

    async with aiofiles.open('pars_site.txt', 'r') as file:
        df = await file.read()
        df = df.replace(';', ' | ')

    async with aiofiles.open('pars_site.txt', 'w') as file:
        await file.write(df)

    print("[INFO] - Copy .csv to .txt successfully")


async def renamer():
    with contextlib.suppress(Exception):
        await os.rename('pars_site.txt', f'{file_name}.txt')

    with contextlib.suppress(Exception):
        await os.rename('pars_site.csv', f'{file_name}.csv')

    with contextlib.suppress(Exception):
        await os.rename('pars_site.xlsx', f'{file_name}.xlsx')

    print("[INFO] - Renaming of all files was successful")


async def remover():
    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.csv")
        await os.remove(f"{file_name}.csv")

    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.xlsx")
        await os.remove(f"{file_name}.xlsx")

    with contextlib.suppress(Exception):
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.txt")
        await os.remove(f"{file_name}.txt")

    print("[INFO] - Removing of all files was successful")


async def delete_new_site_table():
    # Delete advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """drop table advertisement;"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table deleted")


async def delete_update_ad_table():
    with contextlib.suppress(Exception):
        await start_connection()
    # Delete update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """drop table update_ad;"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table deleted")


async def main_site_finish(req_res):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """COPY advertisement TO '/Users/user/PycharmProjects/Parser/pars_site.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную

    await delete_new_site_table()

    if req_res == 'csv':
        await renamer()
    elif req_res == 'xlsx':
        await convert_site_csv_to_xlsx()
        await renamer()
    elif req_res == 'txt':
        await convert_site_csv_to_txt()
        await renamer()
    elif req_res == 'all':
        await convert_site_csv_to_xlsx()
        await convert_site_csv_to_txt()
        await renamer()


async def close_connection():
    if glob.connection:
        glob.cursor.close()
        glob.connection.close()
        print("[INFO] - PostgreSQL connection closed")
