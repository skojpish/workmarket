# WorkMarketBot
![](https://shields.microej.com/badge/python-3.10-orange)
![](https://shields.microej.com/badge/aiogram-v3.4.1-lightblue)
![](https://shields.microej.com/badge/sqlalchemy-v2.0.28-red)
![](https://shields.microej.com/badge/alembic-v1.13.1-blue)


## Описание
WorkMarketBot - это телеграм бот для покупки размещения рекламы в сети каналов WorkMarket.
В данном боте можно выбрать нужные для размещения каналы, заполнить данные рекламного поста, выбрать дату и время публикации, после чего необходимо произвести оплату переводом
на кошелек Юмани для оплаты услуги.
Со стороны администратора, при добавлении бота в телеграм канал, необходимо заполнить для него данные, такие как: страна к которой относится канал, город и стоимость публикации рекламы


### ТЗ от заказчика
У заказщика были следующие требования:
1. Возможность добавления бота в качестве администратора в канал, с последующей автоматизацией публикации постов
2. Реализовать администратору возможность отправки поста сразу во все добавленные каналы
3. Возможность закрепления постов пользователем на определенное время
4. Подсчет стоимости выбранных пользователем опций и формирование ссылки на оплату
5. Вывод для каждого пользователя списка купленных постов


### Выбранные решения для реализации требований
Бот написан на асинхронном фреймворке aiogram, в качестве БД используется PostgreSQL с использованием асинхронного драйвера asyncpg. Запросы к БД написаны с помощью SQLAlchemy,
миграции и контроль версий БД выполнялся с помощью alembic. В качестве FSM хранилища используется NoSQL БД redis.


## Локальный запуск проекта
Выполните клонирование проекта и установите необходимые для работы зависимости:
```
git clone https://github.com/skojpish/workmarket.git
pip install -r requirements.txt
```
Создайте файл .env в родительском каталоге со следующим наполнением:
```
TOKEN="токен бота"
PAYMENT_TOKEN='токен юмани кошелька'

MASTER_ID="id администратора"

DB_NAME='имя основной БД PostgreSQL'
DB_USER='имя пользователя'
DB_PASS='пароль'
DB_HOST='хост'
DB_PORT='порт'

REDIS_HOST='хост redis'
REDIS_PORT=порт
REDIS_USER='имя пользователя (опционально)'
REDIS_PASS='пароль (опционально)'
```
Выполните миграции alembic моделей в вашей БД:
```
alembic revision --autogenerate -m ''
alembic upgrade head
```
Запустите бота:
```
python main.py
```