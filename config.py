from os import getenv
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv('.env')

token = getenv("TOKEN")
bot = Bot(token, parse_mode="HTML")

youmoney_token = getenv("YOUMONEY_TOKEN")

payok_token = getenv("PAYOK_TOKEN")
payok_sk = getenv("PAYOK_SK")
payok_shop_id = getenv("PAYOK_SHOP_ID")
payok_api_id = getenv("PAYOK_API_ID")

master_id = int(getenv("MASTER_ID"))
master_id1 = int(getenv("MASTER_ID1"))
master_id2 = int(getenv("MASTER_ID2"))
master_id3 = int(getenv("MASTER_ID3"))
master_id4 = int(getenv("MASTER_ID4"))
master_id5 = int(getenv("MASTER_ID5"))
master_id6 = int(getenv("MASTER_ID6"))

masters = [master_id, master_id1, master_id2, master_id3, master_id4, master_id5, master_id6]


db_user = getenv("DB_USER")
db_pass = getenv("DB_PASS")
db_name = getenv("DB_NAME")
db_host = getenv("DB_HOST")
db_port = getenv("DB_PORT")

redis_host = getenv("REDIS_HOST")
redis_port = getenv("REDIS_PORT")
redis_user = getenv("REDIS_USER")
redis_pass = getenv("REDIS_PASS")

REDIS_URL = f"redis://{redis_user}:{redis_pass}@{redis_host}:{redis_port}/0"

