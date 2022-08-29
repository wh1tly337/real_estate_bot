from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

admin_id = 726420734
admin_password = '8361'

bot_aiogram = Bot(token='5432400118:AAFgz1QNbckgmQ7X1jbEu87S2ZdhV6vU1m0')
dp = Dispatcher(bot_aiogram, storage=MemoryStorage())

src = '/Users/user/PycharmProjects/Parser/files/'
src_logger = '/Users/user/PycharmProjects/Parser/logger/'
# src = 'files/'
# src_logger = 'logger/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

host = '127.0.0.1'
user = 'user'
password = '13579001Ivan+'
db_name = 'postgres'
# host = 'ec2-52-49-120-150.eu-west-1.compute.amazonaws.com'
# user = 'eouelnwfidefyc'
# password = '1cfe0954060f8054713c2e579b8c7b1332419ac02c715c76e16c81bd2cff4b6c'
# db_name = 'dad0gaqh88mkuc'
