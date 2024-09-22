import logging
import os
from datetime import datetime, timedelta
from typing import List
import random

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db, engine
from backend.app.models.user_models import User

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")  # URL API для взаимодействия с FastAPI

# Интервал активности пользователей (в секундах) для определения онлайн пользователей
ACTIVITY_INTERVAL = 300  # 5 минут

# Значения для уникальных пользователей
MIN_COINS = 100
MIN_RATING = 50


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Добро пожаловать в TeleWebManager Production Bot.\n"
        "Используйте меню ниже для запуска WebApp."
    )
    await send_main_menu(update, context)


# Отправка основного меню
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Запустить WebApp", web_app=WebAppInfo(url="http://localhost/prod_web/"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


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
            cutoff = datetime.utcnow() - timedelta(seconds=ACTIVITY_INTERVAL)
            result = await db.execute(select(User).where(User.last_login >= cutoff))
            users = result.scalars().all()
            await query.edit_message_text(f"Пользователи онлайн: {len(users)}")

        elif data == 'unique_users':
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


# Создание тестовых пользователей
async def create_test_users(db: AsyncSession, count: int = 50):
    existing_users = await db.execute(select(User))
    existing_users = existing_users.scalars().all()
    if len(existing_users) >= count:
        logger.info("Тестовые пользователи уже созданы.")
        return

    for _ in range(count):
        nickname = f"user_{random.randint(1000, 9999)}"
        telegram_uid = str(random.randint(100000, 999999))
        coins = random.randint(0, 200)
        rating = random.randint(0, 100)
        last_login = datetime.utcnow() - timedelta(seconds=random.randint(0, ACTIVITY_INTERVAL))
        last_logout = last_login + timedelta(seconds=random.randint(1, 300))

        user = User(
            nickname=nickname,
            telegram_uid=telegram_uid,
            coins=coins,
            rating=rating,
            last_login=last_login,
            last_logout=last_logout
        )
        db.add(user)

    await db.commit()
    logger.info(f"Создано {count} тестовых пользователей.")


# Главная функция запуска бота
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавление зависимостей
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Передача зависимости базы данных через bot_data
    app.bot_data["db"] = get_db

    # Запуск задачи по созданию тестовых пользователей при старте бота
    async def on_startup():
        async with AsyncSession(engine) as db:
            await create_test_users(db, count=50)

    app.add_task(on_startup())

    await app.run_polling()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
