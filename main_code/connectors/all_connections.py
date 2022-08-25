import glob

import psycopg2
from loguru import logger
from selenium import webdriver

from auxiliary.req_data import *
from real_estate_bot import variables


async def add_driver():
    try:
        variables.driver = webdriver.Safari()

        logger.info('Driver started')

        return variables.driver

    except Exception as ex:
        logger.error(ex)


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


async def close_driver():
    try:
        variables.driver.quit()

        logger.info('Driver closed')

    except Exception as ex:
        logger.error(ex)
