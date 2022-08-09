import asyncio

from bob_telegram_tools.bot import TelegramBot
from bob_telegram_tools.utils import TelegramTqdm

from auxiliary import req_data as rd
from auxiliary.all_markups import *
from main_code import all_connections as ac
from main_code import work_with_data_base as wwdb, work_with_files as wwf
from parsers import table_parser as tp


async def table_parsing_start():
    try:
        try:
            await wwdb.create_update_ad_table()
        except Exception:
            await wwdb.delete_update_ad_table()
            await wwdb.create_update_ad_table()

    except Exception as ex:
        print('[ERROR] [TABLE_PARSING_START] - ', ex)


async def table_parsing_main(message):
    try:
        bot_tqdm = TelegramBot('5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0', message.chat.id)
        tqdm = TelegramTqdm(bot_tqdm)

        await wwf.file_format_reformer()

        await wwdb.add_data_to_data_base()

        max_row = await wwdb.get_data_from_data_base(from_where='max_row', row=None)

        requirement, driver, counter = False, None, 1

        for row in tqdm(range(max_row)):
            # maybe this stopper work not correctly
            if counter is None:
                break
            else:
                for id_handler in range(max_row):
                    try:
                        ad_id, table_url, old_price = await wwdb.get_data_from_data_base(from_where='else', row=row)

                        if ad_id != counter:
                            continue
                        else:
                            if table_url[:14] == 'https://upn.ru':
                                try:
                                    await tp.upn_table_parser(table_url=table_url, old_price=old_price)

                                except Exception as ex:
                                    print('[ERROR] [UPN_TABLE_PARSER] - ', ex)

                            elif table_url[:19] == 'https://ekb.cian.ru':
                                if driver is None:
                                    driver = await ac.add_driver()

                                requirement = True

                                try:
                                    await tp.cian_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [CIAN_TABLE_PARSER] - ', ex)

                            elif table_url[:24] == 'https://realty.yandex.ru':
                                if driver is None:
                                    driver = await ac.add_driver()

                                requirement = True

                                try:
                                    await tp.yandex_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [YANDEX_TABLE_PARSER] - ', ex)

                            elif table_url[:20] == 'https://www.avito.ru':
                                if driver is None:
                                    driver = await ac.add_driver()

                                requirement = True

                                try:
                                    await tp.avito_table_parser(table_url=table_url, old_price=old_price, driver=driver)

                                except Exception as ex:
                                    print('[ERROR] [AVITO_TABLE_PARSER] - ', ex)

                            counter += 1

                    except Exception as ex:
                        await asyncio.sleep(5)
                        print('[ERROR] [TABLE_CYCLE] - ', ex)
                        counter = None
                        break

        if requirement:
            await ac.close_driver()

        if counter is not None:
            await table_parsing_finish()

            await rd.bot.send_message(chat_id=message.chat.id, text="Вся информация обновлена. В каком формате вы хотите получить результат?", reply_markup=markup_result, parse_mode="Markdown")

            print("[INFO] - Table successfully updated")

    except Exception as ex:
        print('[ERROR] [TABLE_PARSER_MAIN] - ', ex)


async def table_parsing_finish():
    try:
        from main_code.work_with_files import table_name_upd

        await wwdb.table_data_to_csv(table_name_upd)

    except Exception as ex:
        print('[ERROR] [TABLE_PARSING_FINISH] - ', ex)
