from loguru import logger

from main_code import work_with_data_base as wwdb, work_with_files as wwf
from parsers import site_parser as sp


async def site_parsing_start():
    try:
        try:
            await wwdb.create_advertisement_table()

        except Exception:
            await wwdb.delete_advertisement_table()
            await wwdb.create_advertisement_table()

    except Exception as ex:
        logger.error(ex)


async def site_parsing_main(req_site, url_upn, url_cian, url_yandex, url_avito, message):
    if req_site == 1:
        await sp.upn_site_parser(message, url_upn)
    elif req_site == 2:
        await sp.cian_site_parser(message, url_cian)
    elif req_site == 3:
        await sp.yandex_site_parser(message, url_yandex)
    elif req_site == 4:
        await sp.avito_site_parser(message, url_avito)


async def site_parsing_finish(req_res):
    try:
        if req_res != 'error':
            await wwdb.site_data_to_csv()
            if req_res == 'csv':
                await wwf.file_renaming()
            elif req_res == 'xlsx':
                await wwf.converting_csv_to_xlsx(from_where='site')
                await wwf.file_renaming()
            elif req_res == 'txt':
                await wwf.converting_csv_to_txt(from_where='site')
                await wwf.file_renaming()
            elif req_res == 'all':
                await wwf.converting_csv_to_xlsx(from_where='site')
                await wwf.converting_csv_to_txt(from_where='site')
                await wwf.file_renaming()

    except Exception as ex:
        logger.error(ex)
