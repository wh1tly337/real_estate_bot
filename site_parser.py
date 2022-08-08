import asyncio
import itertools
# import lxml
import math
import random
import re
import time
# from random import randint

import html_to_json
import requests
from aiogram import Bot, Dispatcher
from bob_telegram_tools.bot import TelegramBot
from bob_telegram_tools.utils import TelegramTqdm
from bs2json import bs2json
from bs4 import BeautifulSoup
from selenium import webdriver

import main_code as mc
from req_data import *

bot = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot)


async def cian_avito_url_cycle_detector(url_next_page, i):
    pos = url_next_page.find('&p=')
    if pos == -1:
        url_cycle = url_next_page
    else:
        pos = pos + 3
        url_cycle = f"{url_next_page[:pos]}{i}{url_next_page[pos + 1:]}"
    print(url_cycle)

    return url_cycle


async def upn_site_parser(message, url_upn):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    print("[INFO] - Start parsing UPN")
    pos = url_upn.find('?page')
    url = url_upn if pos == -1 else url_upn[:pos]
    request = requests.get(url, headers=headers).text
    response = BeautifulSoup(request, 'lxml')

    num_of_pages = math.ceil(int("".join(re.findall(r'\d+', str(
        bs2json().convert(response.find())['html']['head']['title']['text']).split('|')[1]))) / 25)
    if num_of_pages > 15:
        num_of_pages = 15
        await bot.send_message(chat_id=message.chat.id, text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 '
                                                             'страниц.')

    possibility = True

    for j in tqdm(range(1, num_of_pages + 1)):
        try:
            if re.search(r'\d+', url[-1]):
                url_cycle = f'{url}?page={j}'
            else:
                url_cycle = f'{url}?page={j}'
            print(url_cycle)
            request = requests.get(url_cycle, headers=headers).text
            response = BeautifulSoup(request, 'lxml')
            advertisement = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][2]['div'][1]['div'][1]['div']
            num_of_ads = len(advertisement)
            for i in range(num_of_ads):
                if possibility is False:
                    break
                else:
                    if len(advertisement[i]) == 1:
                        continue
                    if len(advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']) == 3:
                        price = "".join(re.findall(r'\d+', advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']['text']))
                    else:
                        price = "".join(re.findall(r'\d+', advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div'][1]['text']))
                    full_address = "".join((advertisement[i]['div'][1]['div'][1]['span']['text']).split(',')[-2:])
                    url_ad = 'https://upn.ru' + advertisement[i]['div'][1]['a']['attributes']['href']
                    square = round(float("".join((advertisement[i]['div'][1]['div'][2]['div'][0]['div'][1]['text']).split('/')[0])))

                    try:
                        await mc.data_base(status='Active', adres=full_address, price=price, square=square, url=url_ad)
                    except Exception as ex:
                        print("[ERROR] [DATA_BASE] - ", ex)
                        possibility = False
                        break

        except Exception as ex:
            print("[ERROR] [UPN_SITE_PARSER] - ", ex)
    print("[INFO] - Finish parsing UPN")


async def cian_site_parser(message, url_cian):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    print("[INFO] - Start parsing Cian")
    url = url_cian
    driver = webdriver.Safari()
    try:
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]
        for i in range(20):
            try:
                num_of_pages = math.ceil(int("".join(re.findall(r'\d+', full_page['div'][0]['div'][0]['div'][i]['div'][0]['div'][0]['h5'][0]['_value']))) / 28)
                break
            except Exception:
                continue
        if num_of_pages > 15:
            num_of_pages = 15
            await bot.send_message(chat_id=message.chat.id, text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
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

        possibility = True

        for i in tqdm(range(1, num_of_pages + 1)):
            if possibility is False:
                break
            else:
                url_cycle = await cian_avito_url_cycle_detector(url_next_page, i)
                driver.get(url=url_cycle)
                # driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]
                for j in range(20):
                    try:
                        sp = j
                        num_of_ads = len(full_page['div'][0]['div'][0]['div'][j]['article'])
                        break
                    except Exception:
                        continue
                for j in range(num_of_ads):
                    advertisement = full_page['div'][0]['div'][0]['div'][sp]['article'][j]
                    url_ad = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['a'][0]['_attributes']['href']
                    try:
                        square = round(float(str(advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']).split(',')[1].strip()[:3].strip()))
                    except Exception:
                        square = '-'
                    for n, m in itertools.product(range(10), range(10)):
                        try:
                            sp_1 = len(advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'])
                            street_address = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 2]['_value']
                            number_address = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 1]['_value']
                            full_address = f"{street_address} {number_address}"
                        except Exception:
                            continue
                    for n in range(10):
                        try:
                            price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][n]['div'][0]['span'][0]['span'][0]['_value']))
                            break
                        except Exception:
                            continue

                    try:
                        await mc.data_base(status='Active', adres=full_address, price=price, square=square, url=url_ad)
                    except Exception as ex:
                        print("[ERROR] [DATA_BASE] - ", ex)
                        possibility = False
                        break

                    await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        print("[ERROR] [CIAN_SITE_PARSER] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Cian")


async def yandex_site_parser(message, url_yandex):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    print("[INFO]  - Start parsing Yandex")
    url = url_yandex
    driver = webdriver.Safari()
    point = False
    try:
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)
        num_of_pages = \
            full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][1]['div'][0]['form'][0]['div'][0]['div'][2]['div'][0]['div'][0]['div'][0]['fieldset']
        num_of_pages = num_of_pages[len(num_of_pages) - 1]['div'][0]['div'][4]['div'][0]['button'][0]['span'][0]['_value']
        num_of_pages = math.ceil(int("".join(re.findall(r'\d+', num_of_pages))) / 20)
        url_next_page = 1
        for i, j in itertools.product(range(20), range(20)):
            try:
                url_next_page = \
                    full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['div'][i]['span'][0]['label'][j]['button'][0]['span'][0][
                        'a'][0]['_attributes']['href']
                url_next_page = f'https://realty.yandex.ru{url_next_page}'
            except Exception:
                continue
        if url_next_page == 1:
            url_next_page = url
        if num_of_pages > 15:
            num_of_pages = 15
            await bot.send_message(chat_id=message.chat.id, text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
                                                                 '15 страниц.')
        possibility = True

        for j in tqdm(range(num_of_pages)):
            if possibility is False:
                break
            else:
                if point is True:
                    break
                else:
                    pos = url_next_page.find('&page=')
                    if pos == -1:
                        pos = url_next_page.find('?page=')
                        if pos == -1:
                            url_cycle = url_next_page
                        else:
                            pos = pos + 6
                            url_cycle = f"{url_next_page[:pos]}{j}{url_next_page[pos + 1:]}"
                    else:
                        pos = pos + 6
                        url_cycle = f"{url_next_page[:pos]}{j}{url_next_page[pos + 1:]}"
                    print(url_cycle)
                    driver.get(url=url_cycle)
                    # driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                    full_page = html_to_json.convert(driver.page_source)
                    num_of_ads = len(full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'])
                    for i in range(num_of_ads):
                        advertisement = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]
                        if len(advertisement) != 3:
                            continue
                        try:
                            advertisement = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]['div'][0]['div'][0]
                        except Exception:
                            continue
                        full_address = []
                        for adr in range(20):
                            try:
                                address = str(advertisement['div'][0]['div'][0]['div'][0]['a'][adr]['_value']).replace(',', '')
                                full_address.append(address)
                            except Exception:
                                address = str(advertisement['div'][0]['div'][0]['div'][0]['text'][adr]).replace(',', '')
                                full_address.append(address)
                            finally:
                                continue
                        full_address = ' '.join(full_address)
                        price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][0]['span'][0]['_value']))
                        url_ad = 'https://realty.yandex.ru' + advertisement['div'][0]['div'][0]['a'][0]['_attributes']['href']
                        square = round(float(str(advertisement['div'][0]['div'][0]['a'][0]['span'][0]['_value']).split(',')[0][:3].strip()))

                        try:
                            await mc.data_base(status='Active', adres=full_address, price=price, square=square, url=url_ad)
                        except Exception as ex:
                            print("[ERROR] [DATA_BASE] - ", ex)
                            point = True
                            possibility = False
                            break

                        await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        print("[ERROR] [YANDEX_SITE_PARSER] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Yandex")


