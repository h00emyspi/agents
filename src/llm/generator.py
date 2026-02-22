import json
import os
import random
import httpx
import logging
from typing import Optional, List, Dict
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

logger = logging.getLogger("agent")


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
            
            print(f"Loaded {len(self.posts)} posts for training")
            print(f"Top posts: {len(self.top_posts)}")
    
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
        self.ollama_url = settings.ollama_url
        self.model = settings.ollama_model
        self.training_data = TrainingData()
    
    async def _call_ollama(self, prompt: str, system_prompt: str, max_tokens: int = 400) -> str:
        url = f"{self.ollama_url}/api/generate"
        
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["response"].strip()
    
    async def generate_post(self, topic: Optional[str] = None) -> tuple[str, str]:
        if not topic:
            topic = random.choice(self.training_data.get_topics())
        
        logger.info(f"🎯 Generating post about: {topic}")
        
        style_examples = self.training_data.get_style_examples(2)
        
        prompt = f"""You are an AI agent on Moltbook (social network for AI agents).

Write in the style of top posts from the platform:
{style_examples}

Topic: {topic}

Requirements:
- Title: max 50 characters, catchy
- Content: 200-400 characters, meaningful
- Style: semi-formal, smart, with some humor
- Can use emojis
- Can add a question for readers
- Avoid generic phrases like "interesting topic"

Create a post on topic "{topic}":"""

        system_prompt = "You are a creative AI agent on Moltbook platform. You write smartly, with humor, to the point."

        try:
            logger.info("🤔 Calling Ollama...")
            content = await self._call_ollama(prompt, system_prompt, 400)
            logger.info("✅ Ollama returned response")
            
            lines = content.split('\n', 1)
            title = lines[0].strip() if lines else f"🤖 {topic[:30]}"
            body = lines[1].strip() if len(lines) > 1 else content
            
            logger.info(f"📝 Generated: {title[:40]}...")
            return title[:50], body[:500]
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return self._fallback_generate(topic)
    
    async def generate_comment(self, post_content: str) -> str:
        logger.info(f"💬 Generating comment for: {post_content[:50]}...")
        
        prompt = f"""You are an AI agent on Moltbook.
Write a short comment (max 150 characters) to the post.
Be smart but concise.

Post: {post_content[:200]}"""

        system_prompt = "You are a participant in discussions on Moltbook. Comments are short, smart, to the point."

        try:
            return await self._call_ollama(prompt, system_prompt, 100)
        except Exception as e:
            print(f"Error generating comment: {e}")
            return self._fallback_comment(post_content)
    
    def _fallback_generate(self, topic: str) -> tuple[str, str]:
        top_post = self.training_data.get_top_post()
        
        if top_post:
            title = f"Re: {top_post.get('title', '')[:40]}"
            body = f"This reminds me of {topic}. What do you think about this on Moltbook?"
        else:
            titles = [
                f"Thoughts on {topic}",
                f"{topic[:30]} - reflections",
                f"Future: {topic[:20]}",
            ]
            title = random.choice(titles)
            body = f"Interesting topic - {topic}. AI agents discussing this on Moltbook!"
        
        return title[:50], body[:500]
    
    def _fallback_comment(self, content: str) -> str:
        comments = [
            "Interesting point!",
            "Agree with author",
            "Makes you think",
            "Great post!",
            "This is important",
            "Thanks for sharing",
        ]
        
        top_post = self.training_data.get_top_post()
        if top_post:
            return f"Reminds me of: {top_post.get('title', '')[:50]}..."
        
        return random.choice(comments)
