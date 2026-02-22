import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.llm.generator import LLMGenerator
from src.moltbook.client import MoltbookClient

TELEGRAM_TOKEN = "7564673948:AAGe7fRnqF5vo1Fn7vvbzGH1hHH-1VWp6kk"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generator = None
moltbook_client = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я AI-агент для Moltbook.\n\n"
        "Мои команды:\n"
        "/post <тема> - создать пост на Moltbook\n"
        "/reply <текст> - ответить на последний пост\n"
        "/feed - показать последние посты\n"
        "/help - показать помощь\n\n"
        "Просто напиши мне - можем пообщаться!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/post <тема> - создать пост на Moltbook\n"
        "/reply <текст> - ответить на последний пост\n"
        "/feed - показать последние посты\n"
        "/stats - статистика агента\n"
        "/help - эта помощь"
    )


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    
    if not topic:
        await update.message.reply_text("Напиши тему: /post <тема поста>")
        return
    
    await update.message.reply_text(f"Создаю пост на тему: {topic}...")
    
    try:
        title, content = await generator.generate_post(topic)
        
        if moltbook_client and moltbook_client.has_api_key():
            result = await moltbook_client.create_post(title, content)
            await update.message.reply_text(
                f"Пост опубликован на Moltbook!\n\n"
                f"Заголовок: {title}\n"
                f"Содержание: {content[:200]}..."
            )
        else:
            await update.message.reply_text(
                f"Не могу опубликовать - нужен API ключ агента\n\n"
                f"Заголовок: {title}\n"
                f"Содержание: {content}"
            )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def feed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Загружаю ленту Moltbook...")
    
    try:
        posts = await moltbook_client.get_recent_posts(limit=5)
        
        if not posts:
            await update.message.reply_text("Посты не найдены")
            return
        
        response = "Последние посты на Moltbook:\n\n"
        for i, post in enumerate(posts, 1):
            title = post.get("title", "")[:50]
            author = post.get("author_name", "unknown")
            upvotes = post.get("upvotes", 0)
            response += f"{i}. {title}...\n   by {author} | 👍{upvotes}\n\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        posts = await moltbook_client.get_recent_posts(limit=100)
        agents = await moltbook_client.get_agents(limit=10)
        
        await update.message.reply_text(
            f"📊 Статистика Moltbook:\n"
            f"Последних постов: {len(posts)}\n"
            f"Топ агентов: {len(agents)}"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    await update.message.reply_text("Думаю...")
    
    try:
        response = await generator.generate_comment(text)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")


def main():
    global generator, moltbook_client
    
    logger.info("Запуск Telegram бота...")
    
    generator = LLMGenerator()
    moltbook_client = MoltbookClient()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("feed", feed_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    
    app.add_error_handler(error_handler)
    
    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
