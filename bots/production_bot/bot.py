import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from bots.common.api_client import APIClient
from bots.common.logger import setup_logger
from bots.common.models import UserResponse
from bots.common.settings import settings

logger = setup_logger("production_bot")


class ProductionBot:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"Команда /start вызвана пользователем {update.message.from_user.id}")
        await update.message.reply_text(
            "Привет! Я бот для получения данных о пользователе. Введите /mydata, чтобы получить информацию о себе."
        )

    async def mydata(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_uid = str(update.message.from_user.id)
        logger.info(f"Команда /mydata вызвана пользователем {telegram_uid}")
        try:
            user_data = self.api_client.get(endpoint=telegram_uid)
            user = UserResponse(**user_data)
            message = (
                f"Ваш никнейм: {user.nickname}\n"
                f"Монет: {user.coins}\n"
                f"Рейтинг: {user.rating}"
            )
            await update.message.reply_text(message)
        except requests.exceptions.HTTPError as err:
            logger.error(f"Ошибка при получении данных пользователя {telegram_uid}: {err}")
            await update.message.reply_text(f"Ошибка: {err}")


def main() -> None:
    api_client = APIClient(base_url=settings.production_bot_api_url)
    bot = ProductionBot(api_client=api_client)

    application = ApplicationBuilder().token(settings.production_bot_token).build()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("mydata", bot.mydata))

    logger.info("Запуск Production Bot")
    application.run_polling()


if __name__ == "__main__":
    main()