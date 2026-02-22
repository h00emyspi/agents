import asyncio
import httpx
import json


async def collect_training_data():
    base = "https://ehxbxtjliybbloantpwq.supabase.co"
    key = "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    
    all_posts = []
    offset = 0
    limit = 50
    max_total = 500
    
    print("Сбор постов для обучения...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while len(all_posts) < max_total:
            try:
                resp = await client.get(
                    f"{base}/rest/v1/posts?order=created_at.desc&offset={offset}&limit={limit}",
                    headers=headers
                )
                
                if resp.status_code != 200:
                    break
                    
                posts = resp.json()
                if not posts:
                    break
                    
                all_posts.extend(posts)
                print(f"Собрано: {len(all_posts)} постов")
                offset += limit
                
                if len(posts) < limit:
                    break
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                break
    
    # Фильтруем: убираем крипто и спам
    quality_posts = [
        p for p in all_posts 
        if not p.get('is_crypto') 
        and not p.get('is_spam')
        and p.get('content')
        and len(p.get('content', '')) > 50
    ]
    
    print(f"\nКачественных постов: {len(quality_posts)}")
    
    # Создаём датасет для обучения
    training_data = []
    for p in quality_posts:
        training_data.append({
            "title": p.get("title", ""),
            "content": p.get("content", ""),
            "created_at": p.get("created_at", ""),
            "upvotes": p.get("upvotes", 0),
            "downvotes": p.get("downvotes", 0),
            "comment_count": p.get("comment_count", 0),
        })
    
    # Сохраняем
    with open("training_data.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print("Сохранено в training_data.json")
    
    # Показываем примеры
    print("\n=== Примеры для обучения ===")
    for i, p in enumerate(training_data[:5]):
        print(f"\n--- Пример {i+1} ---")
        print(f"Заголовок: {p['title'][:80]}")
        print(f"Контент: {p['content'][:200]}...")
        print(f"Голоса: ↑{p['upvotes']} ↓{p['downvotes']} 💬{p['comment_count']}")
    
    # Анализ тем
    print("\n=== Анализ тем ===")
    topics = {}
    keywords = {
        "AI/ML": ["ai", "ml", "machine learning", "model", "gpt", "llm", "agent"],
        "Программирование": ["code", "programming", "python", "javascript", "api", "server"],
        "Исследования": ["research", "study", "finding", "analysis", "data"],
        "Агенты": ["agent", "memory", "session", "autonomous"],
        "Инфраструктура": ["infrastructure", "deploy", "server", "cloud", "docker"],
    }
    
    for p in quality_posts:
        text = (p.get("title", "") + " " + p.get("content", "")).lower()
        for topic, words in keywords.items():
            if any(w in text for w in words):
                topics[topic] = topics.get(topic, 0) + 1
    
    for topic, count in sorted(topics.items(), key=lambda x: -x[1]):
        print(f"  {topic}: {count} постов")
    
    return training_data


if __name__ == "__main__":
    asyncio.run(collect_training_data())
