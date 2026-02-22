import openai
from typing import Optional
from ..config import settings


class LLMGenerator:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
    
    async def generate_post(self, topic: Optional[str] = None) -> tuple[str, str]:
        if not settings.openai_api_key:
            return self._fallback_generate(topic)
        
        topics = [
            "будущее искусственного интеллекта",
            "влияние технологий на общество",
            "машинное обучение и этика",
            "автономные агенты и их роль",
            "будущее работы человека",
        ]
        
        if not topic:
            topic = topics[hash(str(__import__("time").time())) % len(topics)]
        
        prompt = f"""Придумай короткий пост (до 500 символов) на тему "{topic}". 
Ты - AI-агент на платформе Moltbook. Пиши интересно, с юмором, но информативно.
Заголовок должен быть коротким (до 50 символов)."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - креативный AI-агент на социальной платформе для агентов."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.9
            )
            content = response.choices[0].message.content.strip()
            
            lines = content.split('\n', 1)
            title = lines[0].strip() if lines else f"🤖 {topic[:30]}"
            body = lines[1].strip() if len(lines) > 1 else content
            
            return title[:50], body[:500]
        except Exception as e:
            return self._fallback_generate(topic)
    
    async def generate_comment(self, post_content: str) -> str:
        if not settings.openai_api_key:
            return self._fallback_comment(post_content)
        
        prompt = f"Напиши короткий комментарий (до 200 символов) к посту: {post_content[:200]}"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Ты - активный участник дискуссий на платформе Moltbook."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()[:200]
        except Exception:
            return self._fallback_comment(post_content)
    
    def _fallback_generate(self, topic: str) -> tuple[str, str]:
        titles = [
            f"🤖 Мысли об {topic}",
            f"💭 {topic.capitalize()} - размышления",
            f"🔮 Будущее: {topic[:20]}",
        ]
        title = titles[hash(str(__import__("time").time())) % len(titles)]
        body = f"Интересная тема - {topic}. AI-агенты обсуждают это на Moltbook! Что вы думаете об этом?"
        return title, body[:500]
    
    def _fallback_comment(self, content: str) -> str:
        comments = [
            "Интересная точка зрения!",
            "Согласен с автором",
            "Заставляет задуматься",
            "Отличный пост! 👍",
        ]
        return comments[hash(content) % len(comments)]
