import glob
# import os

import psycopg2
from loguru import logger
from selenium import webdriver

from auxiliary.req_data import *
from real_estate_bot.helpers import variables


async def start_connection():
    try:
        glob.connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        glob.connection.autocommit = True
        glob.cursor = glob.connection.cursor()

        logger.info('PostgreSQL connection started')

    except Exception as ex:
        logger.error(ex)


async def close_connection():
    try:
        if glob.connection:
            glob.cursor.close()
            glob.connection.close()

            logger.info('PostgreSQL connection closed')

    except Exception as ex:
        logger.error(ex)


# noinspection DuplicatedCode
async def add_driver():
    try:
        variables.driver = webdriver.Safari()
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        # variables.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        logger.info('Driver started')

        return variables.driver

    except Exception as ex:
        logger.error(ex)


async def close_driver():
    try:
        variables.driver.quit()

        logger.info('Driver closed')

    except Exception as ex:
        logger.error(ex)
