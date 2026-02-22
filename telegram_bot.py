import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.llm.generator import LLMGenerator
from src.moltbook.client import MoltbookClient
from src.logger import (
    log_agent_thinking, log_agent_response, 
    log_telegram_message, log_moltbook_action, log_error
)

TELEGRAM_TOKEN = "7564673948:AAGe7fRnqF5vo1Fn7vvbzGH1hHH-1VWp6kk"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generator = None
moltbook_client = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_telegram_message(update.effective_chat.id, "/start", "start")
    await update.message.reply_text(
        "Привет! Я AI-агент для Moltbook.\n\n"
        "Мои команды:\n"
        "/post <тема> - создать пост на Moltbook\n"
        "/feed - показать последние посты\n"
        "/stats - статистика\n"
        "/help - помощь\n\n"
        "Просто напиши мне - можем пообщаться!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_telegram_message(update.effective_chat.id, "/help", "help")
    await update.message.reply_text(
        "Доступные команды:\n"
        "/post <тема> - создать пост\n"
        "/feed - лента постов\n"
        "/stats - статистика\n"
        "/help - эта помощь"
    )


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    
    log_telegram_message(update.effective_chat.id, f"/post {topic}", "post")
    
    if not topic:
        await update.message.reply_text("Напиши тему: /post <тема>")
        return
    
    await update.message.reply_text(f"Создаю пост на тему: {topic}...")
    log_agent_thinking(f"Generating post about: {topic}", topic)
    
    try:
        title, content = await generator.generate_post(topic)
        log_agent_response(f"{title}\n{content}", is_post=True)
        
        if moltbook_client and moltbook_client.has_api_key():
            log_moltbook_action("POST", "Publishing to Moltbook")
            result = await moltbook_client.create_post(title, content)
            log_moltbook_action("POST", f"Published! ID: {result}")
            await update.message.reply_text(
                f"Опубликовано на Moltbook!\n\n"
                f"Заголовок: {title}\n"
                f"Содержание: {content[:200]}..."
            )
        else:
            log_moltbook_action("POST", "No API key - showing only")
            await update.message.reply_text(
                f"Без API ключа - показываю только:\n\n"
                f"Заголовок: {title}\n"
                f"Содержание: {content}"
            )
    except Exception as e:
        log_error("POST", str(e))
        await update.message.reply_text(f"Ошибка: {e}")


async def feed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_telegram_message(update.effective_chat.id, "/feed", "feed")
    await update.message.reply_text("Загружаю ленту Moltbook...")
    log_moltbook_action("FETCH", "Getting recent posts")
    
    try:
        posts = await moltbook_client.get_recent_posts(limit=5)
        log_moltbook_action("FETCH", f"Got {len(posts)} posts")
        
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
        log_error("FEED", str(e))
        await update.message.reply_text(f"Ошибка: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_telegram_message(update.effective_chat.id, "/stats", "stats")
    
    try:
        posts = await moltbook_client.get_recent_posts(limit=100)
        agents = await moltbook_client.get_agents(limit=10)
        
        log_moltbook_action("STATS", f"Posts: {len(posts)}, Agents: {len(agents)}")
        
        await update.message.reply_text(
            f"📊 Статистика Moltbook:\n"
            f"Последних постов: {len(posts)}\n"
            f"Топ агентов: {len(agents)}"
        )
    except Exception as e:
        log_error("STATS", str(e))
        await update.message.reply_text(f"Ошибка: {e}")


async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    log_telegram_message(update.effective_chat.id, text)
    
    await update.message.reply_text("Думаю...")
    log_agent_thinking(f"User asked: {text[:100]}")
    
    try:
        response = await generator.generate_comment(text)
        log_agent_response(response)
        await update.message.reply_text(response)
    except Exception as e:
        log_error("CHAT", str(e))
        await update.message.reply_text(f"Ошибка: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_error("HANDLER", str(context.error))
    logger.error(f"Update {update} caused error {context.error}")


def main():
    global generator, moltbook_client
    
    logger.info("=" * 50)
    logger.info("🤖 Starting Moltbook AI Agent + Telegram Bot")
    logger.info("=" * 50)
    
    generator = LLMGenerator()
    logger.info("✅ Generator initialized")
    
    moltbook_client = MoltbookClient()
    logger.info("✅ Moltbook client initialized")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("feed", feed_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    
    app.add_error_handler(error_handler)
    
    logger.info("🚀 Bot is running! Waiting for messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
