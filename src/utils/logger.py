from environs import Env
from logtail import LogtailHandler
from loguru import logger
from notifiers.logging import NotificationHandler


def load_loguru():
    env: Env = Env()
    env.read_env('.env')
    LOGTAIL_SOURCE_TOKEN = env('LOGTAIL_INSIGTER_SOURCE')

    ALERT_BOT_TOKEN = env('LOGER_BOT_TOKEN')
    TELEGRAM_NOTIFIERS_CHAT_IDS = [int(chat_id) for chat_id in env('TELEGRAM_CHAT_IDS').split(',')]

    for chat_id in TELEGRAM_NOTIFIERS_CHAT_IDS:
        params = {
            "token": ALERT_BOT_TOKEN,
            "chat_id": chat_id,

        }

        logger.add(NotificationHandler("telegram", defaults=params), level="ERROR")

    logtail_handler = LogtailHandler(source_token=LOGTAIL_SOURCE_TOKEN)
    logger.add(
        logtail_handler,
        format="{message}",
        level="INFO",
        backtrace=False,
        diagnose=False,
    )

    return logger


insighter_logger = load_loguru()

if __name__ == '__main__':

    def divide(a, b):
        insighter_logger.info('Старт функции', divide.__name__)
        return a / b


    def main():
        insighter_logger.info('Старт функции', main.__name__)
        try:
            divide(1, 0)
        except ZeroDivisionError:
            insighter_logger.exception("Деление на ноль")
