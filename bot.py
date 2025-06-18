from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from datetime import datetime
import feedparser


# # 🔐 API ключ від NewsAPI
# API_KEY = "94601de32797445c8e6b199554b68a81"
# NEWS_URL = "https://newsapi.org/v2/everything"

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

def get_rss_news(keywords):
    feeds = [
        "https://www.pravda.com.ua/rss/",
        "https://kyivindependent.com/news-archive/feed",
        "https://euromaidanpress.com/feed"
    ]

    results = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            source = feed.feed.get("title", "джерело")

            text = f"{title} {summary}".lower()
            # if any(word in text for word in keywords):
            # ТИМЧАСОВО — показати все
            if True:
                results.append({
                    "title": title.strip(),
                    "summary": summary.strip()[:200] + "...",
                    "link": link,
                    "source": source.strip()
                })
    print(f"🧪 Парсинг завершено. Знайдено {len(results)} новин:")
    for r in results:
        print(f"  - {r['title']}")

    return results[:5]


# 📰 Обробка вибраної теми
async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = ["футбол", "бокс", "війна"]
    news = get_rss_news(keywords)

    if not news:
        await update.message.reply_text("🔇 Новини за ключовими словами не знайдено. Спробуй пізніше.")
        return

    messages = []
    for item in news:
        messages.append(
            f"🗞️ <b>{item['title']}</b> ({item['source']})\n"
            f"{item['summary']}\n{item['link']}"
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
