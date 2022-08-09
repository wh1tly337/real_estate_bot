import glob

import psycopg2
from selenium import webdriver

from auxiliary.req_data import *

global driver


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
