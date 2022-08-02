# from table_parser import *
# from site_parser import *
# from main_code import *
# from main_bot import *
#
# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.dispatcher.filters import Text
# from bs4 import BeautifulSoup as BS
# from datetime import datetime
# from selenium import webdriver
# from bs2json import bs2json
# import openpyxl as op
# from aiofiles import os
# import pandas as pd
# import html_to_json
# import psycopg2
# import requests
# import asyncio
# import aiohttp
# import pyexcel
# # import lxml
# import shutil
# import glob
# import math
# import time
# import sys
# import re
# import os

# requests

# url_upn = 'https://upn.ru/kupit/kvartiry'
# url_upn = 'https://upn.ru/kupit/kvartiry/studii-0/oblast-sverdlovskaya-1/tsena-do-3000000'

# url_cian = 'https://ekb.cian.ru/kupit-kvartiru/'
# url_cian = 'https://ekb.cian.ru/cat.php?deal_type=sale&engine_version=2&foot_min=10&kitchen_stove=electric&min_balconies=1&offer_type=flat&only_foot=2&region=4743&room2=1'

# url_yandex = 'https://realty.yandex.ru/ekaterinburg/kupit/kvartira'
# url_yandex = 'https://realty.yandex.ru/ekaterinburg/kupit/kvartira/dvuhkomnatnaya/dist-leninskij-rajon-559143/?hasPark=YES&metroTransport=ON_FOOT&timeToMetro=10&floorExceptFirst=YES'

# url_avito = 'https://www.avito.ru/ekaterinburg/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1'
# url_avito = 'https://www.avito.ru/ekaterinburg/kvartiry/prodam/vtorichka-ASgBAQICAUSSA8YQAUDmBxSMUg?cd=1&f=ASgBAQICAUSSA8YQBEDmBxSMUqy~DRSkxzW~wQ0UuP03gr0OFNCk0QE&footWalkingMetro=10'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

# PostgreSQL

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'

# Bot

token = '5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0'

# create table advertisement(
#     id SERIAL PRIMARY KEY,
#     adres varchar(255),
#     price varchar(30),
#     square varchar(10),
#     url varchar(255)
# );

# select * from advertisement;

# drop table advertisement;

