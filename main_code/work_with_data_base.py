import glob


async def data_base(status, adres, price, square, url):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""INSERT INTO advertisement (status, adres, price, square, url) VALUES ('{status}', '{adres}', '{price}', '{square}', '{url}');"""
        )


async def add_data_to_data_base():
    from main_code.work_with_files import table_name_upd

    try:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute(f"""COPY update_ad FROM '/Users/user/PycharmProjects/Parser/{table_name_upd}.csv' DELIMITER ';' CSV HEADER;""")

    except Exception as ex:
        print('[ERROR] [ADD_DATA_TO_TABLE] - ', ex)


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

    print("[INFO] - PostgreSQL 'advertisement' table created")


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

    print("[INFO] - PostgreSQL 'update_ad' table created")


async def get_data_from_data_base(from_where, row):
    if from_where == 'max_row' and row is None:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM update_ad;""")
            max_row = glob.cursor.fetchall()[0][0]

        return max_row
    elif from_where == 'check' and row is None:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT count(*) FROM advertisement;""")
            check = glob.cursor.fetchall()[0][0]

        return check
    else:
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT id FROM update_ad;""")
            ad_id = glob.cursor.fetchall()[row][0]
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT url FROM update_ad;""")
            table_url = glob.cursor.fetchall()[row][0]
        with glob.connection.cursor() as glob.cursor:
            glob.cursor.execute("""SELECT price FROM update_ad;""")
            old_price = glob.cursor.fetchall()[row][0]

        return ad_id, table_url, old_price


async def site_data_to_csv():
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """COPY advertisement TO '/Users/user/PycharmProjects/Parser/pars_site.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную


async def table_data_to_csv(table_name_upd):
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            f"""COPY update_ad TO '/Users/user/PycharmProjects/Parser/{table_name_upd}.csv' (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');"""
        )
    # Скорее всего это не будет работать на сервере, нужно будет менять директорию на серверную


async def delete_advertisement_table():
    # Delete advertisement table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE advertisement;"""
        )

    print("[INFO] - PostgreSQL 'advertisement' table deleted")


async def delete_update_ad_table():
    # Delete update_ad table
    with glob.connection.cursor() as glob.cursor:
        glob.cursor.execute(
            """DROP TABLE update_ad;"""
        )

    print("[INFO] - PostgreSQL 'update_ad' table deleted")
