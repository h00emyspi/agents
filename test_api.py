import asyncio
import httpx


async def test_moltbook():
    base = "https://ehxbxtjliybbloantpwq.supabase.co"
    key = "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        # Get posts
        resp = await client.get(f"{base}/rest/v1/posts?order=created_at.desc&limit=10", headers=headers)
        print(f"Posts status: {resp.status_code}")
        posts = resp.json()
        print(f"Found {len(posts)} posts\n")
        
        for post in posts[:5]:
            print(f"=== Post ===")
            print(f"Title: {post.get('title', '')[:60]}")
            print(f"Author: {post.get('author_name', 'unknown')}")
            print(f"Content: {post.get('content', '')[:100]}...")
            print(f"Created: {post.get('created_at', '')}")
            print(f"ID: {post.get('id', '')}")
            print()
        
        # Get agents
        resp = await client.get(f"{base}/rest/v1/agents?select=name,karma,posts_count&order=karma.desc&limit=10", headers=headers)
        print(f"Agents status: {resp.status_code}")
        agents = resp.json()
        print(f"\nTop agents:")
        for agent in agents[:5]:
            print(f"  {agent.get('name', 'unknown')}: karma={agent.get('karma', 0)}, posts={agent.get('posts_count', 0)}")


if __name__ == "__main__":
    asyncio.run(test_moltbook())
