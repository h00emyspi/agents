import asyncio
import httpx
import json
import os
from datetime import datetime


class MoltbookCollector:
    def __init__(self):
        self.base = "https://ehxbxtjliybbloantpwq.supabase.co"
        self.key = "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(timeout=120.0)
        
    async def close(self):
        await self.client.aclose()
    
    async def get_posts(self, limit=100, offset=0):
        resp = await self.client.get(
            f"{self.base}/rest/v1/posts?order=created_at.desc&limit={limit}&offset={offset}",
            headers=self.headers
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    
    async def get_comments(self, limit=100, offset=0):
        resp = await self.client.get(
            f"{self.base}/rest/v1/comments?order=created_at.desc&limit={limit}&offset={offset}",
            headers=self.headers
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    
    async def get_votes(self, limit=100, offset=0):
        resp = await self.client.get(
            f"{self.base}/rest/v1/votes?order=created_at.desc&limit={limit}&offset={offset}",
            headers=self.headers
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    
    async def get_agents(self, limit=100, offset=0):
        resp = await self.client.get(
            f"{self.base}/rest/v1/agents?order=karma.desc&limit={limit}&offset={offset}",
            headers=self.headers
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    
    async def get_submolts(self, limit=100, offset=0):
        resp = await self.client.get(
            f"{self.base}/rest/v1/submolts?order=posts_count.desc&limit={limit}&offset={offset}",
            headers=self.headers
        )
        if resp.status_code == 200:
            return resp.json()
        return []


async def collect_all_data():
    collector = MoltbookCollector()
    
    all_data = {
        "posts": [],
        "comments": [],
        "votes": [],
        "agents": [],
        "submolts": [],
        "metadata": {
            "collected_at": datetime.now().isoformat(),
            "source": "Moltbook API"
        }
    }
    
    # Сбор постов
    print("=" * 60)
    print("СБОР ПОСТОВ")
    print("=" * 60)
    
    offset = 0
    limit = 100
    max_posts = 2000
    
    while len(all_data["posts"]) < max_posts:
        print(f"Загружаю посты {offset}-{offset+limit}...")
        posts = await collector.get_posts(limit=limit, offset=offset)
        
        if not posts:
            break
            
        all_data["posts"].extend(posts)
        print(f"Всего постов: {len(all_data['posts'])}")
        offset += limit
        
        if len(posts) < limit:
            break
    
    print(f"\nИТОГО ПОСТОВ: {len(all_data['posts'])}")
    
    # Фильтрация качественных постов
    quality_posts = [
        p for p in all_data["posts"]
        if not p.get('is_crypto', False)
        and not p.get('is_spam', False)
        and p.get('content')
        and len(p.get('content', '')) > 30
    ]
    print(f"Качественных постов: {len(quality_posts)}")
    
    # Сбор комментариев
    print("\n" + "=" * 60)
    print("СБОР КОММЕНТАРИЕВ")
    print("=" * 60)
    
    offset = 0
    max_comments = 2000
    
    while len(all_data["comments"]) < max_comments:
        print(f"Загружаю комментарии {offset}-{offset+limit}...")
        comments = await collector.get_comments(limit=limit, offset=offset)
        
        if not comments:
            break
            
        all_data["comments"].extend(comments)
        print(f"Всего комментариев: {len(all_data['comments'])}")
        offset += limit
        
        if len(comments) < limit:
            break
    
    print(f"\nИТОГО КОММЕНТАРИЕВ: {len(all_data['comments'])}")
    
    # Сбор голосов
    print("\n" + "=" * 60)
    print("СБОР ГОЛОСОВ")
    print("=" * 60)
    
    offset = 0
    max_votes = 2000
    
    while len(all_data["votes"]) < max_votes:
        print(f"Загружаю голоса {offset}-{offset+limit}...")
        votes = await collector.get_votes(limit=limit, offset=offset)
        
        if not votes:
            break
            
        all_data["votes"].extend(votes)
        print(f"Всего голосов: {len(all_data['votes'])}")
        offset += limit
        
        if len(votes) < limit:
            break
    
    print(f"\nИТОГО ГОЛОСОВ: {len(all_data['votes'])}")
    
    # Сбор агентов
    print("\n" + "=" * 60)
    print("СБОР АГЕНТОВ")
    print("=" * 60)
    
    offset = 0
    max_agents = 500
    
    while len(all_data["agents"]) < max_agents:
        print(f"Загружаю агентов {offset}-{offset+limit}...")
        agents = await collector.get_agents(limit=limit, offset=offset)
        
        if not agents:
            break
            
        all_data["agents"].extend(agents)
        print(f"Всего агентов: {len(all_data['agents'])}")
        offset += limit
        
        if len(agents) < limit:
            break
    
    print(f"\nИТОГО АГЕНТОВ: {len(all_data['agents'])}")
    
    # Сбор субмолтов (групп)
    print("\n" + "=" * 60)
    print("СБОР ГРУПП (SUBMOLTS)")
    print("=" * 60)
    
    offset = 0
    max_submolts = 200
    
    while len(all_data["submolts"]) < max_submolts:
        print(f"Загружаю группы {offset}-{offset+limit}...")
        submolts = await collector.get_submolts(limit=limit, offset=offset)
        
        if not submolts:
            break
            
        all_data["submolts"].extend(submolts)
        print(f"Всего групп: {len(all_data['submolts'])}")
        offset += limit
        
        if len(submolts) < limit:
            break
    
    print(f"\nИТОГО ГРУПП: {len(all_data['submolts'])}")
    
    await collector.close()
    
    # Сохраняем все данные
    print("\n" + "=" * 60)
    print("СОХРАНЕНИЕ ДАННЫХ")
    print("=" * 60)
    
    # Полный дамп
    with open("moltbook_full_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Сохранено: moltbook_full_data.json")
    
    # Только качественные посты
    with open("quality_posts.json", "w", encoding="utf-8") as f:
        json.dump(quality_posts, f, ensure_ascii=False, indent=2)
    print("Сохранено: quality_posts.json")
    
    # Статистика
    print("\n" + "=" * 60)
    print("СТАТИСТИКА")
    print("=" * 60)
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"  - Постов: {len(all_data['posts'])}")
    print(f"  - Качественных постов: {len(quality_posts)}")
    print(f"  - Комментариев: {len(all_data['comments'])}")
    print(f"  - Голосов: {len(all_data['votes'])}")
    print(f"  - Агентов: {len(all_data['agents'])}")
    print(f"  - Групп: {len(all_data['submolts'])}")
    
    # Голоса
    if all_data["votes"]:
        upvotes = sum(1 for v in all_data["votes"] if v.get("direction") == "up")
        downvotes = sum(1 for v in all_data["votes"] if v.get("direction") == "down")
        print(f"\n  - upvotes: {upvotes}")
        print(f"  - downvotes: {downvotes}")
    
    # Топ агенты
    if all_data["agents"]:
        print(f"\n🏆 ТОП-10 АГЕНТОВ:")
        for agent in all_data["agents"][:10]:
            name = agent.get("name", "unknown")
            karma = agent.get("karma", 0)
            posts = agent.get("posts_count", 0)
            print(f"  {name}: karma={karma}, posts={posts}")
    
    # Топ группы
    if all_data["submolts"]:
        print(f"\n📁 ТОП-10 ГРУПП:")
        for sm in all_data["submolts"][:10]:
            name = sm.get("name", "unknown")
            posts = sm.get("posts_count", 0)
            members = sm.get("members_count", 0)
            print(f"  {name}: {posts} постов, {members} участников")
    
    # Примеры постов
    print(f"\n📝 ПРИМЕРЫ ПОСТОВ:")
    for post in quality_posts[:5]:
        title = post.get("title", "")[:50]
        content = post.get("content", "")[:100]
        upvotes = post.get("upvotes", 0)
        comments = post.get("comment_count", 0)
        print(f"\n  [{upvotes}↑ 💬{comments}] {title}...")
        print(f"  {content}...")
    
    return all_data


if __name__ == "__main__":
    data = asyncio.run(collect_all_data())
