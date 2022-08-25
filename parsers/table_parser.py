import asyncio
import contextlib
# import lxml
import glob
import random

import html_to_json
import requests
from bs2json import bs2json
from bs4 import BeautifulSoup
from loguru import logger

from auxiliary.req_data import *
from real_estate_bot import variables


# from random import randint


async def db_price_updater(new_price, old_price, table_url):
    try:
        change = int(old_price) - int(new_price)
    except Exception:
        change = int(str(old_price)[1:]) - int(new_price)

    if change == 0:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f""" UPDATE update_ad SET status = 'Active_upd' WHERE url = '{table_url}';""")

        logger.info('Price don`t changed')
    elif change > 0:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↓{str(new_price)}'}' WHERE url = '{table_url}';""")
            glob.cursor.execute(f""" UPDATE update_ad SET status = 'Updated' WHERE url = '{table_url}';""")

        logger.info(f"Price update successfully | {f'↓ {str(new_price)}'}")
    else:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f""" UPDATE update_ad SET price = '{f'↑{str(new_price)}'}' WHERE url = '{table_url}';""")
            glob.cursor.execute(f""" UPDATE update_ad SET status = 'Updated' WHERE url = '{table_url}';""")

        logger.info(f"Price update successfully | {f'↑ {str(new_price)}'}")


async def upn_table_parser(table_url, old_price):
    request = requests.get(table_url, headers=headers).text
    response = BeautifulSoup(request, 'lxml')
    try:
        availability = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][0]['div']['div'][0]['b']['text']
    except Exception:
        availability = 1
    if availability == 'ОБЪЕКТ НЕ НАЙДЕН':
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""UPDATE update_ad SET status = 'DELETED' WHERE url = '{table_url}';""")
        logger.info('Advertisement deleted')
    else:
        new_price = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div']['div']['span'][0]['meta'][3]['attributes']['content']
        await db_price_updater(new_price=new_price, old_price=old_price, table_url=table_url)

    await asyncio.sleep(1)


async def cian_table_parser(table_url, old_price, driver):
    driver.get(url=table_url)
    await asyncio.sleep(float('{:.3f}'.format(random.random())))
    # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")

    full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][1]['main'][0]
    try:
        availability = full_page['div'][0]['div'][2]['_value']
    except Exception:
        availability = 1
    if availability == 'Объявление снято с публикации':
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""UPDATE update_ad SET status = 'DELETED' WHERE url = '{table_url}';""")
        logger.info('Advertisement deleted')
    else:
        new_price = full_page['div'][2]['div'][0]['div'][0]['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        await db_price_updater(new_price=new_price, old_price=old_price, table_url=table_url)

    await asyncio.sleep(float('{:.3f}'.format(random.random())))


async def yandex_table_parser(table_url, old_price, driver):
    driver.get(url=table_url)
    await asyncio.sleep(float('{:.3f}'.format(random.random())))
    # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")

    full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][1]['div'][0]['div'][3]['div'][0]['div'][0]
    try:
        availability = full_page['div'][2]['div'][0]['div'][0]['div'][0]['_value']
    except Exception:
        availability = 1
    if availability == 'объявление снято или устарело':
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""UPDATE update_ad SET status = 'DELETED' WHERE url = '{table_url}';""")
        logger.info('Advertisement deleted')
    else:
        new_price = full_page['div'][1]['h1'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')[:-1]
        await db_price_updater(new_price=new_price, old_price=old_price, table_url=table_url)

    await asyncio.sleep(float('{:.3f}'.format(random.random())))


async def avito_table_parser(table_url, old_price, driver):
    driver.get(url=table_url)
    await asyncio.sleep(float('{:.3f}'.format(random.random())))
    # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")

    with contextlib.suppress(Exception):
        full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][2]['div'][0]['div'][0]
    try:
        availability = full_page['div'][0]['div'][0]['div'][1]['div'][0]['a'][0]['span'][0]['_value']
    except Exception:
        try:
            availability = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][1]['div'][0]['div'][0]['h1'][0]['_value']
        except Exception:
            availability = 1
    if availability in {'Объявление снято с публикации.', 'Ой! Такой страницы на нашем сайте нет :('}:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""UPDATE update_ad SET status = 'DELETED' WHERE url = '{table_url}';""")
        logger.info('Advertisement deleted')
    else:
        new_price = full_page['div'][0]['div'][1]['div'][1]['div'][1]['div'][0]['div'][0]['div'][0]['div'][0]
        new_price = new_price['div'][0]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['span'][0]['_value']
        new_price = str(new_price).replace(' ', '')
        await db_price_updater(new_price=new_price, old_price=old_price, table_url=table_url)

    await asyncio.sleep(float('{:.3f}'.format(random.random())))
