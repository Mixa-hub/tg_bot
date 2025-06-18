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
        "🇺🇦 Україна": "ukraine war",
        "🌍 Світ": "world news",
        "💰 Економіка": "economy",
        "⚽️ Спорт": "football OR boxing OR україна"
    }

    user_input = update.message.text
    if user_input == "🔁 Показати ще":
        query = context.user_data.get("last_query", "ukraine")
        page = context.user_data.get("page", 1) + 1
    else:
        query = topic_map.get(user_input, "ukraine")
        page = 1

    context.user_data["last_query"] = query
    context.user_data["page"] = page

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "uk",
        "country": "ua",
        "max": 5,
        "page": page,
        "token": "ed8046caba3e55eec04826c52b330a3a"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
    except Exception:
        await update.message.reply_text("⚠️ Помилка з'єднання з GNews API.")
        return

    if not articles:
        await update.message.reply_text(
            "🔇 Новини тимчасово недоступні або ще не зʼявились у стрічці. Спробуй пізніше або обери іншу тему."
        )
        return

    messages = []
    for article in articles:
        title = article.get("title", "Без назви")
        desc = article.get("description", "")
        source = article.get("source", {}).get("name", "")
        url = article.get("url", "")

        if desc and len(desc) > 200:
            desc = desc[:200] + "..."

        messages.append(f"🗞️ <b>{title}</b> ({source})\n{desc}\n{url}")

    reply_markup = ReplyKeyboardMarkup(
        [["🔁 Показати ще"] + list(topic_map.keys())],
        resize_keyboard=True
    )

    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")
    await update.message.reply_text("⬅ Обери ще тему або натисни “🔁 Показати ще”", reply_markup=reply_markup)


# 🚀 Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token("7891148251:AAGBdvq8SDpx3szIbx9pBBMlMocW9OzTvpg").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("Бот запущений!")
    app.run_polling()
