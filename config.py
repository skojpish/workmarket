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


