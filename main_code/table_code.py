import asyncio

from bob_telegram_tools.bot import TelegramBot
from bob_telegram_tools.utils import TelegramTqdm
from loguru import logger

from real_estate_bot import main_bot as mb
from main_code import (
    all_connections as ac,
    work_with_data_base as wwdb,
    work_with_files as wwf
)
from parsers import table_parser as tp


async def table_parsing_start():
    try:
        try:
            await wwdb.create_update_ad_table()
        except Exception:
            await wwdb.delete_update_ad_table()
            await wwdb.create_update_ad_table()

    except Exception as ex:
        logger.error(ex)


async def table_parsing_main(message):
    try:
        bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
        tqdm = TelegramTqdm(bot_tqdm)

        logger.info(f"{message.chat.id} | Table update start")

        await wwf.file_format_reformer()

        await wwdb.add_data_to_data_base()

        max_row = await wwdb.get_data_from_data_base(from_where='max_row', row=None)

        requirement, driver, flag = False, None, True

        for row in tqdm(range(max_row)):
            ad_id, table_url, old_price = await wwdb.get_data_from_data_base(from_where='else', row=row)
            # maybe this stopper work not correctly
            if flag is False:
                break
            else:
                if table_url[:14] == 'https://upn.ru':
                    try:
                        await tp.upn_table_parser(table_url=table_url, old_price=old_price)

                    except Exception as ex:
                        await asyncio.sleep(5)
                        logger.error(ex)
                        flag = False
                        break

                elif table_url[:19] == 'https://ekb.cian.ru':
                    if driver is None:
                        driver = await ac.add_driver()

                    requirement = True

                    try:
                        await tp.cian_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                    except Exception as ex:
                        await asyncio.sleep(5)
                        logger.error(ex)
                        flag = False
                        break

                elif table_url[:24] == 'https://realty.yandex.ru':
                    if driver is None:
                        driver = await ac.add_driver()

                    requirement = True

                    try:
                        await tp.yandex_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                    except Exception as ex:
                        await asyncio.sleep(5)
                        logger.error(ex)
                        flag = False
                        break

                elif table_url[:20] == 'https://www.avito.ru':
                    if driver is None:
                        driver = await ac.add_driver()

                    requirement = True

                    try:
                        await tp.avito_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                    except Exception as ex:
                        await asyncio.sleep(5)
                        logger.error(ex)
                        flag = False
                        break

        if requirement:
            await ac.close_driver()

        if flag:
            await table_parsing_finish()

            await mb.table_parser_end_with_settings(message)

            logger.info(f"{message.chat.id} | Table successfully updated")

    except Exception as ex:
        logger.error(ex)


async def table_parsing_finish():
    try:
        from main_code.work_with_files import table_name_upd

        await wwdb.table_data_to_csv(table_name_upd)

    except Exception as ex:
        logger.error(ex)
