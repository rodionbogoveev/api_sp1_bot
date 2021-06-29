import os
import time
import requests
import telegram
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log', 
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    filemode='a'
)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status != 'reviewing':
        if homework_status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        if homework_status == 'approved':
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    pass

def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload).json()
    timestamp['current'] = homework_statuses['current_date']
    return homework_statuses

def send_message(message):
    if message is not None:
        try:
            return bot.send_message(CHAT_ID, message)
        except Exception as error:
            logging.error(error, exc_info=True)
            return bot.send_message(chat_id=CHAT_ID, text=str(error))
    pass

timestamp = {
    'current': 0
}

def main():

    while True:
        try:
            logging.debug('Start')
            current_timestamp = timestamp['current']
            homeworks = get_homeworks(current_timestamp)
            if len(homeworks['homeworks']) != 0:
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
                logging.info('Message sent')
            pass
            time.sleep(5)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
