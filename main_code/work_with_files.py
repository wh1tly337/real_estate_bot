import contextlib
import shutil
from datetime import datetime

import aiofiles
import openpyxl as op
import pandas as pd
import pyexcel
from aiofiles import os
from loguru import logger

from auxiliary.req_data import src
from real_estate_bot import variables


async def filename_creator(freshness):
    if freshness == 'new':
        today = datetime.now()

        minute = f'0{str(today.minute)}' if int(today.minute) < 10 else today.minute
        variables.filename = f"{today.day}.{today.month}.{today.year} - {today.hour}.{minute}"

        return variables.filename
    else:
        return variables.filename


async def table_name_handler(message):
    try:
        variables.table_name = message.document.file_name
        if variables.table_name[-3:] == 'txt' or variables.table_name[-3:] == 'csv':
            if variables.table_name.split('.')[-2][-3:] == 'upd':
                variables.table_name_upd = f"{src}{variables.table_name[:-4]}"
            else:
                variables.table_name_upd = f"{src}{variables.table_name[:-4]}_upd"
        elif variables.table_name[-4:] != 'xlsx':
            if variables.table_name.split('.')[-2][-3:] == 'upd':
                variables.table_name_upd = f"{src}{variables.table_name[:-5]}"
            else:
                variables.table_name_upd = f"{src}{variables.table_name[:-4]}_upd"

        return variables.table_name, variables.table_name_upd

    except Exception as ex:
        logger.error(ex)


async def convert_csv_to_xlsx(from_where):
    try:
        if from_where == 'site':
            file_name_to_convert = 'pars_site'
            file_name_to_convert = f"{src}{file_name_to_convert}"
        else:
            file_name_to_convert = variables.table_name_upd

        sheet = pyexcel.get_sheet(file_name=f"{file_name_to_convert}.csv", delimiter=";")
        sheet.save_as(f"{file_name_to_convert}.xlsx")
        table = op.load_workbook(f"{file_name_to_convert}.xlsx")
        main_sheet = table[f"{file_name_to_convert.split('/')[-1]}.csv"]
        main_sheet.column_dimensions['B'].width = 10
        main_sheet.column_dimensions['C'].width = 30
        main_sheet.column_dimensions['D'].width = 10
        main_sheet.column_dimensions['F'].width = 40
        table.save(f"{file_name_to_convert}.xlsx")

        logger.info('Copy .csv to .xlsx successfully')

    except Exception as ex:
        logger.error(ex)


async def convert_csv_to_txt(from_where):
    try:
        if from_where == 'site':
            file_name_to_convert = 'pars_site'
            file_name_to_convert = f"{src}{file_name_to_convert}"
        else:
            file_name_to_convert = variables.table_name_upd

        shutil.copyfile(f"{file_name_to_convert}.csv", f"{src}garages_table_4txt.csv")
        await os.rename(f"{src}garages_table_4txt.csv", f"{file_name_to_convert}.txt")

        async with aiofiles.open(f"{file_name_to_convert}.txt", 'r') as file:
            df = await file.read()
            df = df.replace(';', ' | ')
            df = df.replace('"', '')

        async with aiofiles.open(f"{file_name_to_convert}.txt", 'w') as file:
            await file.write(df)

        logger.info('Copy .csv to .txt successfully')

    except Exception as ex:
        logger.error(ex)


async def convert_txt_to_csv():
    try:
        async with aiofiles.open(f"{src}{variables.table_name}", 'r') as file:
            df = await file.read()
            df = df.replace(' | ', ';')

        async with aiofiles.open(f"{src}{variables.table_name}", 'w') as file:
            await file.write(df)

        df = pd.read_csv(f"{src}{variables.table_name}")
        df.to_csv(f"{variables.table_name_upd}.csv", index=False, header=True)

        logger.info('Copy .txt to .csv  successfully')

    except Exception as ex:
        logger.error(ex)


async def file_format_reformer():
    try:
        if variables.table_name[-3:] == 'txt':
            await convert_txt_to_csv()
        elif variables.table_name[-4:] == 'xlsx':
            # noinspection PyArgumentList
            df = pd.read_excel(f"{src}{variables.table_name}")
            df.to_csv(f"{variables.table_name_upd}.csv", index=False, header=True, sep=";")

            logger.info('Copy .xlsx to .csv  successfully')
        else:
            await os.rename(f"{src}{variables.table_name}", f"{variables.table_name_upd}.csv")

            logger.info('Already .csv file')

    except Exception as ex:
        logger.error(ex)


async def file_renamer():
    try:
        with contextlib.suppress(Exception):
            await os.rename(f"{src}pars_site.txt", f"{src}{await filename_creator(freshness='new')}.txt")

        with contextlib.suppress(Exception):
            await os.rename(f"{src}pars_site.csv", f"{src}{await filename_creator(freshness='new')}.csv")

        with contextlib.suppress(Exception):
            await os.rename(f"{src}pars_site.xlsx", f"{src}{await filename_creator(freshness='new')}.xlsx")

        logger.info('Renaming of all files was successful')

    except Exception as ex:
        logger.error(ex)


async def file_remover(from_where):
    try:
        if from_where == 'site':
            with contextlib.suppress(Exception):
                await os.remove(f"{src}{await filename_creator(freshness='load')}.csv")
            with contextlib.suppress(Exception):
                await os.remove(f"{src}{await filename_creator(freshness='load')}.xlsx")
            with contextlib.suppress(Exception):
                await os.remove(f"{src}{await filename_creator(freshness='load')}.txt")
        elif from_where == 'admin':
            with contextlib.suppress(Exception):
                await os.remove(f"{src}user_data.csv")
        else:
            with contextlib.suppress(Exception):
                await os.remove(f"{src}{variables.table_name}")
            with contextlib.suppress(Exception):
                await os.remove(f"{variables.table_name_upd}.csv")
            with contextlib.suppress(Exception):
                await os.remove(f"{variables.table_name_upd}.txt")
            with contextlib.suppress(Exception):
                await os.remove(f"{variables.table_name_upd}.xlsx")

        logger.info('Removing of all files was successful')

    except Exception as ex:
        logger.error(ex)
