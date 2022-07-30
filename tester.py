import asyncio
import itertools
import math
import re

import aiohttp
import html_to_json


async def get_page_data(session, page, url_next_page):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    pos = url_next_page.find('&p=')
    if pos == -1:
        url = url_next_page
    else:
        pos = pos + 3
        url = f"{url_next_page[:pos]}{page}{url_next_page[pos + 1:]}"

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        response_text = html_to_json.convert(response_text)

        full_page = response_text['html'][0]['body'][0]
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
                square = str(advertisement['div'][0]['div'][1]['div'][0]['div'][0]['div'][0]['span'][0]['span'][0]['_value']).split(',')[1].strip()[:3].strip()
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
            print(price, square, full_address, url_ad)
            await asyncio.sleep(0.5)
            # try:
            #     await data_base(adres=full_address, price=price, square=square, url=url_ad)
            # except Exception:
            #     quit()


async def gather_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    url = 'https://ekb.cian.ru/kupit-kvartiru/'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        full_page = await response.text()
        full_page = html_to_json.convert(full_page)

        for i in range(20):
            try:
                num_of_pages = math.ceil(int("".join(re.findall(r'\d+', full_page['html'][0]['body'][0]['div'][0]['div'][0]['div'][i]['div'][0]['div'][0]['h5'][0]['_value']))) / 28)
                break
            except Exception:
                continue

        url_next_page = 1
        for i in range(20):
            try:
                url_next_page = full_page['html'][0]['body'][0]['div'][0]['div'][0]['div'][i]['div'][0]['ul'][0]['li'][1]['a'][0]['_attributes']['href']
                break
            except Exception:
                continue
        if url_next_page == 1:
            url_next_page = url

        tasks = []

        for page in range(1, num_of_pages + 1):
            task = asyncio.create_task(get_page_data(session, page, url_next_page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.run(gather_data())


if __name__ == '__main__':
    main()
