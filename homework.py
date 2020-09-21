import os
import requests
import telegram
import time
import logging
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BOT = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(level='ERROR')
logger = logging.getLogger()


def parse_homework_status(homework):
    try:
        homework_name = homework.get('homework_name')
        if homework_name is None:
            logger.error(f'homework_name is None')
    except Exception as e:
        logger.error(f'Пустое значение homework_name')
    try:
        status = homework.get('status')
        if status is None:
            logger.error(f'status is None')
        if status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    except Exception as e_s:
        logger.error(f'Пустое значение status')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = current_timestamp
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    try:
        homework_statuses = requests.get(url, headers=headers, params=params)
        return homework_statuses.json()
    except Exception as e:
        logger.error(f'Не получилось запросить данные с Практикума.'
                    f' Проверьте учетные даннные')


def send_message(message):
    try:
        return BOT.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logger.error(f'Ошибка при отправке сообщения ботом')


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
