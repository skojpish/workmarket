from os import getenv
from aiogram import Bot
from dotenv import load_dotenv


load_dotenv('.env')

token = getenv("TOKEN")
bot = Bot(token, parse_mode="HTML")

pay_token = getenv("PAYMENT_TOKEN")

master_id = int(getenv("MASTER_ID"))

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

