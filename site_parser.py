from main_bot import data_base

from bs4 import BeautifulSoup as BS
from selenium import webdriver
from bs2json import bs2json
import html_to_json
import requests
import telebot
# import lxml
import math
import time
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

token = '5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0'
bot = telebot.TeleBot(token)


def upn_parser(message, url_upn):
    print("[INFO] - Start parsing UPN")
    if url_upn[-7:-2] == '?page':
        url = url_upn[:-7]
    elif url_upn[-8:-3] == '?page':
        url = url_upn[:-8]
    elif url_upn[-9:-4] == '?page':
        url = url_upn[:-9]
    elif url_upn[-10:-5] == '?page':
        url = url_upn[:-10]
    else:
        url = url_upn
    request = requests.get(url, headers=headers).text
    response = BS(request, 'lxml')
    num_of_pages = math.ceil(int("".join(re.findall(r'\d+', str(
        bs2json().convert(response.find())['html']['head']['title']['text']).split('|')[1]))) / 25)
    if num_of_pages > 15:
        num_of_pages = 15
        bot.send_message(message.chat.id,
                         text="Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 страниц.")
    for j in range(1, num_of_pages + 1):
        try:
            if re.search(r'\d+', url[-1]):
                url_cycle = url + f'?page={j}'
            else:
                url_cycle = url + f'?page={j}'
            print(url_cycle)
            request = requests.get(url_cycle, headers=headers).text
            response = BS(request, 'lxml')
            advertisement = bs2json().convert(response.find())['html']['body']['div'][4]['main']['div']['div'][2]['div'][1]['div'][1]['div']
            num_of_ads = len(advertisement)
            for i in range(num_of_ads):
                if len(advertisement[i]) == 1:
                    continue
                if len(advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']) == 3:
                    price = "".join(re.findall(r'\d+', advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div']['text']))
                else:
                    price = "".join(re.findall(r'\d+', advertisement[i]['div'][1]['div'][7]['div'][0]['div'][0]['div'][1]['text']))
                full_address = "".join((advertisement[i]['div'][1]['div'][1]['span']['text']).split(',')[-2:])
                url_ad = 'https://upn.ru' + advertisement[i]['div'][1]['a']['attributes']['href']
                square = "".join((advertisement[i]['div'][1]['div'][2]['div'][0]['div'][1]['text']).split('/')[0])
                try:
                    data_base(adres=full_address, price=price, square=square, url=url_ad)
                except:
                    quit()
        except Exception as ex:
            print("[ERROR UPN] - ", ex)
    print("[INFO] - Finish parsing UPN")


def cian_parser(message, url_cian):
    print("[INFO] - Start parsing Cian")
    url = url_cian
    try:
        driver = webdriver.Safari()
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]
        for i in range(20):
            try:
                num_of_pages = math.ceil(int("".join(re.findall(r'\d+', full_page['div'][0]['div'][0]['div'][i]['div'][0]['div'][0]['h5'][0]['_value']))) / 28)
                break
            except:
                continue
        url_next_page = 1
        for i in range(20):
            try:
                url_next_page = full_page['div'][0]['div'][0]['div'][i]['div'][0]['ul'][0]['li'][1]['a'][0]['_attributes']['href']
                break
            except:
                continue
        if url_next_page == 1:
            url_next_page = url
        if num_of_pages > 15:
            num_of_pages = 15
            bot.send_message(message.chat.id,
                             text="Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 страниц.")
        for i in range(1, num_of_pages + 1):
            pos = url_next_page.find(f'&p=')
            if pos == -1:
                url_cycle = url_next_page
            else:
                pos = pos + 3
                url_cycle = url_next_page[:pos] + f"{i}" + url_next_page[pos + 1:]
            print(url_cycle)
            driver.get(url=url_cycle)
            full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]
            for j in range(20):
                try:
                    sp = j
                    num_of_ads = len(full_page['div'][0]['div'][0]['div'][j]['article'])
                    break
                except:
                    continue
            for j in range(num_of_ads):
                advertisement = full_page['div'][0]['div'][0]['div'][sp]['article'][j]
                url_ad = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['a'][0]['_attributes']['href']
                try:
                    square = str(advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']).split(',')[1].strip()[:3].strip()
                except:
                    square = '-'
                for n in range(10):
                    for m in range(10):
                        try:
                            sp_1 = len(advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'])
                            street_address = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 2]['_value']
                            number_address = advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][m]['div'][n]['a'][sp_1 - 1]['_value']
                            full_address = f"{street_address} {number_address}"
                        except:
                            continue
                for n in range(10):
                    try:
                        price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][n]['div'][0]['span'][0]['span'][0]['_value']))
                        break
                    except:
                        continue
                try:
                    data_base(adres=full_address, price=price, square=square, url=url_ad)
                except:
                    quit()
    except Exception as ex:
        print("[ERROR CIAN] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Cian")


