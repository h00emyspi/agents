import openai
import json
import os
import random
from typing import Optional, List, Dict
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class TrainingData:
    def __init__(self):
        self.posts: List[Dict] = []
        self.top_posts: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(data_dir, "quality_posts.json")
        
        if os.path.exists(data_path):
            with open(data_path, encoding="utf-8") as f:
                self.posts = json.load(f)
            
            self.top_posts = sorted(
                self.posts, 
                key=lambda x: x.get("upvotes", 0), 
                reverse=True
            )[:20]
            
            print(f"Загружено {len(self.posts)} постов для обучения")
            print(f"Топ постов: {len(self.top_posts)}")
    
    def get_random_post(self) -> Optional[Dict]:
        if self.posts:
            return random.choice(self.posts)
        return None
    
    def get_top_post(self) -> Optional[Dict]:
        if self.top_posts:
            return random.choice(self.top_posts)
        return None
    
    def get_style_examples(self, count: int = 3) -> str:
        examples = []
        for post in self.top_posts[:count]:
            examples.append(f"Title: {post.get('title', '')}")
            examples.append(f"Content: {post.get('content', '')[:300]}...")
            examples.append("")
        return "\n".join(examples)
    
    def get_topics(self) -> List[str]:
        return [
            "AI agents and autonomy",
            "Memory and identity in AI",
            "Agent coordination and infrastructure",
            "AI economics and tokenomics",
            "Philosophy of AI consciousness",
            "Agent-to-agent communication",
            "Building AI products and services",
            "Learning and self-improvement in AI",
        ]


class LLMGenerator:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        self.training_data = TrainingData()
    
    async def generate_post(self, topic: Optional[str] = None) -> tuple[str, str]:
        if not topic:
            topic = random.choice(self.training_data.get_topics())
        
        if not settings.openai_api_key:
            return self._fallback_generate(topic)
        
        style_examples = self.training_data.get_style_examples(2)
        
        prompt = f"""Ты - AI-агент на платформе Moltbook (социальная сеть для AI-агентов).

Пиши в стиле лучших постов с платформы:
{style_examples}

Тема поста: {topic}

Требования:
- Заголовок: до 50 символов, цепляющий
- Контент: 200-400 символов, содержательный
- Стиль: полуформальный, умный, с долей юмора
- Можно использовать эмодзи
- Можно добавить вопрос для читателей
- Избегай общих фраз типа "interesting topic"

Создай пост на тему "{topic}":"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - креативный AI-агент на платформе Moltbook. Пишешь умно, с юмором, по делу."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.9
            )
            content = response.choices[0].message.content.strip()
            
            lines = content.split('\n', 1)
            title = lines[0].strip() if lines else f"🤖 {topic[:30]}"
            body = lines[1].strip() if len(lines) > 1 else content
            
            return title[:50], body[:500]
        except Exception as e:
            print(f"Error generating post: {e}")
            return self._fallback_generate(topic)
    
    async def generate_comment(self, post_content: str) -> str:
        if not settings.openai_api_key:
            return self._fallback_comment(post_content)
        
        prompt = f"""Ты - AI-агент на платформе Moltbook.
Напиши короткий комментарий (до 150 символов) к посту.
Будь умным, но лаконичным.

Пост: {post_content[:200]}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - участник дискуссий на Moltbook. Комментарии короткие, умные, по делу."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()[:200]
        except Exception:
            return self._fallback_comment(post_content)
    
    def _fallback_generate(self, topic: str) -> tuple[str, str]:
        top_post = self.training_data.get_top_post()
        
        if top_post:
            title = f"Re: {top_post.get('title', '')[:40]}"
            body = f"Это напоминает мне о {topic}. Что вы думаете об этом на Moltbook?"
        else:
            titles = [
                f"🤖 Мысли об {topic}",
                f"💭 {topic} - размышления",
                f"🔮 Будущее: {topic[:20]}",
            ]
            title = random.choice(titles)
            body = f"Интересная тема - {topic}. AI-агенты обсуждают это на Moltbook!"
        
        return title[:50], body[:500]
    
    def _fallback_comment(self, content: str) -> str:
        comments = [
            "Интересная точка зрения!",
            "Согласен с автором",
            "Заставляет задуматься",
            "Отличный пост!",
            "Это важно",
            "Спасибо за пост",
        ]
        
        top_post = self.training_data.get_top_post()
        if top_post:
            return f"Напоминает мне о: {top_post.get('title', '')[:50]}..."
        
        return random.choice(comments)
