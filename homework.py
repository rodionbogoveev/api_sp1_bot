import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

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


class TGBotException(Exception):
    pass


def parse_homework_status(homework):
    if 'homework_name' and 'status' not in homework:
        raise TGBotException('The message does not contain required fields')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    if homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        url, headers=headers, params=payload).json()
    
    send_error_message(error)
    global timestamp
    timestamp = homework_statuses['current_date']
    return homework_statuses


def send_message(message):
    if message is not None:
        return bot.send_message(CHAT_ID, message)
        logging.info('Message sent')
    raise TGBotException('The message does not required')


def send_error_message(error):
    logging.error(error, exc_info=True)
    message = f'Bot has down by error - {error}'
    return bot.send_message(chat_id=CHAT_ID, text=message)


timestamp = 0


def main():

    while True:
        try:
            logging.debug('Start')
            print(timestamp)
            homeworks = get_homeworks(timestamp)
            if len(homeworks['homeworks']) != 0:
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
            pass
            time.sleep(5)

        except Exception as error:
            send_error_message(error)
            time.sleep(5)


if __name__ == '__main__':
    main()
