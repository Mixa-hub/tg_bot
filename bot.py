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
async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_map = {
        "🇺🇦 Україна": "top",
        "🌍 Світ": "world",
        "💰 Економіка": "business",
        "⚽️ Спорт": "sports"
    }

    user_input = update.message.text
    category = topic_map.get(user_input, "top")

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": "pub_ea070273626e4ed59a1931fb4389ff27",
        "country": "ua",
        "language": "uk",
        "category": category,
        "page": 1
    }

    response = requests.get(url, params=params)
    data = response.json()
    articles = data.get("results", [])

    if not articles:
        await update.message.reply_text(
            f"😶 Новин на тему <b>{category}</b> зараз не знайдено.\n"
            "Можливо, джерела ще не оновили стрічку або дані недоступні.",
            parse_mode="HTML"
        )
        return

    messages = []
    for article in articles[:5]:
        title = article.get("title", "Без назви")
        description = article.get("description", "")
        source = article.get("source_id", "")
        link = article.get("link", "")

        if description and len(description) > 200:
            description = description[:200] + "..."

        messages.append(
            f"🗞️ <b>{title}</b> ({source})\n{description}\n{link}"
        )

    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")


# 🚀 Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token("7891148251:AAGBdvq8SDpx3szIbx9pBBMlMocW9OzTvpg").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("Бот запущений!")
    app.run_polling()
