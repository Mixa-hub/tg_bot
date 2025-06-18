from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
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

last_keywords = {}  # Глобальний словник для збереження останнього запиту

def get_rss_news(keywords):
    import feedparser

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

            if any(kw.lower() in title.lower() for kw in keywords):
                results.append({
                    "title": title.strip(),
                    "summary": summary.strip()[:200] + "...",
                    "link": link,
                    "source": source.strip()
                })

    return results[:5]

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic_map = {
        "🇺🇦 Україна": ["війна", "київ", "дрон"],
        "🌍 Світ": ["g7", "ізраїль", "польща"],
        "💰 Економіка": ["економіка", "гривня", "ціна", "інфляція"],
        "⚽️ Спорт": ["футбол", "бокс", "олімпіада"],
        "🔁 Показати ще": None
    }

    user_input = update.message.text

    if user_input == "🔁 Показати ще":
        keywords = last_keywords.get(update.effective_chat.id, ["війна"])
    else:
        keywords = topic_map.get(user_input, ["війна"])
        last_keywords[update.effective_chat.id] = keywords

    news = get_rss_news(keywords)

    if not news:
        await update.message.reply_text("🔇 Жодної новини не знайдено. Спробуй пізніше або обери іншу тему.")
        return

    messages = []
    for item in news:
        messages.append(
            f"🗞️ <b>{item['title']}</b> ({item['source']})\n"
            f"{item['summary']}\n{item['link']}"
        )

    keyboard = [["🔁 Показати ще"], ["🇺🇦 Україна", "🌍 Світ"], ["💰 Економіка", "⚽️ Спорт"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("\n\n".join(messages), parse_mode="HTML", reply_markup=markup)

# 🆕 Хендлер команди /rss
async def rss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❓ Вкажи тему, наприклад: /rss футбол")
        return
    keywords = context.args
    last_keywords[update.effective_chat.id] = keywords
    news = get_rss_news(keywords)

    if not news:
        await update.message.reply_text("🔇 Новин за цією темою не знайдено.")
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
    app.add_handler(CommandHandler("rss", rss_command))


    print("Бот запущений!")
    app.run_polling()