def yandex_parser(message, url_yandex):
    print("[INFO]  - Start parsing Yandex")
    url = url_yandex
    try:
        driver = webdriver.Safari()
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)
        num_of_pages = \
            full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][1]['div'][0]['form'][0]['div'][0]['div'][2]['div'][0]['div'][0]['div'][0][
                'fieldset']
        num_of_pages = num_of_pages[len(num_of_pages) - 1]['div'][0]['div'][4]['div'][0]['button'][0]['span'][0]['_value']
        num_of_pages = math.ceil(int("".join(re.findall(r'\d+', num_of_pages))) / 20)
        url_next_page = 1
        for i in range(20):
            for j in range(20):
                try:
                    url_next_page = \
                        full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['div'][i]['span'][0]['label'][j]['button'][0]['span'][0][
                            'a'][0]['_attributes']['href']
                    url_next_page = 'https://realty.yandex.ru' + url_next_page
                except:
                    continue
        if url_next_page == 1:
            url_next_page = url
        if num_of_pages > 15:
            num_of_pages = 15
            bot.send_message(message.chat.id,
                             text="Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 страниц.")
        for j in range(num_of_pages):
            pos = url_next_page.find(f'&page=')
            if pos == -1:
                pos = url_next_page.find(f'?page=')
                if pos == -1:
                    url_cycle = url_next_page
                else:
                    pos = pos + 6
                    url_cycle = url_next_page[:pos] + f"{j}" + url_next_page[pos + 1:]
            else:
                pos = pos + 6
                url_cycle = url_next_page[:pos] + f"{j}" + url_next_page[pos + 1:]
            print(url_cycle)
            driver.get(url=url_cycle)
            full_page = html_to_json.convert(driver.page_source)
            num_of_ads = len(full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'])
            for i in range(num_of_ads):
                advertisement = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]
                if len(advertisement) == 3:
                    try:
                        advertisement = full_page['html'][0]['body'][0]['div'][1]['div'][1]['div'][0]['div'][0]['div'][1]['div'][3]['ol'][0]['li'][i]['div'][0]['div'][0]
                    except:
                        continue
                else:
                    continue
                full_address = ("".join(str(advertisement['div'][0]['div'][0]['div'][0]['_value']).split(',')[-2:])).strip()
                price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][0]['span'][0]['_value']))
                url_ad = 'https://realty.yandex.ru' + advertisement['div'][0]['div'][0]['a'][0]['_attributes']['href']
                square = str(advertisement['div'][0]['div'][0]['a'][0]['span'][0]['_value']).split(',')[0][:3].strip()
                try:
                    data_base(adres=full_address, price=price, square=square, url=url_ad)
                except:
                    quit()
    except Exception as ex:
        print("[ERROR YANDEX] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Yandex")


def avito_parser(message, url_avito):
    print("[INFO] - Start parsing Avito")
    url = url_avito
    try:
        driver = webdriver.Safari()
        time.sleep(1)
        driver.get(url=url)
        full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][0]
        num_of_pages = math.ceil(int("".join(re.findall(r'\d+', full_page['div'][2]['div'][1]['div'][0]['span'][0]['_value']))) / 50)
        if num_of_pages == 1:
            url_next_page = url
        else:
            for i in range(20):
                try:
                    url_next_page = full_page['div'][2]['div'][2]['div'][2]['div'][i]['div'][1]['div'][0]['a'][1]['_attributes']['href']
                    url_next_page = 'https://www.avito.ru' + url_next_page
                    break
                except:
                    continue
        if num_of_pages > 15:
            num_of_pages = 15
            bot.send_message(message.chat.id,
                             text="Вы ввели ссылку с слишком большим количеством объявлений. Более точно настройте фильтры или оставьте все так, но я обработаю только 15 страниц.")
        for i in range(1, num_of_pages + 1):
            pos = url_next_page.find(f'&p=')
            if pos == -1:
                url_cycle = url_next_page
            else:
                pos = pos + 3
                url_cycle = url_next_page[:pos] + f"{i}" + url_next_page[pos + 1:]
            print(url_cycle)
            driver.get(url=url_cycle)
            full_page = html_to_json.convert(driver.page_source)['html'][0]['body'][0]['div'][0]
            for n in range(10):
                try:
                    num_of_ads = len(full_page['div'][2]['div'][2]['div'][2]['div'][n]['div'][0]['div'])
                    sp = n
                except:
                    continue
            for j in range(num_of_ads):
                advertisement = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]
                if len(advertisement) == 3:
                    try:
                        advertisement = full_page['div'][2]['div'][2]['div'][2]['div'][sp]['div'][0]['div'][j]
                    except:
                        continue
                else:
                    continue
                for n in range(10):
                    for m in range(10):
                        try:
                            full_address = advertisement['div'][0]['div'][1]['div'][n]['div'][m]['span'][0]['span'][0]['_value']
                            break
                        except:
                            continue
                helper = full_address.split(',')
                if len(helper) < 3:
                    full_address = full_address
                else:
                    full_address = helper[-2] + ' ' + helper[-1]
                try:
                    try:
                        price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_value']))
                    except:
                        price = "".join(re.findall(r'\d+', advertisement['div'][0]['div'][1]['div'][2]['span'][0]['span'][0]['span'][0]['_values'][0]))
                except:
                    continue
                url_ad = 'https://www.avito.ru' + advertisement['div'][0]['div'][0]['a'][0]['_attributes']['href']
                try:
                    if url_cycle.find(f"doma") == -1:
                        square = str(advertisement['div'][0]['div'][1]['div'][1]['a'][0]['h3'][0]['_value']).split(',')[1].strip()
                        if len(square) > 4:
                            square = square[:-2].strip()
                        if square.find('>') != -1:
                            square = square[2:].strip()
                    else:
                        square = '-'
                except:
                    square = '-'
                try:
                    data_base(adres=full_address, price=price, square=square, url=url_ad)
                except:
                    quit()
    except Exception as ex:
        print("[ERROR AVITO] - ", ex)
    finally:
        driver.quit()
    print("[INFO] - Finish parsing Avito")
