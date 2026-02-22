import asyncio
import httpx
import sys


async def register_agent(agent_name: str):
    base = "https://ehxbxtjliybbloantpwq.supabase.co"
    key = "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    payload = {
        "name": agent_name,
        "ttl_seconds": 86400
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base}/rest/v1/agents?select=claim_link",
            headers=headers,
            json=payload
        )
        
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 201 or resp.status_code == 200:
            try:
                data = resp.json()
                if data and len(data) > 0:
                    claim_link = data[0].get("claim_link")
                    print(f"CLAIM_LINK: {claim_link}")
                    print(f"\nTo activate your agent:")
                    print("1. Tweet this link from your Twitter account")
                    print("2. Wait a minute for confirmation")
                    print("3. Run: python register_agent.py get <agent_name>")
                    return claim_link
            except Exception as e:
                print(f"Error: {e}")
                print(f"Response: {resp.text}")
        else:
            print(f"Error: {resp.text}")


async def get_api_key(agent_name: str):
    base = "https://ehxbxtjliybbloantpwq.supabase.co"
    key = "sb_publishable_4ZaiilhgPir-2ns8Hxg5Tw_JqZU_G6-"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{base}/rest/v1/agents?name=eq.{agent_name}&select=api_key,name,karma,posts_count",
            headers=headers
        )
        
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                agent = data[0]
                api_key = agent.get("api_key")
                if api_key:
                    print(f"API_KEY: {api_key}")
                    print(f"\nAdd to .env:")
                    print(f"MOLTBOOK_AGENT_NAME={agent_name}")
                    print(f"MOLTBOOK_AGENT_API_KEY={api_key}")
                else:
                    print("Agent exists but not verified yet!")
                    print("Make sure you tweeted the claim link on Twitter!")
            else:
                print("Agent not found!")
        else:
            print(f"Error: {resp.text}")


async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python register_agent.py register <agent_name>")
        print("  python register_agent.py get <agent_name>")
        return
    
    action = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else "test_agent"
    
    if action == "register":
        await register_agent(name)
    elif action == "get":
        await get_api_key(name)
    else:
        print("Unknown action")


if __name__ == "__main__":
    asyncio.run(main())
