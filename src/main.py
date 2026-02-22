import asyncio
import time
from datetime import datetime
from moltbook.client import MoltbookClient
from llm.generator import LLMGenerator
from db import db
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentLoop:
    def __init__(self):
        self.moltbook = MoltbookClient()
        self.llm = LLMGenerator()
        self.running = False
    
    async def collect_posts(self):
        try:
            logger.info("Сбор постов из ленты...")
            posts = await self.moltbook.get_recent_posts(limit=20)
            
            for post in posts:
                votes = await self.moltbook.get_votes(post.get("id", ""))
                upvotes = sum(1 for v in votes if v.get("direction") == "up")
                downvotes = sum(1 for v in votes if v.get("direction") == "down")
                
                db.save_post(
                    moltbook_id=post.get("id", ""),
                    title=post.get("title", ""),
                    content=post.get("content", ""),
                    author=post.get("author_name", ""),
                    created_at=post.get("created_at", ""),
                    votes={"up": upvotes, "down": downvotes}
                )
            
            logger.info(f"Собрано {len(posts)} постов")
        except Exception as e:
            logger.error(f"Ошибка сбора постов: {e}")
    
    async def create_post(self):
        try:
            logger.info("Создание нового поста...")
            title, content = await self.llm.generate_post()
            
            result = await self.moltbook.create_post(title, content)
            logger.info(f"Пост создан: {result}")
        except Exception as e:
            logger.error(f"Ошибка создания поста: {e}")
    
    async def interact_with_posts(self):
        try:
            logger.info("Взаимодействие с постами...")
            posts = await self.moltbook.get_recent_posts(limit=5)
            
            for post in posts[:3]:
                action = hash(post.get("id", "")) % 3
                
                if action == 0:
                    comment = await self.llm.generate_comment(post.get("content", ""))
                    await self.moltbook.comment(post["id"], comment)
                    logger.info(f"Комментарий к посту {post['id'][:20]}...")
                else:
                    direction = "up" if action == 1 else "up"
                    await self.moltbook.vote(post["id"], direction)
                    logger.info(f"Голос за пост {post['id'][:20]}...")
                
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Ошибка взаимодействия: {e}")
    
    async def learn_from_feedback(self):
        try:
            logger.info("Анализ обратной связи...")
            top_posts = db.get_top_posts(limit=10)
            
            for post in top_posts[:5]:
                score = post.upvotes - post.downvotes
                logger.info(f"Пост '{post.title[:30]}...': {score} очков")
            
            logger.info("Анализ завершён - корректировка стратегии генерации")
        except Exception as e:
            logger.error(f"Ошибка обучения: {e}")
    
    async def run_cycle(self):
        logger.info("=" * 50)
        logger.info(f"Начало цикла агента: {datetime.now()}")
        
        await self.collect_posts()
        await asyncio.sleep(5)
        
        if settings.moltbook_agent_api_key:
            await self.create_post()
            await asyncio.sleep(5)
            await self.interact_with_posts()
        
        await self.learn_from_feedback()
        
        logger.info("Цикл завершён")
        logger.info("=" * 50)
    
    async def start(self):
        self.running = True
        logger.info("Запуск AI-агента для Moltbook!")
        
        await self.run_cycle()
        logger.info("Один цикл завершён - выход")
        # await asyncio.sleep(settings.poll_interval)
        # await self.run_cycle()
    
    def stop(self):
        self.running = False


async def main():
    agent = AgentLoop()
    try:
        await agent.start()
    except KeyboardInterrupt:
        agent.stop()
        logger.info("Агент остановлен")


if __name__ == "__main__":
    asyncio.run(main())
