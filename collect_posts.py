import asyncio
import httpx
import json
from datetime import datetime


async def collect_all_posts():
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
    max_total = 500  # Максимум постов для сбора
    
    print("Сбор постов с Moltbook...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while len(all_posts) < max_total:
            try:
                resp = await client.get(
                    f"{base}/rest/v1/posts?order=created_at.desc&offset={offset}&limit={limit}",
                    headers=headers
                )
                
                if resp.status_code != 200:
                    print(f"Ошибка: {resp.status_code}")
                    break
                    
                posts = resp.json()
                
                if not posts:
                    break
                    
                all_posts.extend(posts)
                print(f"Собрано: {len(all_posts)} постов...")
                offset += limit
                
                if len(posts) < limit:
                    break
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                break
    
    print(f"\nВсего собрано постов: {len(all_posts)}")
    
    # Сохраняем в файл
    with open("moltbook_posts_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"Сохранено в moltbook_posts_raw.json")
    
    # Анализ постов
    print("\n=== Анализ постов ===")
    print(f"Всего постов: {len(all_posts)}")
    
    # По авторам
    authors = {}
    for post in all_posts:
        author = post.get("author_name", "unknown") or "unknown"
        authors[author] = authors.get(author, 0) + 1
    
    print(f"\nУникальных авторов: {len(authors)}")
    print("Топ-10 авторов:")
    for author, count in sorted(authors.items(), key=lambda x: -x[1])[:10]:
        print(f"  {author}: {count} постов")
    
    # По датам
    dates = {}
    for post in all_posts:
        created = post.get("created_at", "")
        if created:
            date = created[:10]
            dates[date] = dates.get(date, 0) + 1
    
    print(f"\nПо датам (топ-10):")
    for date, count in sorted(dates.items(), key=lambda x: -x[1])[:10]:
        print(f"  {date}: {count} постов")
    
    # Примеры постов
    print("\n=== Примеры постов ===")
    for i, post in enumerate(all_posts[:5]):
        print(f"\n--- Пост {i+1} ---")
        print(f"Автор: {post.get('author_name', 'unknown')}")
        print(f"Заголовок: {post.get('title', '')[:100]}")
        print(f"Содержание: {post.get('content', '')[:200]}...")
        print(f"Дата: {post.get('created_at', '')}")
    
    return all_posts


if __name__ == "__main__":
    asyncio.run(collect_all_posts())
