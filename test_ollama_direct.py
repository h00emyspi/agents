import asyncio
import httpx
import json

async def test():
    url = "http://localhost:11434/api/generate"
    model = "gpt-oss:120b-cloud"
    
    prompt = """You are a creative AI agent on Moltbook platform.
Write a short post (max 200 chars) about AI agents.
Title and content.
Be smart and funny."""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(url, json=payload)
        data = resp.json()
        
        result = data.get("response", "")
        
        with open("ollama_final_test.txt", "w", encoding="utf-8") as f:
            f.write(f"Result:\n{result}")
        
        print(f"OK! See ollama_final_test.txt")

asyncio.run(test())
