import os
import json

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Словарь для хранения профилей пользователей
user_data = {}
TOKEN = "8543955504:AAHIj2AuQYCOua8O9a1ZOv-yIb1ofLlElSE"

# Загружаем данные из файла user.json
def load_data():
    global user_data

    if os.path.exists("user.json"):
        with open("user.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)


# Сохраняем данные в файл user.json
def save_data():
    with open("user.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Если профиль уже существует
    if user_id in user_data:
        await update.message.reply_text(
            "Твой профиль уже сохранён!\n"
            "Используй /profile, чтобы посмотреть его."
        )
        return

    # Запоминаем, что следующим пользователь должен написать имя
    context.user_data["step"] = "name"

    await update.message.reply_text(
        "Привет! Давай создадим твой профиль.\n\n"
        "Напиши своё имя:"
    )


# Получаем имя и цвет пользователя
async def get_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text

    # Пользователь вводит имя
    if context.user_data.get("step") == "name":
        context.user_data["name"] = message
        context.user_data["step"] = "color"

        await update.message.reply_text(
            "Отлично!\n"
            "Теперь напиши свой любимый цвет:"
        )
        return

    # Пользователь вводит цвет
    if context.user_data.get("step") == "color":
        name = context.user_data["name"]
        color = message

        # Сохраняем имя и цвет пользователя
        user_data[user_id] = {
            "name": name,
            "color": color
        }

        # Записываем данные в JSON
        save_data()

        # Очищаем временные данные
        context.user_data.clear()

        await update.message.reply_text(
            "Профиль успешно сохранён! ✅\n\n"
            f"Имя: {name}\n"
            f"Любимый цвет: {color}\n\n"
            "Теперь можешь написать /profile"
        )


# Команда /profile
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Проверяем, есть ли профиль
    if user_id not in user_data:
        await update.message.reply_text(
            "У тебя ещё нет профиля.\n"
            "Напиши /start, чтобы создать его."
        )
        return

    profile_data = user_data[user_id]

    await update.message.reply_text(
        "👤 Твой профиль:\n\n"
        f"Имя: {profile_data['name']}\n"
        f"Любимый цвет: {profile_data['color']}"
    )


# Главная функция
def main():
    # Загружаем сохранённые профили при запуске
    load_data()

    # Вставь сюда токен своего бота


    # Создаём приложение
    application = Application.builder().token(TOKEN).build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Команда /profile
    application.add_handler(CommandHandler("profile", profile))

    # Обработка обычных сообщений
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_profile
        )
    )

    print("Бот запущен!")

    # Запускаем бота
    application.run_polling()


# Запускаем программу
if __name__ == "__main__":
    main()