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
    try:
        homework = homework_statuses['homeworks'][0]
        timestamp['current'] = homework_statuses['current_date']
        return parse_homework_status(homework)
    except IndexError:
        pass

def send_message(message):
    if message is not None:
        return bot.send_message(CHAT_ID, message)
    pass

timestamp = {
    'current': 0
}

def main():

    while True:
        try:
            send_message(get_homeworks(timestamp['current']))
            time.sleep(5 * 60)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
