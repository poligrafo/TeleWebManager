import logging
import os
from typing import Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # URL API для взаимодействия с FastAPI


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это Admin/QA бот TeleWebManager.\n"
        "Используйте команды для управления пользователями и получения статистики."
    )


# Команда /get_uid <nickname>
async def get_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Пожалуйста, укажите никнейм пользователя.\nПример: /get_uid user123")
        return

    nickname = args[0]
    async with context.bot_data.get("db")() as db:
        result = await db.execute(select(User).where(User.nickname == nickname))
        user = result.scalars().first()
        if user:
            await update.message.reply_text(f"UID пользователя {nickname}: {user.id}")
        else:
            await update.message.reply_text("Пользователь не найден.")


# Команда /change_data <nickname> <field> <value>
async def change_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Использование: /change_data <nickname> <field> <value>\n"
                                        "Пример: /change_data user123 coins 200")
        return

    nickname, field, value = args
    if field not in {"coins", "rating"}:
        await update.message.reply_text("Неверное поле. Доступные поля: coins, rating")
        return

    try:
        value = int(value)
        if value < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Значение должно быть положительным целым числом.")
        return

    async with context.bot_data.get("db")() as db:
        result = await db.execute(select(User).where(User.nickname == nickname))
        user = result.scalars().first()
        if user:
            setattr(user, field, value)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            await update.message.reply_text(f"Данные пользователя {nickname} обновлены.")
        else:
            await update.message.reply_text("Пользователь не найден.")


# Команда /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Количество пользователей", callback_data='total_users')],
        [InlineKeyboardButton("Пользователи онлайн", callback_data='online_users')],
        [InlineKeyboardButton("Уникальные пользователи", callback_data='unique_users')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите статистику:', reply_markup=reply_markup)


# Обработка нажатий на кнопки статистики
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    async with context.bot_data.get("db")() as db:
        if data == 'total_users':
            result = await db.execute(select(User))
            users = result.scalars().all()
            await query.edit_message_text(f"Количество пользователей: {len(users)}")

        elif data == 'online_users':
            ACTIVITY_INTERVAL = 300  # 5 минут
            cutoff = datetime.utcnow() - timedelta(seconds=ACTIVITY_INTERVAL)
            result = await db.execute(select(User).where(User.last_login >= cutoff))
            users = result.scalars().all()
            await query.edit_message_text(f"Пользователи онлайн: {len(users)}")

        elif data == 'unique_users':
            MIN_COINS = 100
            MIN_RATING = 50
            result = await db.execute(
                select(User).where(
                    User.coins > MIN_COINS,
                    User.rating > MIN_RATING
                )
            )
            users = result.scalars().all()
            await query.edit_message_text(f"Уникальные пользователи: {len(users)}")
        else:
            await query.edit_message_text("Неизвестная команда.")


# Команда /qa_check
async def qa_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика проверки QA билда
    await update.message.reply_text("QA билд проверен успешно!")


# Главная функция запуска бота
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавление обработчиков команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get_uid", get_uid))
    app.add_handler(CommandHandler("change_data", change_data))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("qa_check", qa_check))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Передача зависимости базы данных через bot_data
    app.bot_data["db"] = get_db

    await app.run_polling()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
