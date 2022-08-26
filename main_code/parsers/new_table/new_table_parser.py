import asyncio
import itertools
# from random import randint
# import lxml
import math
import random
import re
import time

import html_to_json
import requests
from bob_telegram_tools.bot import TelegramBot
from bob_telegram_tools.utils import TelegramTqdm
from bs2json import bs2json
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver

from auxiliary.req_data import *
from main_code.workers import work_with_data_base as wwdb
from real_estate_bot.helpers import variables


async def cian_avito_url_cycle_detector(url_next_page, i):
    index = url_next_page.find('&p=')
    if index == -1:
        url_cycle = url_next_page
    else:
        index = index + 3
        url_cycle = f"{url_next_page[:index]}{i}{url_next_page[index + 1:]}"
    logger.info(url_cycle)

    return url_cycle


async def upn_site_parser(message, url_upn):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    logger.info(f"{message.chat.id} | Start parsing UPN")
    index = url_upn.find('?page')
    url = url_upn if index == -1 else url_upn[:index]
    request = requests.get(url, headers=headers).text
    response = BeautifulSoup(request, 'lxml')

    page_count = math.ceil(int("".join(re.findall(r"\d+", str(
        bs2json().convert(response.find())['html']['head']['title']['text']).split('|')[1]))) / 25)
    if page_count > 15:
        page_count = 15
        await bot_aiogram.send_message(chat_id=message.chat.id,
                                       text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 '
                                            'страниц.')

    variables.possibility = True

    for j in tqdm(range(1, page_count + 1)):
        try:
            if re.search(r"\d+", url[-1]):
                url_cycle = f"{url}?page={j}"
            else:
                url_cycle = f"{url}?page={j}"

            logger.info(url_cycle)

            request = requests.get(url_cycle, headers=headers).text
            response = BeautifulSoup(request, 'lxml')
            ad = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][2]['div'][1]['div'][1]['div']
            ads_count = len(ad)
            for i in range(ads_count):
                if variables.possibility is False:
                    break
                else:
                    if len(ad[i]) == 1:
                        continue
                    if len(ad[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']) == 3:
                        price = "".join(re.findall(r"\d+", ad[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']['text']))
                    else:
                        price = "".join(re.findall(r"\d+", ad[i]['div'][1]['div'][7]['div'][0]['div'][0]['div'][1]['text']))
                    full_address = "".join((ad[i]['div'][1]['div'][1]['span']['text']).split(',')[-2:])
                    ad_url = 'https://upn.ru' + ad[i]['div'][1]['a']['attributes']['href']
                    square = round(float("".join((ad[i]['div'][1]['div'][2]['div'][0]['div'][1]['text']).split('/')[0])))

                    try:
                        await wwdb.data_base(status='Active', adres=full_address, price=price, square=square, url=ad_url)

                    except Exception as ex:
                        logger.error(ex)
                        variables.possibility = False
                        break

        except Exception as ex:
            logger.error(ex)

    logger.info(f"{message.chat.id} | Finish parsing UPN")


# noinspection DuplicatedCode
async def cian_site_parser(message, url_cian):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    logger.info(f"{message.chat.id} | Start parsing Cian")
    url = url_cian
    variables.driver = webdriver.Safari()

    try:
        time.sleep(1)
        variables.driver.get(url=url)
        full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]
        for i in range(20):
            try:
                page_count = math.ceil(int("".join(re.findall(r"\d+", full_page['div'][0]['div'][0]['div'][i]['div'][0]['div'][0]['h5'][0]['_value']))) / 28)
                break
            except Exception:
                continue
        if page_count > 15:  # noqa
            page_count = 15
            await bot_aiogram.send_message(chat_id=message.chat.id,
                                           text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
                                                '15 страниц.')
        url_next_page = 1
        for i in range(20):
            try:
                url_next_page = full_page['div'][0]['div'][0]['div'][i]['div'][0]['ul'][0]['li'][1]['a'][0]['_attributes']['href']
                break

            except Exception:
                continue
        if url_next_page == 1:
            url_next_page = url

        variables.possibility = True

        for i in tqdm(range(1, page_count + 1)):
            if variables.possibility is False:
                break
            else:
                url_cycle = await cian_avito_url_cycle_detector(url_next_page, i)
                variables.driver.get(url=url_cycle)
                # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]
                for j in range(20):
                    try:
                        sp = j
                        ads_count = len(full_page['div'][0]['div'][0]['div'][j]['article'])
                        break

                    except Exception:
                        continue
                for j in range(ads_count):  # noqa
                    ad = full_page['div'][0]['div'][0]['div'][sp]['article'][j]  # noqa
                    ad_url = ad['div'][0]['div'][1]['div'][0]['div'][0]['a'][0]['_attributes']['href']
                    try:
                        square = round(float(str(ad['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']).split(',')[1].strip()[:3].strip()))

                    except Exception:
                        square = '-'
                    for n, m in itertools.product(range(10), range(10)):
                        try:
                            sp_1 = len(ad['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'])
                            street_address = ad['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 2]['_value']
                            number_address = ad['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 1]['_value']
                            full_address = f"{street_address} {number_address}"

                        except Exception:
                            continue
                    for n in range(10):
                        try:
                            price = "".join(re.findall(r"\d+", ad['div'][0]['div'][1]['div'][0]['div'][0]['div'][n]['div'][0]['span'][0]['span'][0]['_value']))
                            break

                        except Exception:
                            continue

                    try:
                        await wwdb.data_base(status='Active', adres=full_address, price=price, square=square, url=ad_url)  # noqa

                    except Exception as ex:
                        logger.error(ex)
                        variables.possibility = False
                        break

                    await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        logger.error(ex)
    finally:
        variables.driver.quit()

    logger.info(f"{message.chat.id} | Finish parsing Cian")


async def yandex_site_parser(message, url_yandex):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    logger.info(f"{message.chat.id} | Start parsing Yandex")
    url = url_yandex
    variables.driver = webdriver.Safari()
    point = False

    try:
        time.sleep(1)
        variables.driver.get(url=url)
        full_page = html_to_json.convert(variables.driver.page_source)
        page_count = \
            full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][1]['div'][0]['form'][0]['div'][0]['div'][2]['div'][0]['div'][0]['div'][0]['fieldset']
        page_count = page_count[len(page_count) - 1]['div'][0]['div'][4]['div'][0]['button'][0]['span'][0]['_value']
        page_count = math.ceil(int("".join(re.findall(r"\d+", page_count))) / 20)
        url_next_page = 1
        for i, j in itertools.product(range(20), range(20)):
            try:
                url_next_page = \
                    full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['div'][i]['span'][0]['label'][j]['button'][0]['span'][0][
                        'a'][0]['_attributes']['href']
                url_next_page = f"https://realty.yandex.ru{url_next_page}"

            except Exception:
                continue
        if url_next_page == 1:
            url_next_page = url
        if page_count > 15:
            page_count = 15
            await bot_aiogram.send_message(chat_id=message.chat.id,
                                           text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
                                                '15 страниц.')
        variables.possibility = True

        for j in tqdm(range(page_count)):
            if variables.possibility is False:
                break
            else:
                if point is True:
                    break
                else:
                    index = url_next_page.find('&page=')
                    if index == -1:
                        index = url_next_page.find('?page=')
                        if index == -1:
                            url_cycle = url_next_page
                        else:
                            index = index + 6
                            url_cycle = f"{url_next_page[:index]}{j}{url_next_page[index + 1:]}"
                    else:
                        index = index + 6
                        url_cycle = f"{url_next_page[:index]}{j}{url_next_page[index + 1:]}"
                    logger.info(url_cycle)
                    variables.driver.get(url=url_cycle)
                    # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                    full_page = html_to_json.convert(variables.driver.page_source)
                    ads_count = len(full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'])
                    for i in range(ads_count):
                        ad = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]
                        if len(ad) != 3:
                            continue
                        try:
                            ad = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]['div'][0]['div'][0]

                        except Exception:
                            continue

                        full_address = []
                        for adr in range(20):
                            try:
                                address = str(ad['div'][0]['div'][0]['div'][0]['a'][adr]['_value']).replace(',', '')
                                full_address.append(address)

                            except Exception:
                                continue
                        full_address = " ".join(full_address)
                        if len(full_address) == 0:
                            full_address = []
                            for adr in range(20):
                                try:
                                    address = str(ad['div'][0]['div'][0]['div'][0]['_values'][adr]).replace(',', '')
                                    full_address.append(address)

                                except Exception:
                                    continue
                            full_address = " ".join(full_address)
                        price = "".join(re.findall(r"\d+", ad['div'][0]['div'][1]['div'][0]['span'][0]['_value']))
                        ad_url = 'https://realty.yandex.ru' + ad['div'][0]['div'][0]['a'][0]['_attributes']['href']
                        square = round(float(str(ad['div'][0]['div'][0]['a'][0]['span'][0]['_value']).split(',')[0][:3].strip()))

                        try:
                            await wwdb.data_base(status='Active', adres=full_address, price=price, square=square, url=ad_url)

                        except Exception as ex:
                            logger.error(ex)
                            point = True
                            variables.possibility = False
                            break

                        await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        logger.error(ex)
    finally:
        variables.driver.quit()

    logger.info(f"{message.chat.id} | Finish parsing Yandex")


# noinspection DuplicatedCode
async def avito_site_parser(message, url_avito):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    logger.info(f"{message.chat.id} | Start parsing Avito")
    url = url_avito
    variables.driver = webdriver.Safari()

    try:
        time.sleep(1)
        variables.driver.get(url=url)
        full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][0]['div'][0]
        page_count = math.ceil(int("".join(re.findall(r"\d+", full_page['div'][2]['div'][1]['div'][0]['span'][0]['_value']))) / 50)
        if page_count == 1:
            url_next_page = url
        else:
            for i in range(20):
                try:
                    url_next_page = full_page['div'][2]['div'][2]['div'][2]['div'][i]['div'][1]['div'][0]['a'][1]['_attributes']['href']
                    url_next_page = f"https://www.avito.ru{url_next_page}"
                    break

                except Exception:
                    continue
        if page_count > 15:
            page_count = 15
            await bot_aiogram.send_message(chat_id=message.chat.id,
                                           text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
                                                '15 страниц.')
        variables.possibility = True

        for i in tqdm(range(1, page_count + 1)):
            if variables.possibility is False:
                break
            else:
                url_cycle = await cian_avito_url_cycle_detector(url_next_page, i)  # noqa
                variables.driver.get(url=url_cycle)
                # variables.driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                full_page = html_to_json.convert(variables.driver.page_source)['html'][0]['body'][0]['div'][0]['div'][0]
                for n in range(10):
                    try:
                        ads_count = len(full_page['div'][2]['div'][2]['div'][2]['div'][n]['div'][0]['div'])
                        sp = n

                    except Exception:
                        continue
                for j in range(ads_count):  # noqa
                    ad = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]  # noqa
                    if len(ad) != 3:
                        continue
                    try:
                        ad = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]

                    except Exception:
                        continue
                    for n in range(10):
                        for m in range(10):
                            try:
                                full_address = ad['div'][0]['div'][1]['div'][n]['div'][m]['span'][0]['span'][0]['_value']
                                break

                            except Exception:
                                continue
                    helper = full_address.split(',')  # noqa
                    if len(helper) < 3:
                        full_address = full_address
                    else:
                        full_address = f"{helper[-2]} {helper[-1]}"
                    try:
                        try:
                            price = "".join(re.findall(r"\d+", ad['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_value']))

                        except Exception:
                            price = "".join(re.findall(r"\d+", ad['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_values'][0]))

                    except Exception:
                        continue
                    ad_url = 'https://www.avito.ru' + ad['div'][0]['div'][0]['a'][0]['_attributes']['href']
                    try:
                        if url_cycle.find('doma') == -1:
                            square = str(ad['div'][0]['div'][1]['div'][1]['a'][0]['h3'][0]['_value']).split(',')[1].strip()
                            if len(square) > 4:
                                square = square[:-2].strip()
                                square = round(float(square))
                            if square.find('>') != -1:
                                square = square[2:].strip()
                                square = round(float(square))
                        else:
                            square = '-'

                    except Exception:
                        square = '-'

                    try:
                        await wwdb.data_base(status='Active', adres=full_address, price=price, square=square, url=ad_url)

                    except Exception as ex:
                        logger.error(ex)
                        variables.possibility = False
                        break

                    await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        logger.error(ex)
    finally:
        variables.driver.quit()

    logger.info(f"{message.chat.id} | Finish parsing Avito")
