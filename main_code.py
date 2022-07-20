from site_parser import *

from datetime import datetime
import openpyxl as op
import psycopg2
import pyexcel
import shutil
import glob
import os

global file_name
today = datetime.today()
if int(today.minute) < 10:
    minute = '0' + str(today.minute)
else:
    minute = today.minute
file_name = str(("{}.{}.{} - {}.{}".format(today.day, today.month, today.year, today.hour, minute)))

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'


def start_connection():
    glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
    glob.connection.autocommit = True
    glob.cursor = glob.connection.cursor()
    print("[INFO] - PostgreSQL connection started")


def create_new_site_table():
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


def create_update_ad_table():
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


def main_site_start():
    try:
        create_new_site_table()
    except:
        delete_new_site_table()
        create_new_site_table()


def main_table_start():
    try:
        create_update_ad_table()
    except:
        delete_update_ad_table()
        create_update_ad_table()


def main_site_main(req_site, url_upn, url_cian, url_yandex, url_avito, message):
    if req_site == 1:
        upn_parser(message, url_upn)
    elif req_site == 2:
        cian_parser(message, url_cian)
    elif req_site == 3:
        yandex_parser(message, url_yandex)
    elif req_site == 4:
        avito_parser(message, url_avito)


def convert_site_csv_to_xlsx():
    sheet = pyexcel.get_sheet(file_name='pars_site.csv', delimiter=";")
    sheet.save_as("pars_site.xlsx")

    table = op.load_workbook("pars_site.xlsx")
    main_sheet = table['pars_site.csv']
    main_sheet.column_dimensions['B'].width = 30
    main_sheet.column_dimensions['C'].width = 10
    main_sheet.column_dimensions['E'].width = 40
    table.save("pars_site.xlsx")

    print("[INFO] - Copy .csv to .xlsx successfully")


def convert_site_csv_to_txt():
    os.system('cp pars_site.csv garages_table_4txt.csv')
    os.rename('garages_table_4txt.csv', 'pars_site.txt')

    with open('pars_site.txt', 'r') as file:
        df = file.read()
        df = df.replace(';', ' | ')

    with open('pars_site.txt', 'w') as file:
        file.write(df)

    print("[INFO] - Copy .csv to .txt successfully")


def renamer():
    flag = 0
    try:
        os.rename('pars_site.txt', f'{file_name}.txt')
        flag = 1
    except:
        pass
    try:
        os.rename('pars_site.csv', f'{file_name}.csv')
        flag = 1
    except:
        pass
    try:
        os.rename('pars_site.xlsx', f'{file_name}.xlsx')
        flag = 1
    except:
        pass
    if flag == 1:
        print("[INFO] - Renaming of all files was successful")


def remover():
    flag = 0
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.csv")
        os.remove(f"{file_name}.csv")
        flag = 1
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.xlsx")
        os.remove(f"{file_name}.xlsx")
        flag = 1
    except:
        pass
    try:
        # os.remove(f"/Users/user/PycharmProjects/Parser/{file_name}.txt")
        os.remove(f"{file_name}.txt")
        flag = 1
    except:
        pass
    if flag == 1:
        print("[INFO] - Removing of all files was successful")


def delete_new_site_table():
    # Delete advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """drop table advertisement;"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table deleted")


def delete_update_ad_table():
    try:
        start_connection()
    except:
        pass
    # Delete update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """drop table update_ad;"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table deleted")


def main_site_finish(req_res):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """COPY advertisement TO '/Users/user/PycharmProjects/Parser/pars_site.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную

    delete_new_site_table()

    if req_res == 'csv':
        renamer()
    elif req_res == 'xlsx':
        convert_site_csv_to_xlsx()
        renamer()
    elif req_res == 'txt':
        convert_site_csv_to_txt()
        renamer()
    elif req_res == 'all':
        convert_site_csv_to_xlsx()
        convert_site_csv_to_txt()
        renamer()
    elif req_res == 'error':
        pass


def close_connection():
    if glob.connection:
        glob.cursor.close()
        glob.connection.close()
        print("[INFO] - PostgreSQL connection closed")