async def avito_site_parser(message, url_avito):
    bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
    tqdm = TelegramTqdm(bot_tqdm)

    print("[INFO] - Start parsing Avito")
    url = url_avito
    driver = webdriver.Safari()
    try:
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][0]['div'][0]
        num_of_pages = math.ceil(int("".join(re.findall(r'\d+', full_page['div'][2]['div'][1]['div'][0]['span'][0]['_value']))) / 50)
        if num_of_pages == 1:
            url_next_page = url
        else:
            for i in range(20):
                try:
                    url_next_page = full_page['div'][2]['div'][2]['div'][2]['div'][i]['div'][1]['div'][0]['a'][1]['_attributes']['href']
                    url_next_page = f'https://www.avito.ru{url_next_page}'
                    break
                except Exception:
                    continue
        if num_of_pages > 15:
            num_of_pages = 15
            await bot.send_message(chat_id=message.chat.id, text='Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только '
                                                                 '15 страниц.')
        possibility = True

        for i in tqdm(range(1, num_of_pages + 1)):
            if possibility is False:
                break
            else:
                url_cycle = await cian_avito_url_cycle_detector(url_next_page, i)
                driver.get(url=url_cycle)
                # driver.execute_script(f"window.scrollTo(0, {randint(0, 1080)})")
                full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][0]['div'][0]
                for n in range(10):
                    try:
                        num_of_ads = len(full_page['div'][2]['div'][2]['div'][2]['div'][n]['div'][0]['div'])
                        sp = n
                    except Exception:
                        continue
                for j in range(num_of_ads):
                    advertisement = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]
                    if len(advertisement) != 3:
                        continue
                    try:
                        advertisement = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]
                    except Exception:
                        continue
                    for n in range(10):
                        for m in range(10):
                            try:
                                full_address = advertisement['div'][0]['div'][1]['div'][n]['div'][m]['span'][0]['span'][0]['_value']
                                break
                            except Exception:
                                continue
                    helper = full_address.split(',')
                    if len(helper) < 3:
                        full_address = full_address
                    else:
                        full_address = f'{helper[-2]} {helper[-1]}'
                    try:
                        try:
                            price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_value']))
                        except Exception:
                            price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_values'][0]))
                    except Exception:
                        continue
                    url_ad = 'https://www.avito.ru' + advertisement['div'][0]['div'][0]['a'][0]['_attributes']['href']
                    try:
                        if url_cycle.find('doma') == -1:
                            square = str(advertisement['div'][0]['div'][1]['div'][1]['a'][0]['h3'][0]['_value']).split(',')[1].strip()
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
                        await mc.data_base(status='Active', adres=full_address, price=price, square=square, url=url_ad)
                    except Exception as ex:
                        print("[ERROR] [DATA_BASE] - ", ex)
                        possibility = False
                        break

                    await asyncio.sleep(float('{:.3f}'.format(random.random())))

    except Exception as ex:
        print("[ERROR] [AVITO_SITE_PARSER] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Avito")
