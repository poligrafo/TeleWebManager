import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from bots.common.api_client import APIClient
from bots.common.models import UserResponse, UserUpdateRequest
from bots.common.logger import setup_logger
from bots.common.settings import settings

logger = setup_logger("admin_bot")


class AdminBot:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def userinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            nickname = context.args[0]
            logger.info(f"Команда /userinfo вызвана для пользователя {nickname}")
            user_data = self.api_client.get(endpoint=f"?nickname={nickname}")
            user = UserResponse(**user_data)
            message = (
                f"Никнейм: {user.nickname}\n"
                f"Монет: {user.coins}\n"
                f"Рейтинг: {user.rating}"
            )
            await update.message.reply_text(message)
        except IndexError:
            logger.warning("Ошибка: Никнейм не был указан")
            await update.message.reply_text("Пожалуйста, укажите никнейм.")
        except requests.exceptions.HTTPError as err:
            logger.error(f"Ошибка при получении данных пользователя {nickname}: {err}")
            await update.message.reply_text(f"Ошибка: {err}")

    async def updateuser(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            nickname = context.args[0]
            coins = int(context.args[1])
            rating = int(context.args[2])
            logger.info(f"Команда /updateuser вызвана для пользователя {nickname} с новыми значениями монет: {coins}, рейтинг: {rating}")
            user_data = self.api_client.get(endpoint=f"?nickname={nickname}")
            user = UserResponse(**user_data)
            self.api_client.put(endpoint=f"{user.id}", data=UserUpdateRequest(coins=coins, rating=rating).dict())
            await update.message.reply_text(f"Данные пользователя {nickname} обновлены.")
        except (IndexError, ValueError):
            logger.warning("Ошибка в формате команды /updateuser")
            await update.message.reply_text("Неверный формат команды. Используйте: /updateuser <nickname> <coins> <rating>.")
        except requests.exceptions.HTTPError as err:
            logger.error(f"Ошибка при обновлении данных пользователя {nickname}: {err}")
            await update.message.reply_text(f"Ошибка: {err}")


def main() -> None:
    api_client = APIClient(base_url=settings.admin_bot_api_url)
    bot = AdminBot(api_client=api_client)

    application = ApplicationBuilder().token(settings.admin_bot_token).build()

    application.add_handler(CommandHandler("userinfo", bot.userinfo))
    application.add_handler(CommandHandler("updateuser", bot.updateuser))

    logger.info("Запуск Admin Bot")
    application.run_polling()


if __name__ == "__main__":
    main()