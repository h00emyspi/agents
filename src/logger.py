import logging
import sys
from datetime import datetime

# Logger for AI Agent thoughts
agent_logger = logging.getLogger("agent")
agent_logger.setLevel(logging.INFO)

# Logger for Telegram Bot
bot_logger = logging.getLogger("bot")
bot_logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(formatter)

agent_logger.addHandler(console_handler)
bot_logger.addHandler(console_handler)


def log_agent_thinking(prompt: str, topic: str = None):
    """Log what the agent is thinking about"""
    agent_logger.info(f"[THINKING] Topic: {topic or 'general'}")
    agent_logger.info(f"[PROMPT] {prompt[:100]}...")


def log_agent_response(response: str, is_post: bool = False):
    """Log agent's response"""
    prefix = "[POST]" if is_post else "[REPLY]"
    agent_logger.info(f"{prefix} Generated:")
    for line in response.split('\n')[:3]:
        agent_logger.info(f"  {line[:80]}")


def log_telegram_message(chat_id: int, text: str, command: str = None):
    """Log incoming Telegram message"""
    bot_logger.info(f"[TG] Chat: {chat_id}")
    if command:
        bot_logger.info(f"[TG] Command: {command}")
    bot_logger.info(f"[TG] Text: {text[:50]}...")


def log_moltbook_action(action: str, details: str):
    """Log Moltbook API actions"""
    agent_logger.info(f"[MOLTBOOK] {action}: {details}")


def log_error(source: str, error: str):
    """Log errors"""
    agent_logger.error(f"[ERROR] {source}: {error}")
