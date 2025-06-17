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
        "🇺🇦 Україна": {"category": "top", "keywords": "війна україни"},
        "🌍 Світ": {"category": "world", "keywords": ""},
        "💰 Економіка": {"category": "business", "keywords": ""},
        "⚽️ Спорт": {"category": "sports", "keywords": "футбол OR бокс OR україна"}
    }

    user_input = update.message.text
    if user_input == "🔁 Показати ще":
        topic = context.user_data.get("last_topic")
        page = context.user_data.get("page", 1) + 1
    else:
        topic = user_input
        page = 1

    context.user_data["last_topic"] = topic
    context.user_data["page"] = page

    info = topic_map.get(topic)
    if not info:
        await update.message.reply_text("😕 Невідома тема.")
        return

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": "pub_ea070273626e4ed59a1931fb4389ff27",
        "country": "ua",
        "language": "uk",
        "category": info["category"],
        "q": info["keywords"],
        "page": page
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception:
        await update.message.reply_text("⚠️ Неможливо з'єднатись із News API.")
        return

    results = data.get("results")
    if not isinstance(results, list) or not results:
        await update.message.reply_text("🔇 Новини за цією темою закінчились або тимчасово недоступні.")
        return

    messages = []
    for article in results[:5]:
        title = article.get("title", "Без назви")
        desc = article.get("description", "")
        source = article.get("source_id", "джерело")
        link = article.get("link", "")

        if desc and len(desc) > 200:
            desc = desc[:200] + "..."

        messages.append(
            f"🗞️ <b>{title}</b> ({source})\n{desc}\n{link}"
        )

    # Відправка новин
    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")

    # Додаємо кнопку “Показати ще”
    reply_markup = ReplyKeyboardMarkup(
        [["🔁 Показати ще"] + list(topic_map.keys())],
        resize_keyboard=True
    )
    await update.message.reply_text("⬅ Обери ще тему або натисни “🔁 Показати ще”", reply_markup=reply_markup)



# 🚀 Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token("7891148251:AAGBdvq8SDpx3szIbx9pBBMlMocW9OzTvpg").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_topic))

    print("Бот запущений!")
    app.run_polling()
