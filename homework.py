import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

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
    name = homework['homework_name']
    status = homework['status']
    verdict_template = 'У вас проверили работу "{}"!\n\n{}'
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
        return verdict_template.format(name, verdict)
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return verdict_template.format(name, verdict)
    elif status == 'reviewing':
        return 'Работа на проверке.'
    else:
        raise TGBotException('Unknown homework status')


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        response = requests.get(URL, headers=headers, params=payload)
    except requests.exceptions.RequestException as error:
        raise TGBotException(f'{error}')
    if response.status_code != HTTPStatus.OK:
        raise TGBotException(f'Response status code is {response.status_code}')
    return response.json()


def send_message(message):
    if message is not None:
        bot.send_message(CHAT_ID, message)
        logging.info('Message sent')
    else:
        raise TGBotException('The message does not required')


def send_error_message(error):
    logging.error(error, exc_info=True)
    message = f'Bot has down by error - "{error}"'
    bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    print('Бот начал работу')
    while True:
        try:
            logging.debug('Start')
            homeworks = get_homeworks(current_timestamp)
            if len(homeworks['homeworks']) != 0:
                homework = homeworks['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
            current_timestamp = int(time.time())
            time.sleep(5 * 60)
        except Exception as error:
            send_error_message(error)
            time.sleep(5 * 60)


if __name__ == '__main__':
    main()
