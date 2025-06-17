from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from datetime import datetime

# 🔐 API ключ від NewsAPI
API_KEY = "94601de32797445c8e6b199554b68a81"
NEWS_URL = "https://newsapi.org/v2/everything"

# 📘 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🇺🇦 Україна", "🌍 Світ"],
        ["💰 Економіка", "⚽️ Спорт"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! Обери тему новин 👇", reply_markup=markup
    )

# 🆘 /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я можу шукати новини для тебе за темами.\n"
        "Натисни на одну з кнопок або введи тему вручну 📰"
    )

# 📰 Обробка вибраної теми
from datetime import datetime

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_map = {
        "🇺🇦 Україна": "україна",
        "🌍 Світ": "world",
        "💰 Економіка": "економіка",
        "⚽️ Спорт": "спорт"
    }

    user_input = update.message.text
    topic = topic_map.get(user_input, user_input)

    # Формат дати для "сьогодні"
    today = datetime.now().strftime("%Y-%m-%d")

    # Запит до NewsAPI
    params = {
        "q": topic,
        "language": "uk",
        "from": today,
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY
    }

    response = requests.get(NEWS_URL, params=params)
    data = response.json()

    if data.get("status") != "ok":
        await update.message.reply_text("⚠️ Помилка при отриманні новин.")
        return

    articles = data.get("articles", [])
    if not articles:
        await update.message.reply_text("😐 Свіжих новин не знайдено.")
        return

    messages = []
    for article in articles:
        title = article.get("title", "Без назви")
        description = article.get("description", "")
        source = article.get("source", {}).get("name", "")
        url = article.get("url", "")

        # Обрізаємо опис, якщо він довгий
        if description and len(description) > 200:
            description = description[:200] + "..."

        # Формат повідомлення
        messages.append(
            f"🟦 <b>{title}</b> ({source})\n"
            f"{description}\n"
            f"{url}"
        )

    # Відправка всіх новин
    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")



# 🚀 Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token("7891148251:AAGBdvq8SDpx3szIbx9pBBMlMocW9OzTvpg").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("Бот запущений!")
    app.run_polling()
