import glob

from loguru import logger

from auxiliary.req_data import src


async def data_base(status, adres, price, square, url):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""INSERT INTO advertisement (status, adres, price, square, url) VALUES ('{status}', '{adres}', '{price}', '{square}', '{url}');"""
        )


async def user_data(user_id, user_full_name, user_username, settings, num_site_req, num_table_req, date_last_site_req, date_last_table_req):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""INSERT INTO user_data (user_id, user_full_name, user_username, settings, num_site_req, num_table_req, date_last_site_req, date_last_table_req) 
            VALUES ('{user_id}', '{user_full_name}', '{user_username}', '{settings}', '{num_site_req}', '{num_table_req}', '{date_last_site_req}', '{date_last_table_req}');"""
        )


# noinspection DuplicatedCode
async def update_user_data(user_id, num_site_req, num_table_req, date_last_site_req, date_last_table_req):
    with glob.connection.cursor() as glob.cursor:
        if num_site_req:
            glob.cursor.execute(f"""SELECT num_site_req FROM user_data WHERE user_id = '{user_id}';""")
            num_site = int(glob.cursor.fetchall()[0][0]) + 1

            glob.cursor.execute(f"""SELECT num_table_req FROM user_data WHERE user_id = '{user_id}';""")
            num_table = glob.cursor.fetchall()[0][0]

            date_last_site = str(date_last_site_req).split('-')
            date = date_last_site[0].replace('.', '-')
            time = date_last_site[1].replace('.', '-')
            date_last_site = f"{date}/{time}".replace(' ', '')

            glob.cursor.execute(f"""SELECT date_last_table_req FROM user_data WHERE user_id = '{user_id}';""")
            date_last_table = glob.cursor.fetchall()[0][0]
        elif num_table_req:
            glob.cursor.execute(f"""SELECT num_site_req FROM user_data WHERE user_id = '{user_id}';""")
            num_site = glob.cursor.fetchall()[0][0]

            glob.cursor.execute(f"""SELECT num_table_req FROM user_data WHERE user_id = '{user_id}';""")
            num_table = int(glob.cursor.fetchall()[0][0]) + 1

            glob.cursor.execute(f"""SELECT date_last_site_req FROM user_data WHERE user_id = '{user_id}';""")
            date_last_site = glob.cursor.fetchall()[0][0]

            date_last_table = str(date_last_table_req).split('-')
            date = date_last_table[0].replace('.', '-')
            time = date_last_table[1].replace('.', '-')
            date_last_table = f"{date}/{time}".replace(' ', '')

        glob.cursor.execute(
            f"""UPDATE user_data SET 
            num_site_req = '{num_site}', 
            num_table_req = '{num_table}', 
            date_last_site_req = '{date_last_site}', 
            date_last_table_req = '{date_last_table}' 
            WHERE user_id = '{user_id}';"""
        )


async def update_user_data_settings(settings_format, user_id):
    glob.cursor.execute(
        f"""UPDATE user_data SET settings = '{settings_format}' WHERE user_id = '{user_id}';"""
    )


async def get_user_settings(user_id):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(f"""SELECT settings FROM user_data WHERE user_id = '{user_id}';""")
        user_settings = glob.cursor.fetchall()[0][0]

    return user_settings


async def get_user_data_table():
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""COPY user_data TO '{src}user_data.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )


async def add_data_to_data_base():
    from real_estate_bot import variables

    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""COPY update_ad FROM '{variables.table_name_upd}.csv' DELIMITER ';' CSV HEADER;""")

    except Exception as ex:
        logger.error(ex)


async def create_advertisement_table():
    # Create new advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """CREATE TABLE advertisement(
                id SERIAL PRIMARY KEY,
                status VARCHAR(255),
                adres VARCHAR(255),
                price VARCHAR(30),
                square VARCHAR(10),
                url VARCHAR(255));"""
        )

    logger.info('PostgreSQL "advertisement" table created')


async def create_update_ad_table():
    # Create new update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """CREATE TABLE update_ad(
                id SERIAL PRIMARY KEY,
                status VARCHAR(255),
                adres VARCHAR(255),
                price VARCHAR(30),
                square VARCHAR(10),
                url VARCHAR(255));"""
        )

    logger.info('PostgreSQL "update_ad" table created')


async def get_data_from_data_base(from_where, row):
    if from_where == 'max_row' and row is None:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM update_ad;""")
            max_row = glob.cursor.fetchall()[0][0]

        return max_row
    elif from_where == 'start' and row is None:
        user_ids = []
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM user_data;""")
            max_row = glob.cursor.fetchall()[0][0]
            glob.cursor.execute("""SELECT user_id FROM user_data;""")
            for i in range(max_row):
                user_ids.append(int(glob.cursor.fetchone()[0]))

        return user_ids
    elif from_where == 'check' and row is None:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM advertisement;""")
            check = glob.cursor.fetchall()[0][0]

        return check
    else:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT id FROM update_ad ORDER BY id;""")
            ad_id = glob.cursor.fetchall()[row][0]
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT url FROM update_ad ORDER BY id;""")
            table_url = glob.cursor.fetchall()[row][0]
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT price FROM update_ad ORDER BY id;""")
            old_price = glob.cursor.fetchall()[row][0]

        return ad_id, table_url, old_price


async def site_data_to_csv():
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""COPY advertisement TO '{src}pars_site.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную


async def table_data_to_csv(table_name_upd):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""COPY update_ad TO '{table_name_upd}.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную


async def delete_advertisement_table():
    # Delete advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE advertisement;"""
        )

    logger.info('PostgreSQL "advertisement" table deleted')


async def delete_update_ad_table():
    # Delete update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE update_ad;"""
        )

    logger.info('PostgreSQL "update_ad" table deleted')
