from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# 🔐 Твій API-ключ від NewsAPI
API_KEY = "94601de32797445c8e6b199554b68a81"
NEWS_URL = "https://newsapi.org/v2/everything"

# 📘 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот, який шукає для тебе новини.\n"
        "Команди:\n"
        "/news — останні новини\n"
        "/help — допомога"
    )

# 🆘 /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Що я вмію:\n"
        "/start — почати\n"
        "/news — останні новини\n"
        "/help — допомога"
    )

# 📰 /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    params = {
        "q": "україна OR війна OR світ",
        "language": "uk",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY
    }

    response = requests.get(NEWS_URL, params=params)
    data = response.json()

    if data.get("status") != "ok":
        await update.message.reply_text("😕 Не вдалося отримати новини.")
        return

    articles = data.get("articles", [])
    if not articles:
        await update.message.reply_text("Новин не знайдено.")
        return

    messages = []
    for article in articles:
        title = article.get("title", "Без назви")
        url = article.get("url", "")
        messages.append(f"📰 <b>{title}</b>\n{url}")

    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML")

# 🚀 Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token("7891148251:AAGBdvq8SDpx3szIbx9pBBMlMocW9OzTvpg").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("news", news))

    print("Бот запущений!")
    app.run_polling()
